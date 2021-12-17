# cPAK

This python script (and binary) can be used to manage datasets with cKAN.
It expects python3 and is tested on *nix systems.


# Usage

```
Usage: cpak.py [OPTIONS] COMMAND [ARGS]...

  This script creates a cKAN dataset based on a metadata PDF and uploads all
  valid files in a folder and subfolders. Note run [command]--help on commands
  to get more information. Example: cpak set-settings --help

Options:
  --help  Show this message and exit.

Commands:
  delete-datasets         Batch delete datasets
  set-settings            This command will create a settings file called...
  show-allowed-extension  Show allowed extensions to upload
  show-pending-datasets   Show all pending datasets (private)
  show-settings           This command shows content of current...
  show-version            Show the current script version
  upload-package          This command will upload a dataset to cKAN.

```

# Install binary (Linux only)
```
curl -o- https://raw.githubusercontent.com/cuprit-gbr/cpak/main/install.sh | bash

# check if it works
cpak
```
