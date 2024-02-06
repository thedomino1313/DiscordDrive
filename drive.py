import os.path
from os import getcwd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveAPI:
    root = {"name":None, "id":None}
    
    folders = dict()

    FOLDER_TYPE = "application/vnd.google-apps.folder"
    SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.activity", "https://www.googleapis.com/auth/drive.metadata"]
    
    def __init__(self, root:str):
        print(getcwd())
        if not root:
            raise Exception("A root directory must be provided.")
        self.root["name"] = root
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("drive", "v3", credentials=creds)

            folder = self.search(name=self.root['name'], files=False)
            
            if not folder:
                print("No folders found, check the root name.")
                return
            folder = folder[0]
            self.root = folder
            self.folders[self.root['name']] = self.root['id']
            print(f"Found folder '{self.root['name']}' with id '{self.root['id']}'")
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f"An error occurred: {error}")

    def folder_id_lookup(self, folder):
        try:
            return self.folders[folder]
        except:
            found_folder = self.search(name=folder, files=False)[0][0]
            if not found_folder:
                raise HttpError("No folders were found")
            self.folders[found_folder["name"]] = found_folder["id"]
            return found_folder["id"]

    def update_folders(self, flist):
        for file in flist:
            if file["mimeType"] == self.FOLDER_TYPE:
                self.folders[file["name"]] = file["id"]

    def search(self, name:str='', pageSize:int=1, parent:str='', files=True, folders=True, pageToken:str='', recursive=False):
        l = locals()
        if any(l[var] == None for var in l):
            raise Exception("Please do not input parameters as None")

        nameScript = f" and name contains '{name}'" if name != "" and name else ""

        try:
            parentScript = f" and '{self.folder_id_lookup(parent)}' in parents" if parent != "" and parent else ""
        except HttpError as error:
            print(f"The parent folder does not exist: {error}")
            return None, None
        
        if nameScript == parentScript:
            raise Exception("Both parameters cannot be empty.")
        
        if files and folders:
            mimeScript = ""
        elif files:
            mimeScript = f"and mimeType!='{self.FOLDER_TYPE}'"
        else:
            mimeScript = f"and mimeType='{self.FOLDER_TYPE}'"

        try:
            results = (
                self.service.files()
                .list(pageSize=pageSize, 
                      pageToken=pageToken, 
                      q=f"trashed = false{mimeScript}{nameScript}{parentScript}", 
                      orderBy="folder, name", 
                      fields="nextPageToken, files(id, name, mimeType)")
                .execute()
            )
            files = results.get("files", [])
            self.update_folders(files)
            if (pageToken := results.get("nextPageToken", "")) != "" and recursive:
                return results.get("files", []) + self.search(name=name, pageSize=pageSize, parent=parent, files=files, folders=folders, pageToken=pageToken, recursive=recursive)
            return files
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None, None

if __name__ == "__main__":
    API = DriveAPI("RPI")
    print(API.search(pageSize=100, parent="RPI"))