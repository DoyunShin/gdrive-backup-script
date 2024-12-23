#!/usr/bin/python3
import importlib.util

required = [
    "googleapiclient.http",
    "googleapiclient.discovery",
    "google.oauth2"
]

if not all([importlib.util.find_spec(i) for i in required]):
    raise ImportError("One or more required modules not found. Check https://github.com/DoyunShin/gdrive-backup-script/ for more information")

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
import mimetypes
import json
import sys
import os

class gdrive():
    def __init__(self, credential: Path, root: str):
        credential = json.loads(credential.read_text())
        self.credential = service_account.Credentials.from_service_account_info(credential, scopes=["https://www.googleapis.com/auth/drive"])
        self.service = build('drive', 'v3', credentials=self.credential)
        self.root = root

        self._is_root_accessible()

    def _is_root_accessible(self):
        query = f"'{self.root}' in parents"
        self._get_files(q=query).execute()
        return True

    def _get_files(self, **kwargs):
        if "fields" not in kwargs:
            kwargs["fields"] = "nextPageToken, files(id, name, mimeType)"
        return self.service.files().list(includeItemsFromAllDrives=True, supportsAllDrives=True, pageSize=1000, **kwargs)
    
    def _upload(self, metadata: dict, media = None) -> str:
        kwargs = {"body": metadata, "fields": "id"}
        if media: kwargs["media_body"] = media
        file = self.service.files().create(supportsAllDrives=True, **kwargs).execute()
        return file.get('id')

    def get_list(self) -> dict:
        """Get list of files in the root folder
        
        Returns:
            files(dict[name, gid]): Dictionary of file name and Google Drive file id
        """

        query = f"'{self.root}' in parents"
        results = self._get_files(q=query).execute()
        files = {}
        for i in results["files"]:
            files[i["name"]] = i["id"]
        
        return files

    def mkdir(self, name: str) -> str:
        """Create folder in Google Drive

        Args:
            name(str): Name of the folder
            
        Returns:
            gid(str): Google Drive folder id
        """

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.root]
        }
        return self.upload(file_metadata)

    def upload(self, file: Path, dirid: str = None) -> str:
        """Upload file to Google Drive

        Args:
            file(pathlib.Path): Path to file
        
        Return:
            fileid(str): Google Drive file id
        """

        if not dirid: dirid = self.root

        file_info = {
            'name': file.name,
            'parents': [dirid]
        }

        mimetype = mimetypes.guess_type(file)[0]

        media = MediaFileUpload(file, mimetype, resumable=True)
        fileid = self._upload(file_info, media)

        return fileid

def update():
    os.system("sudo sh -c 'curl -L https://raw.githubusercontent.com/DoyunShin/gdrive-backup-script/master/gbackup.py > /usr/local/bin/gbackup'")
    os.system("sudo chmod +x /usr/local/bin/gbackup")
    print("Updated to latest version")
    

if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args:
        print("Usage: gbackup.py <file> <gfolderid>")
        print("    file: file to upload")
        print("    gfolderid: Google Drive folder id")
        print()
        print("Credential file: ~/.config/gbackup/gdrive-credential.json (Service Account)")
        print("To update: gbackup.py --update / -u")
        print("Check https://github.com/DoyunShin/gdrive-backup-script for more information")
        exit(0)

    elif "--update" in args or "-u" in args:
        update()
        exit(0)

    elif len(args) != 2:
        print("Usage: gbackup.py <file> <gfolderid>")
        print("Check https://github.com/DoyunShin/gdrive-backup-script for more information")
        exit(1)

    cred = Path.home() / ".config" / "gbackup" / "gdrive-credential.json"
    cred = cred.resolve()
    uploadpath = Path(args[0])
    root = args[1]

    if not cred.exists():
        raise FileNotFoundError(f"Credential {cred} not found")
    if not root:
        raise ValueError("Root not set")

    if uploadpath.is_dir():
        files = [i for i in uploadpath.iterdir() if i.is_file()]
    elif uploadpath.is_file():
        files = [uploadpath]
    else:
        raise FileNotFoundError(f"File not found: {uploadpath}")
    
    g = gdrive(cred, root)

    for i in files:
        rtn = g.upload(i)
        print(f"{rtn} - {i.name}")
    
    exit(0)
