# upload datasets and resources

```
Usage: cpak.py [OPTIONS] COMMAND [ARGS]...
Usage from binary: cpak [OPTIONS] COMMAND [ARGS]...

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
### Install binary (Linux only)

```
curl -o- https://raw.githubusercontent.com/cuprit-gbr/cpak/main/install.sh | bash

# check if it works
cpak
```
