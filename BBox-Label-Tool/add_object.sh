#!/usr/bin/env bash
echo "This tool is for prepare a new class for labeling."
echo "You will have to enter the class id and name, and the video to convert in images."
echo "Enter the class ID (integer):"

# Get class id, check value.
ID=""
while [[ ! $ID =~ ^[0-9]+$ ]]; do
    read ID
    if [[ ! $ID =~ ^[0-9]+$ ]]; then
        echo "This is not an Id. Type an integer!"
    fi
done
printf -v CLASS_ID "%03d" $ID

echo "Enter the class label: "
read CLASS_LABEL
echo "The class \"$CLASS_LABEL\" will be created with the id $CLASS_ID"

# Create related folders
mkdir -p ./Images/$CLASS_ID
mkdir -p ./Examples/$CLASS_ID
mkdir -p ./Labels/$CLASS_ID

# if [[ $REPLY =~ 'yes' ]]
# then
#     echo "Will save DB."
#     mkdir -p backup
#     touch "backup/backup-$(date +'%m%d%y-%R').json"
#     ./manage.py dumpdata > "backup/backup-$(date +'%m%d%y-%R').json"
#
#     # Remove previous DB
#     sudo rm ./db.sqlite3
#
#     # Initialise an empty DB
#     python manage.py makemigrations
#     python manage.py migrate --run-syncdb
#
#     # Create a superuser
#     echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell
#
#     # Start server
#     echo "START DJANGO SERVER"
#     python manage.py runserver
#
# fi
