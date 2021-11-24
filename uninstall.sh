#!/usr/bin/env bash
set -e;

read -p "Are you sure? [y/n]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    PROJECT_DIRECTORY=~/opendata_script
    rm -rf $PROJECT_DIRECTORY /usr/local/bin/cpak
    echo Deleted:$PROJECT_DIRECTORY /usr/local/bin/cpak
fi