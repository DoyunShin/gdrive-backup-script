#!/usr/bin/python3
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
import mimetypes
import json
import sys

class gdrive():
    def __init__(self, credential: Path, root: str):
        credential = json.loads(credential.read_text())
        self.credential = service_account.Credentials.from_service_account_info(credential, scopes=["https://www.googleapis.com/auth/drive"])
        self.service = build('drive', 'v3', credentials=self.credential)
        self.root = root

    def _get_files(self, **kwargs):
        if "fields" not in kwargs:
            kwargs["fields"] = "nextPageToken, files(id, name, mimeType)"
        return self.service.files().list(includeItemsFromAllDrives=True, supportsAllDrives=True, pageSize=1000, **kwargs)
        
    def get_list(self) -> dict:
        """
        Return:
            dict[name, gid]
        """
        query = f"'{self.root}' in parents"
        results = self._get_files(q=query).execute()
        files = {}
        for i in results["files"]:
            files[i["name"]] = i["id"]
        
        return files
    
    def _upload(self, metadata: dict, media = None) -> str:
        kwargs = {"body": metadata, "fields": "id"}
        if media: kwargs["media_body"] = media
        file = self.service.files().create(supportsAllDrives=True, **kwargs).execute()
        return file.get('id')

    def mkdir(self, name: str) -> str:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.root]
        }
        return self.upload(file_metadata)

    def upload(self, file: Path, dirid: str = None) -> dict:
        """
        Args:
            file: Path to file
        
        Return:
            dict[filename, fileid]
        """

        if not dirid: dirid = self.root

        file_info = {
            'name': file.name,
            'parents': [dirid]
        }

        mimetype = mimetypes.guess_type(file)[0]

        media = MediaFileUpload(file, mimetype)
        fileid = self._upload(file_info, media)

        return fileid

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        #raise ValueError("Usage: upload.py <file> <root>")
        print("Usage: upload.py <file> <root>")
        exit(1)
    cred = Path.home() / ".config" / "gbackup" / "gdrive-credential.json"
    cred = cred.resolve()
    uploadfile = Path(args[0])
    root = args[1]

    if not cred.exists():
        raise FileNotFoundError(f"Credential {cred} not found")
    if not uploadfile.exists():
        raise FileNotFoundError(f"File {uploadfile} not found")
    if not root:
        raise ValueError("Root not set")
    
    g = gdrive(cred, root)
    rtn = g.upload(uploadfile)
    print(rtn)
    exit(0)

