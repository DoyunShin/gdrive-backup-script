# GDrive Backup Script

This script is used to backup files from a local directory to Google Drive. It uses the Google Drive API to upload files to Google Drive.

## Installation

1. Install the script by running the following command:
    ```bash
    curl -L https://raw.githubusercontent.com/DoyunShin/gdrive-backup-script/master/gbackup.py > /usr/local/bin/gbackup
    chmod +x /usr/local/bin/gbackup
    sudo su - -c "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    ```

2. Create a credential file with service account key. Follow the instructions [here](https://cloud.google.com/docs/authentication/getting-started) to create a service account credential. 

    And save it as `gdrive-credentials.json` in the directory `~/.config/gbackup/`.
