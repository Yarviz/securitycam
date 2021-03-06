#!/bin/bash

DATABASE='security.db'
PHOTO_DIR='photos'
force=false

check_next () {
    if [ $# -eq 1 ] || [ ${2::1} == "-" ]; then
        echo "define next arguments"
        exit 1
    fi
}

while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        -f|--force)
            force=true
            shift
        ;;
        -d|--dummy)
            check_next "$@"
            init_dummy=$2
            shift 2
        ;;
        -db|--database)
            check_next "$@"
            init_file=$2
            shift 2
        ;;
        *)
        shift
        ;;
    esac
done

if [ -f $DATABASE ]; then
    echo "$DATABASE already exists!"
    if [ $force == true ]; then
        echo "removing old database and photos"
        rm -f $DATABASE
        find $PHOTO_DIR -name "*.jpg" -type f -delete
    else
        exit 0
    fi
fi

if [ -z $init_file ]; then
    echo "database init file not defined"
    exit 1
fi

echo "Creating fresh database $DATABASE"

sqlite3 $DATABASE < $init_file

if [ -v init_dummy ];then
    echo "Importing dummy files"
    sqlite3 $DATABASE < $init_dummy
fi

if [ ! -d $PHOTO_DIR ]; then
    echo "Creating photo directory"
    mkdir $PHOTO_DIR
fi