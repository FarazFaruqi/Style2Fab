clear
eval "$(conda shell.bash hook)"
conda activate fa3ds
screen -d -m -S "preprocess_screen" -L -Logfile /home/ubuntu/fa3ds/backend/edit/edit_utils/preprocess.log python3 /home/ubuntu/fa3ds/backend/edit/edit_utils/preprocess.py
screen -x