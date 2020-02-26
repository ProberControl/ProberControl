echo off

REM UPDATING PIP
python -m pip install --upgrade pip

REM INSTALLING ALL REQUIREMENTS
python -m pip install -r requirements.txt

REM INSTALLING OPENCV
python -m pip install opencv-python

pause