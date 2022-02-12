#!/usr/bin/env bash
set -e;

VERSION=1.1.6-dev
PROJECT_DIRECTORY=~/opendata_script
mkdir -p $PROJECT_DIRECTORY
curl -L "https://github.com/cuprit-gbr/cpak/releases/download/$VERSION/cpak" -o $PROJECT_DIRECTORY/cpak
chmod +x $PROJECT_DIRECTORY/cpak
ln -s $PROJECT_DIRECTORY/cpak /usr/local/bin/cpak

echo "created folder in $PROJECT_DIRECTORY"
echo "symlink created /usr/local/bin/cpak"
echo "try to run the script with cpak"