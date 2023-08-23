import  AddIcon  from "@material-ui/icons/Add";
import  RemoveIcon  from "@material-ui/icons/Remove";
import { Button, Fab, FormControl, IconButton, InputLabel, TextField, Typography, makeStyles } from "@material-ui/core";
import Flex from "components/Flex/Flex";
import ModalCommon from "components/Modal/ModalCommon";
import { aiAgents, sampleVoice } from "pages/AllCharacters";
import { useEffect, useMemo, useRef, useState } from "react";
import { IAgentInfo, initAgent } from "./ModalCreateAiagent";
import { updateAgentAPI } from "service/api/api";
import axios from "axios";
import { notifyFail, notifySuccess } from "utils/notify";
import DeleteIcon from "@material-ui/icons/Delete";
import { EDIT_AGENT_TYPE } from "utils/util";
import { v4 as uuidv4 } from "uuid";
import PhotoCamera from "@material-ui/icons/PhotoCamera";
import { getLocalAccessToken } from "service/token";

const useStyles = makeStyles(() => ({
  row: {},
  inputTxt: {
    minWidth: 400,
    marginRight: 20,
    width: "100%",
  },
  label: {
    // minWidth: 400,
    textAlign: "left",
    fontWeight: 700,
  },
  iconConversation: {
    alignItems: "center",
    display: "flex",
    justifyContent: "center",
    cursor: "pointer",
    "&:hover": {
      opacity: 0.7,
    },
  },
  button:{
    height: '36.5px',
  },
  input:{
    // display: "none",
    opacity: 0,
    width: '24px',
    transform: 'translateX(-24px)',
    "&:hover": {
      // opacity: 0,
    }
  }
}));

export interface AiAgentEdit extends aiAgents {
  iconFile: any;
  pdfFile: any;
  voiceFile: any;
}

const ModalEditAgent = ({
  openDetail,
  setOpenDetail,
  agent,
}: {
  openDetail: boolean;
  setOpenDetail: (value: boolean) => void;
  agent: AiAgentEdit | undefined;
}) => {
  const token = getLocalAccessToken();
  const classes = useStyles();
  const [aiAgent, setAgent] = useState(agent);
  const [loadingEdit, setLoadingEdit] = useState(false);
  const [sampleVoiceData, setSampleVoiceData] = useState<any[]>([]);


  useEffect(() => {
    setAgent(agent);
  }, [agent]);

  // NOTE: FUNCTION CONVERSATION
  function handleChangeConversation(i: number, event: any) {
    const newValues = [...(aiAgent?.sample_dialog || [])];
    newValues[i].content = event.target.value;
    setAgent((prev: any) => ({ ...prev, sample_dialog: newValues }));
  }

  function handleAddConversation() {
    const newValues = [...(aiAgent?.sample_dialog || []), { content: "" }];
    setAgent((prev: any) => ({ ...prev, sample_dialog: newValues }));
  }

  function handleRemoveConversation(i: number) {
    const newValues = aiAgent?.sample_dialog.filter(
      (___, index) => index !== i
    );
    setAgent((prev: any) => ({ ...prev, sample_dialog: newValues }));
  }

  // NOTE: FUNCTION VOICE FILE
  function handleAddVoiceFile() {
    const newValues = [
      ...(aiAgent?.sample_voice || []),
      { file: null, id: uuidv4(), type: EDIT_AGENT_TYPE.create },
    ];
    setAgent((prev: any) => ({
      ...prev,
      sample_voice: newValues,
    }));
  }

  function handleRemoveVoiceFile(i: number, item: sampleVoice) {
    const newValues = aiAgent?.sample_voice.filter((___, index) => index !== i);
    setAgent((prev: any) => ({ ...prev, sample_voice: newValues }));

    if(item.type === EDIT_AGENT_TYPE.create) {
      const newValuesVoice = sampleVoiceData.filter((e, __) => e.id !== item.id)
      setSampleVoiceData(newValuesVoice);
    } else {
      if (!sampleVoiceData.map(e => e.id).includes(item.id)) {
        setSampleVoiceData((prev: any) => [...prev, ({id: item.id , type: EDIT_AGENT_TYPE.delete})])
      } else {
        const voiceExits = sampleVoiceData.find((e) => e.id === item.id);
        if (voiceExits) voiceExits.type = EDIT_AGENT_TYPE.delete;
      }
    }
  }

  function handleChangeVoiceFile(i: number, event: any, item: sampleVoice) {
    const newValues = [...(aiAgent?.sample_voice || [])];
    newValues[i].file = event.target.files?.[0];
    setAgent((prev: any) => ({ ...prev, sample_voice: newValues }));


    if (item?.type === EDIT_AGENT_TYPE.create) {
      if (!sampleVoiceData.map((e) => e.id).includes(item.id)) {
        setSampleVoiceData((prev: any) => [
          ...prev,
          {
            id: item.id,
            file: event.target.files?.[0],
            type: EDIT_AGENT_TYPE.create,
          },
        ]);
      } else {
        const voiceExits = sampleVoiceData.find(e => e.id === item.id)
        if(voiceExits) voiceExits.file = event.target.files?.[0];
      }
    } else {
      if (!sampleVoiceData.map((e) => e.id).includes(item.id)) {
        setSampleVoiceData((prev: any) => [
          ...prev,
          {
            id: item?.id,
            file: event.target.files?.[0],
            type: EDIT_AGENT_TYPE.update,
          },
        ]);
      } else {
        const voiceExits = sampleVoiceData.find((e) => e.id === item.id);
        if (voiceExits){
          voiceExits.file = event.target.files?.[0];
          voiceExits.type = EDIT_AGENT_TYPE.update;
        } 
      }
    }
  }

  const showBtnAddVoiceFile = useMemo(() => {
    if(aiAgent?.sample_voice.some(e => !e.file && e.type === EDIT_AGENT_TYPE.create)) return true
    return false
  }, [aiAgent]);

  const handleUpdateAgent = async () => {
    setLoadingEdit(true);

    const formData = new FormData();
    formData.append("user_id", aiAgent?.user_id as any);
    formData.append("name", aiAgent?.name as any);
    formData.append("introduction", aiAgent?.introduction as any);
    formData.append("pdf_file", aiAgent?.pdfFile as any);
    formData.append("icon_file", aiAgent?.iconFile as any);
    // formData.append("voice_model_file", voice?.[0] as any);
    formData.append("pinecone_namespace", "" as any);
    formData.append(
      "sampledialogs",
      JSON.stringify(aiAgent?.sample_dialog) as any
    );

    formData.append(
      "sample_voices_info",
      JSON.stringify(sampleVoiceData.map(e => ({id: e.id, type: e.type}))) as any
    );

    for (let i = 0; i < sampleVoiceData?.length; i++) {
      sampleVoiceData[i]?.file &&  formData.append("sample_voices_file", sampleVoiceData[i]?.file);
    }

    formData.append("age", aiAgent?.age as any);
    formData.append(
      "first_person_pronoun",
      aiAgent?.first_person_pronoun as any
    );
    formData.append(
      "second_person_pronoun",
      aiAgent?.second_person_pronoun as any
    );
    formData.append("activity", aiAgent?.activity as any);
    formData.append("hobbies", aiAgent?.hobbies as any);
    formData.append("occupation", aiAgent?.occupation as any);
    formData.append("speaking_style", aiAgent?.speaking_style as any);

    axios
      .put(
        `${process.env.REACT_APP_BASE_URL}/aiagents/update/${aiAgent?.id}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            "access-control-allow-origin": "*",
            "ngrok-skip-browser-warning": "*",
            Authorization: `Bearer ${token}`,
          },
        }
      )
      .then((response) => {
        notifySuccess("Update agent successfully");
      })
      .catch((error) => {
        notifyFail("Update agent fail");
      })
      .finally(() => {
        setLoadingEdit(false);
      });
  };

  return (
    <ModalCommon
      open={openDetail}
      setOpen={setOpenDetail}
      title="Update Ai agent"
      handleCloseModal={() => {
        setAgent(agent);
      }}
      loadingConfirm={loadingEdit}
      handleConfirm={() => {
        handleUpdateAgent();
      }}
    >
      <Flex className={classes.row}>
        <TextField
          size="small"
          required
          margin="normal"
          id="name"
          value={aiAgent?.name}
          variant="outlined"
          label="Name"
          onChange={(e) =>
            setAgent((prev: any) => ({ ...prev, name: e.target.value }))
          }
          className={classes.inputTxt}
        />
        <TextField
          type="number"
          required
          size="small"
          margin="normal"
          id="age"
          label="Age"
          value={aiAgent?.age}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({ ...prev, age: e.target.value }))
          }
          className={classes.inputTxt}
        />
      </Flex>
      <Flex>
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="First person pronoun"
          value={aiAgent?.first_person_pronoun}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              first_person_pronoun: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="Second person pronoun"
          value={aiAgent?.second_person_pronoun}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              second_person_pronoun: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
      </Flex>
      <Flex>
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="Activity"
          value={aiAgent?.activity}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              activity: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="Hobbies"
          value={aiAgent?.hobbies}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              hobbies: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
      </Flex>
      <Flex>
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="Occupation"
          value={aiAgent?.occupation}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              occupation: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
        <TextField
          required
          size="small"
          margin="normal"
          id="age"
          label="Speaking style"
          value={aiAgent?.speaking_style}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              speaking_style: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
      </Flex>
      <Flex>
        <TextField
          size="small"
          required
          multiline
          rows={4}
          margin="normal"
          id="description"
          label="Introduction"
          value={aiAgent?.introduction}
          variant="outlined"
          onChange={(e) =>
            setAgent((prev: any) => ({
              ...prev,
              introduction: e.target.value,
            }))
          }
          className={classes.inputTxt}
        />
      </Flex>
      <Flex
        alignItems="center"
        justifyContent="space-between"
        style={{ marginTop: 20 }}
      >
        <Typography className={classes.label}>Conversation</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleAddConversation}
          size="small"
          className={classes.button}
          style={{ marginLeft: 20 }}
        >
          <AddIcon />
          Add
        </Button>
      </Flex>
      {aiAgent?.sample_dialog.map((value, i) => (
        <Flex>
          <TextField
            size="small"
            required
            multiline
            rows={2}
            margin="normal"
            id="conversation"
            value={value.content}
            variant="outlined"
            onChange={(e) => handleChangeConversation(i, e)}
            className={classes.inputTxt}
          />
          {aiAgent?.sample_dialog.length > 1 && (
            <div
              onClick={() => handleRemoveConversation(i)}
              className={classes.iconConversation}
            >
              <DeleteIcon />
            </div>
          )}
        </Flex>
      ))}

      {/* // File  */}
      <Flex flexDirection="column" style={{ marginTop: 15 }}>
        <Typography className={classes.label}>Icon file</Typography>
        <div>{!aiAgent?.iconFile && aiAgent?.icon_file}</div>
        <FormControl margin="normal">
          {/* <label htmlFor="image_uploads">Choose images to upload (PNG, JPG)</label> */}
          {/* <InputLabel htmlFor="memoryFileLabel"></InputLabel> */}
          <input
            type="file"
            id="image_uploads"
            accept=".jpg,.fbx,.obj,.dae"
            name="image_uploads"
            onChange={(e) =>
              setAgent((prev: any) => ({
                ...prev,
                iconFile: e.target.files?.[0] as any,
              }))
            }
          />
        </FormControl>
      </Flex>

      <Flex flexDirection="column" style={{ marginTop: 15 }}>
        <Typography className={classes.label}>PDF file</Typography>
        {!aiAgent?.pdfFile && aiAgent?.pdf_file}
        <FormControl margin="normal">
          {/* <label htmlFor="image_uploads">Choose images to upload (PNG, JPG)</label> */}
          {/* <InputLabel htmlFor="memoryFileLabel"></InputLabel> */}
          <input
            type="file"
            id="samplecoives"
            accept=".pdf"
            name="samplecoives"
            onChange={(e) =>
              setAgent((prev: any) => ({
                ...prev,
                pdfFile: e.target.files?.[0] as any,
              }))
            }
          />
        </FormControl>
      </Flex>

      <Flex
        alignItems="center"
        justifyContent="space-between"
        style={{ marginTop: 20 }}
      >
        <Typography className={classes.label}>Voice file</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleAddVoiceFile}
          size="small"
          className={classes.button}
          style={{ marginLeft: 20 }}
          disabled={showBtnAddVoiceFile}
        >
          <AddIcon />
          Add
        </Button>
      </Flex>

      {/* ?.filter((item) => item?.type !== EDIT_AGENT_TYPE.delete) */}
      <Flex flexDirection="column">
        {aiAgent?.sample_voice.map((item, i) => 
              <Flex alignItems="center">
                <Flex alignItems="center" style={{ width: "90%" }}>
                  <Typography
                    style={{ margin: "10px 10px 0px 0px", maxWidth: "70%" }}
                  >
                    {typeof item?.file === "string"
                      ? item?.file
                      : item?.file?.name}
                  </Typography>
                  <label htmlFor="contained-button-file">
                    <IconButton
                      color="primary"
                      aria-label="upload picture"
                      component="span"
                      // style={{width: '24px'}}
                    >
                      <PhotoCamera style={{ marginLeft: 20}}/>
                      <input
                        type="file"
                        id="contained-button-file"
                        accept="audio/*"
                        className={classes.input}
                        onChange={(e) => {
                          handleChangeVoiceFile(i, e, item);
                        }}
                      />
                    </IconButton>
                  </label>
                </Flex>
                <div
                  onClick={() => handleRemoveVoiceFile(i, item)}
                  className={classes.iconConversation}
                >
                  <DeleteIcon />
                </div>
              </Flex>
        )}
      </Flex>
    </ModalCommon>
  );
};

export default ModalEditAgent;
