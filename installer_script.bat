@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Running Downloads Cleanup App...
python "Downloads CleanUp App.py"
pause
