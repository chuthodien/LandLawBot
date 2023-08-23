## Run server on Ubuntu

* Read setup.sh replace compatible command for window setup

* Python version >=3.8, <3.9

* install ffmpeg

<pre>
    sudo apt-get install ffmpeg
</pre>

## Method1: Install and run using setup

<pre>
    chmod +x setup.sh
    ./setup.sh
</pre>

## Method2: Install and run step by step

* create and activate environment (if current python version > 3.8)
<pre>
    python3 -m venv venv
    source ./venv/bin/activate
</pre>

* install requirements
<pre>
    pip install -r requirements.txt
</pre>

* install update fastapi
<pre>
    pip install fastapi
</pre>

* download hubert_base.pt
<pre>
    wget "https://docs.google.com/uc?export=download&confirm=t&amp&id=1gn3yWMyFDMrERgC23PfZup2mrNcnk9YT" -O hubert_base.pt
</pre>

* create folder and download example model
<pre>
    mkdir characters
    mkdir characters/male_test1
    cd characters/male_test1/
    wget "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CQwH0FgepvWLIhPrjoFesYmsLuWNUOYP" -O added_index.index
    wget "https://docs.google.com/uc?export=download&confirm=t&amp&id=1CU_Q5V479XHAckb6KNWu9AGcXBf-92a_" -O model.pth
</pre>

* run api
<pre>
    cd ../..
    python3 api.py
</pre>