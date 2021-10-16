# Securitycam

Simple security camera project, where arduino controlled ultrasonic sensor sends measured range \
to serial port and program reads it from there. When motion is detected, web-camera takes picture \
and it's been stored in the sqlite database with timestamp. Notification from new images will be send \
by email to users whose notifications are enabled.

Python web-server runs on hosted server, where authored users can browse those pictures.


**This program is made for school project and it is only for developing purposes.**\
**All the source code is free to use, copy and modify.**


## requirements

required python packages:

    pip install flask flask_login

required linux packages:

    apt-get install fswebcam

required arduino ultrasonic sensor:

- HC-SR04

## arduino files

Arduino sources are stored in src/arduino and need to compiled with arduino IDE\
and installed into the arduino microprocessor.

## creating database

create empty database with tables users and photos

    cd src/database
    ./create_db.sh -db createdb.sql

forced create (overwrites old and remove pictures) with imported test users

    ./create_db.sh -f -db createdb.sql -d dummy.sql

## running program

running with optional arguments

    cd src
    python3 security.py --flask_ip [ip] --flask_port [port] --arduino_port [serialport]

or with shell script to detect arduino port

    ./run.sh [possible flask ip/port opts]
