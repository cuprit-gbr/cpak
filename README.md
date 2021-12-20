# cPAK

This python script (and binary) can be used to manage datasets with cKAN.
It expects python3 and is tested on *nix systems.

# Install binary (Linux only)
```
curl -o- https://raw.githubusercontent.com/cuprit-gbr/cpak/main/install.sh | bash

# check if it works
cpak
```

# Usage

## Commands
```
Usage: python -m cpak [OPTIONS] COMMAND [ARGS]...

  This script creates a cKAN dataset based on a metadata PDF and uploads all
  valid files of a folder (subfolders included). Note: run [command] --help on
  commands to get more information. Example: cpak set-settings --help

Options:
  --help  Show this message and exit.

Commands:
  delete-datasets  Batch delete datasets by slug.
  fetch-archive    Fetch zip or tar resource and unpack it.
  review-needed    Show all pending datasets.
  set-settings     Create file 'settings.ini'
  show-settings    Show settings and version.
  upload-package   Upload a package to cKAN.

```

## Command details

### cpak delete-datasets --help
```
Usage: cpak.py delete-datasets [OPTIONS]

  Batch delete datasets by slug.

Options:
  -s, --slug TEXT  Slugs of datasets each as -s  [required]
  --help           Show this message and exit.
```

### cpak fetch-archive --help
```
Usage: cpak.py fetch-archive [OPTIONS]

  Fetch zip or tar resource and unpack it. You can then use the extracted dir
  as input for upload-package command

Options:
  -u, --url TEXT  Resource URL (only zip or tar.gz) i.e.
                  "https://example.com/data.zip"  [required]
  -o, --out TEXT  Local directory to extract file to i.e. /tmp  [required]
  --no-unpack     If set archive will not be unpacked
  --help          Show this message and exit.
```

### cpak review-needed --help

```
Usage: cpak.py review-needed [OPTIONS]

  Show all pending datasets.

Options:
  --help  Show this message and exit.

```

### cpak set-settings --help

```
Usage: cpak.py set-settings [OPTIONS]

  Create file 'settings.ini'

Options:
  --api-key TEXT    your iDAI.open_data API Key  [required]
  --url URL         your iDAI.open_data url  [required]
  --owner-org TEXT  The owner organisation. (default: dai-external)
  --username TEXT   Your Username, will be written to package.json  [required]
  --overwrite
  --help            Show this message and exit.
```

### cpak show-settings --help

```
Usage: cpak.py show-settings [OPTIONS]

  Show settings and version.

Options:
  --help  Show this message and exit.
```

### cpak upload-package --help

```
Usage: cpak.py upload-package [OPTIONS]

  Upload a package to cKAN. It needs a folder path as input. The folder must
  contain a pdf called metadata.pdf. The Form data is used to create a new
  packge

Options:
  --folder_path TEXT  The path to your data folder: Example "/tmp/my_dataset"
                      [required]
  --help              Show this message and exit.
```
