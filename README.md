# upload datasets and resources

```
Usage: cpak.py [OPTIONS] COMMAND [ARGS]...

  This script creates a cKAN dataset based on a metadata PDF and uploads all
  valid files in a folder and subfolders

Options:
  --help  Show this message and exit.

Commands:
  set-settings    This command will create a settings file called...
  show-settings   This command shows content of current 'settings.ini'.
  show-version    Show the current script version
  upload-package  This command will upload a package to cKAN.
```
### Download binary

```
VERSION=1.0.0-dev
PROJECT_DIRECTORY=~/opendata_script
mkdir -p $PROJECT_DIRECTORY
curl -L "https://github.com/cuprit-gbr/cpak/releases/download/$VERSION/cpak" -o $PROJECT_DIRECTORY/cpak
chmod +x $PROJECT_DIRECTORY/cpak
ln -s $PROJECT_DIRECTORY/cpak /usr/local/bin/cpak

# check if it works
cpak
```