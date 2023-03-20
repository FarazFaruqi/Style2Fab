clear
eval "$(conda shell.bash hook)"
conda activate fa3ds

if [ !$1 ]
then 
    $1=8000
fi
echo "Running on port $1"
cd backend && python3 manage.py runserver $1