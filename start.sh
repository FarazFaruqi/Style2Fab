clear
eval "$(conda shell.bash hook)"
conda activate fa3ds
cd backend && python3 manage.py runserver