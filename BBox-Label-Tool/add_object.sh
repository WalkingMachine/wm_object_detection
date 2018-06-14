#!/usr/bin/env bash
echo "This tool is for prepare a new class for labeling."
echo "You will have to enter the class id and name, and the video to convert in images."
read -p "Enter the class ID: " -r
class_id=$REPLY
read -p "Enter the class label: " -r
class_label=$REPLY
echo "The class $class_label got the id $class_id"

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
