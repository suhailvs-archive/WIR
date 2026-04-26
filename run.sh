#!/bin/bash

# https://github.com/bobbyiliev/introduction-to-bash-scripting
rm mysite/db.sqlite3
python manage.py migrate
python manage.py loaddata datas

# to run $ `bash run.sh`
