#!/bin/bash

# Create python3 environment
python3 -m venv venv

# Activate
source ./venv/bin/activate

# Install requirements from requirements.txt file
pip install -r requirements.txt

# download
wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1gn3yWMyFDMrERgC23PfZup2mrNcnk9YT" -O hubert_base.pt

# create folder
mkdir characters/1
cd characters/1/
wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CQwH0FgepvWLIhPrjoFesYmsLuWNUOYP" -O added_index.index
wget --no-check-certificate "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CU_Q5V479XHAckb6KNWu9AGcXBf-92a_" -O model.pth

# run
cd ../..
python3 api.py
