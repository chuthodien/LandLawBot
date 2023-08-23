FROM nvidia/cuda:11.6.0-cudnn8-devel-ubuntu20.04

ENV TZ=Asia/Kolkata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y wget ca-certificates ffmpeg build-essential dkms gnupg2 lsb-release python3-pip --fix-missing

WORKDIR /aime/rvc
COPY . .
RUN pip install -r requirements.txt
RUN wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1gn3yWMyFDMrERgC23PfZup2mrNcnk9YT" -O hubert_base.pt

RUN mkdir /aime/rvc/characters/male_test1

WORKDIR /aime/rvc/characters/male_test1
RUN wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CQwH0FgepvWLIhPrjoFesYmsLuWNUOYP" -O added_index.index
RUN wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CU_Q5V479XHAckb6KNWu9AGcXBf-92a_" -O model.pth

WORKDIR /aime/rvc

ENTRYPOINT ["python3", "api.py"]

