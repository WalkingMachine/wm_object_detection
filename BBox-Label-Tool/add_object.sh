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

# Select video
FILE=`zenity --file-selection --title="Sélectionnez la video"`
case $? in
        0)
              echo "\"$FILE\" est sélectionné."
              ffmpeg -i $FILE -vf fps=10 ./Images/$CLASS_ID/$CLASS_LABEL%d.JPEG
              python main.py
              ;;
        1)
              echo "Aucun fichier sélectionné. Va quitter";;
        -1)
              echo "Une erreur inattendue est survenue.";;
esac
