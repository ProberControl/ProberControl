echo off

REM UPDATING PIP
python -m pip install --upgrade pip

REM INSTALLING ALL REQUIREMENTS
pip install -r requirements.txt

REM INSTALLING OPENCV
pip install opencv-python