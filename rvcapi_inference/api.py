from fastapi import FastAPI, WebSocket, UploadFile, File
from tempfile import NamedTemporaryFile
from vc_infer_pipeline import VC
import torch
from infer_pack.models import SynthesizerTrnMs256NSFsid, SynthesizerTrnMs256NSFsid_nono
from fairseq import checkpoint_utils
import traceback
import uvicorn
import argparse
import soundfile
import os
from starlette.responses import FileResponse
import time
import faiss
import numpy as np
from subprocess import Popen

current_dir = os.getcwd()
number_of_cpu = os.cpu_count()
noparallel = False

G_pth = "pretrained/G48k.pth"
D_pth = "pretrained/D48k.pth"

def load_model(model_path, device, is_half):
    model = torch.load(model_path, map_location=device)
    tgt_sr = model["config"][-1]
    model["config"][-3]=model["weight"]["emb_g.weight"].shape[0]
    if_f0=model.get("f0",1)
    if(if_f0==1):
        net_g = SynthesizerTrnMs256NSFsid(*model["config"], is_half=is_half)
    else:
        net_g = SynthesizerTrnMs256NSFsid_nono(*model["config"])
    del net_g.enc_q

    net_g.load_state_dict(model["weight"], strict=False)
    net_g.to(device)

    if is_half:net_g = net_g.half()
    else: net_g = net_g.float()

    net_g.eval()

    vc = VC(tgt_sr, device, is_half)
    return model, vc, net_g, tgt_sr

def load_hubert(device, is_half):

    models, _, _ = checkpoint_utils.load_model_ensemble_and_task(["hubert_base.pt"],suffix="",)
    hubert_model = models[0]
    feats = torch.rand(512)

    hubert_model = hubert_model.to(device)

    if is_half: 
        hubert_model = hubert_model.half()
        feats = feats.half()
    else: 
        hubert_model = hubert_model.float()
        feats = feats.float()
    
    # warm up model for first inference time

    feats = feats.view(1, -1)
    padding_mask = torch.BoolTensor(feats.shape).to(device).fill_(False)

    inputs = {
        "source": feats.to(device),
        "padding_mask": padding_mask,
        "output_layer": 9,  # layer 9
    }
    
    hubert_model.eval()
    logits = hubert_model.extract_features(**inputs)

    return hubert_model

def delete_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except OSError:
        traceback.print_exc()
from scipy.signal import resample

def generate_app(hubert_model) -> FastAPI:
    app = FastAPI(
        title="Voice Changer",
        description="Voice Changer",
    )
    app.state.models = {}
    @app.post("/train")
    
    async def train(path_dataset: str, character_id: str, batch_size: int, epochs: int, save_frequency: int):
        ### STAGE 1:
        os.makedirs("%s/logs/%s" %(current_dir, character_id), exist_ok=True)
        open("%s/logs/%s/preprocess.log"%(current_dir, character_id), "w").close()
        cmd = "python3 trainset_preprocess_pipeline_print.py %s %s %s %s/logs/%s " \
            %(path_dataset, 48000 ,number_of_cpu, current_dir, character_id) + str(noparallel)
        p = Popen(cmd, shell=True)
        p.wait()
        print("STAGE1 DONEEEE")
        ### STAGE2
        open("%s/logs/%s/extract_f0_feature.log" % (current_dir, character_id), "w")
        cmd= "python3 extract_feature_print.py cuda:0 1 0 %s/logs/%s" %(current_dir, character_id)
        p = Popen(cmd, shell=True, cwd=current_dir)#, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=now_dir
        p.wait()
        print("STAGE2 DONEEEE")
        ### STAGE3
        exp_dir = "%s/logs/%s"%(current_dir, character_id)
        gt_wavs_dir = "%s/0_gt_wavs"%(exp_dir)
        co256_dir = "%s/3_feature256"%(exp_dir)
        names = set([name.split(".")[0] for name in os.listdir(gt_wavs_dir)]) & set(
                    [name.split(".")[0] for name in os.listdir(co256_dir)]
                )
        opt=[]
        for name in names:
            opt.append(
                    "%s/%s.wav|%s/%s.npy|%s"
                    % (
                        gt_wavs_dir.replace("\\", "\\\\"),
                        name,
                        co256_dir.replace("\\", "\\\\"),
                        name,
                        0,
                    )
                )
        
            opt.append(
                "%s/logs/mute/0_gt_wavs/mute%s.wav|%s/logs/mute/3_feature256/mute.npy|%s"
                % (current_dir, "48k", current_dir, 0)
            )
            with open("%s/filelist.txt"%exp_dir,"w")as f:
                f.write("\n".join(opt))
        
        """
            0: nosinging
            1: save lastest
            1: load to gpu mem (for 10mins audio)
        """
        
        cmd = "python3 train_nsf_sim_cache_sid_load_pretrain.py -e %s -sr %s -f0 %s -bs %s -te %s -se %s -pg %s -pd %s -l %s -c %s" \
            % (character_id, "48k", 0, batch_size,epochs,save_frequency,G_pth, D_pth, 1, 1)
        p = Popen(cmd, shell=True, cwd=current_dir)
        p.wait()
        print("STAGE3 DONEEEE")
        ## STAGE 4:
        feature_dir="%s/3_feature256"%(exp_dir)
        npys = []
        listdir_res=list(os.listdir(feature_dir))
        for name in sorted(listdir_res):
            phone = np.load("%s/%s" % (feature_dir, name))
            npys.append(phone)
        big_npy = np.concatenate(npys, 0)
        np.save("%s/%s_total_fea.npy" % (exp_dir, character_id), big_npy)
        n_ivf = big_npy.shape[0] // 39

        index = faiss.index_factory(256, "IVF%s,Flat"%n_ivf)

        index_ivf = faiss.extract_index_ivf(index)  #
        index_ivf.nprobe = int(np.power(n_ivf,0.3))
        index.train(big_npy)
        faiss.write_index(index, '%s/%s.index' % (exp_dir, character_id))

        index.add(big_npy)
        faiss.write_index(index, '%s/%s_main_index.index' % (exp_dir, character_id))
        print("STAGE4 DONEEEE")

    @app.post("/http_inference")
    async def http_inference(f0_up_key: int,
                             f0_method: str,
                             index_rate: float,
                             sr: int,
                             character_id: str,
                             file: bytes = File(...)):
        if character_id not in app.state.models:
            return "Model not found"
        
        t1 = time.time()
        audio_data = np.frombuffer(file, dtype=np.int16).astype(np.float32) / 32768.0
        audio_data = resample(audio_data, int(len(audio_data) * 16000 / sr))
        t2 = time.time()
        print("Audio processing time:", t2 - t1)

        times = [0, 0, 0]
        model, vc, net_g, tgt_sr, index, big_npy = app.state.models[character_id]
        if_f0 = model.get("f0", 1)

        start = time.time()
        audio_opt=vc.pipeline(hubert_model,net_g, 0,audio_data,times,f0_up_key,f0_method, index, big_npy,
                                index_rate,if_f0)
        end = time.time()
        print("Inference time:", end - start)
        
        with NamedTemporaryFile(delete=False) as f:
            soundfile.write(
                file=f, data=audio_opt, samplerate=tgt_sr, format="WAV"
            )

        return FileResponse(
            f.name,
            media_type="audio/wav",
        )

    @app.post("/load_model")
    async def load_pretrained_model(
        character_id: str
    ):

        model_path = 'characters/%s/model.pth' % character_id
        file_index = 'characters/%s/added_index.index' % character_id
        
        t1 = time.time()
        index = faiss.read_index(file_index)
        big_npy = index.reconstruct_n(0, index.ntotal)
        
        model, vc, net_g, tgt_sr = load_model(model_path, device, is_half)

        app.state.models[character_id] = [model, vc, net_g, tgt_sr, index, big_npy]

        t2 = time.time()
        print("time load model:", t2 - t1)
        return {"message": "Model loaded successfully."}
    
    @app.post('/delete_model')
    async def delete_model(character_id: str):
        if character_id in app.state.models:
            del app.state.models[character_id]
            print("deleted model")
            return {"message": "Model deleted successfully."}
        else:
            return {"message": "Model not found."}

    @app.get("/")
    async def index():
        return {"message": "Hello"}    
    
    return app


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="WebSocket Endpoint")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Hosting default: 0.0.0.0"
    )
    parser.add_argument(
        "--port", type=int, default=50011, help="Port WebSocket"
    )
    parser.add_argument(
        "--cpu", action='store_true', help="using cuda (gpu) for inference"
    )

    args = parser.parse_args()

    if args.cpu:
        device = torch.device('cpu')
        is_half = False
    else:
        device = torch.device('cuda')
        is_half = True

    print("using device:", device)
    print("is haft:", is_half)


    hubert_model = load_hubert(device, is_half)
    uvicorn.run(
        generate_app(
            hubert_model = hubert_model,
        ),
        host=args.host,
        port=args.port,
    )