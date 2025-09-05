#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

# 4. Create a superuser if one doesn't exist
python manage.py create_superuser
echo "✅ انتهى build.sh بنجاح"