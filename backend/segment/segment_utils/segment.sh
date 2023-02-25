clear
eval "$(conda shell.bash hook)"
conda activate fa3ds
screen -d -m -S "segmentations_screen" -L -Logfile segmentation.log python3 /home/ubuntu/fa3ds/backend/segment/segment_utils/mesh_editor.py
screen -x