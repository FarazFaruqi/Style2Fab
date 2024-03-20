#!/bin/bash
clear
eval "$(conda shell.bash hook)"
conda activate kaolin-env

echo "Python Executable: $(which python3)"
echo "Python Path: $(python3 -c 'import sys; print(sys.path)')"

if [ !$1 ]
then 
    $1=8000
fi
echo "Running on port $1"
cd backend && python3 manage.py runserver $1
echo "Python Executable: $(which python3)"
echo "Python Path: $(python3 -c 'import sys; print(sys.path)')"
