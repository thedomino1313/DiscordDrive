import os.path

from inspect import getfullargspec

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from discord import Attachment


class DriveAPI:
    root = {"name":None, "id":None}
    
    folders = dict()

    FOLDER_TYPE = "application/vnd.google-apps.folder"
    SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.activity", "https://www.googleapis.com/auth/drive.metadata"]
    
    def _input_validator(func):
        def _validate(self, *args, **kwargs):
            argspecs = getfullargspec(func)
            annotations = argspecs.annotations
            argnames = argspecs.args
            for val, arg in zip(args, argnames[1:len(args) + 1]):
                assert val is not None, f"Argument '{arg}' is None, please do not use None as an argument"
                assert type(val) == annotations[arg], f"Argument '{arg}' is not of the type '{str(annotations[arg])[8:-2]}'."
            for arg in kwargs:
                assert kwargs[arg] is not None, f"Argument '{arg}' is None, please do not use None as an argument."
                assert type(kwargs[arg]) == annotations[arg], f"Argument '{arg}' is not of the type '{str(annotations[arg])[8:-2]}'."
            return func(self, *args, **kwargs)    
        return _validate
    
    def _temp_dir(path):
        def _temp_decorator(func):
            async def _temp_manager(self, *args, **kwargs):
                if not os.path.exists(path):
                    os.mkdir(path)
                ret = await func(self, *args, **kwargs)
                for file in os.listdir(path):
                    os.remove(os.path.join(path, file))
                os.rmdir(path)
                return ret
            return _temp_manager
        return _temp_decorator

    @_input_validator
    def __init__(self, root:str):
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
                raise Exception("No folders found, check the root name.")
            folder = folder[0]
            self.root = folder
            self.folders[self.root['name']] = self.root['id']
            print(f"Found folder '{self.root['name']}' with id '{self.root['id']}'")
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f"An error occurred: {error}")

    @_input_validator
    def folder_id_lookup(self, folder:str) -> str:
        if not folder:
            raise Exception("Folder name cannot be an empty string.")
        try:
            return self.folders[folder]
        except:
            found_folder = self.search(name=folder, files=False)[0]
            if not found_folder:
                raise HttpError("No folders were found")
            self.folders[found_folder["name"]] = found_folder["id"]
            return found_folder["id"]

    @_input_validator
    def update_folders(self, flist:list) -> None:
        for file in flist:
            if file["mimeType"] == self.FOLDER_TYPE:
                self.folders[file["name"]] = file["id"]
    
    @_input_validator
    def search(self, name:str='', parent:str='', pageSize:int=1, files:bool=True, folders:bool=True, pageToken:str='', recursive:bool=False) -> list:
        """Modular search function that can find files and folders, with the option of a specified parent directory.

        Args:
            name (str, optional): Name of a specific file/folder to find. Defaults to ''.
            parent (str, optional): Name of a parent folder to search inside of. Defaults to ''.
            pageSize (int, optional): Number of results to return. Defaults to 1.
            files (bool, optional): Enable searching for files. Defaults to True.
            folders (bool, optional): Enable searching for folders. Defaults to True.
            pageToken (str, optional): Token for the next page of results. Defaults to ''.
            recursive (bool, optional): Search all pages for all results. Defaults to False.

        Raises:
            Exception: Any input parameters are None
            Exception: Both the name and parent fields are left blank

        Returns:
            list(dict): A list of the files found. Format: [{'mimeType': 'application/vnd.google-apps.folder', 'id': '1FkOWqVDhbj8y5N7gq7-XQqQjCceMVLN9', 'name': 'Example'},...]
        """
        
        # Generate the search parameter for a file name
        nameScript = f" and name = '{name}'" if name else ""

        # Generate the search parameter for a parent folder
        try:
            # Lookup the parent folder's ID
            parentScript = f" and '{self.folder_id_lookup(parent)}' in parents" if parent else ""
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
            foundfiles = results.get("files", [])
            self.update_folders(foundfiles)
            if (pageToken := results.get("nextPageToken", "")) and recursive:
                return foundfiles + self.search(name=name, pageSize=pageSize, parent=parent, files=files, folders=folders, pageToken=pageToken, recursive=recursive)
            return foundfiles
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    @_input_validator
    @_temp_dir("temp")
    async def upload_from_discord(self, file:Attachment, folder:str=""):
        filename = f"temp/{file.filename}"
        await file.save(filename)
        return self.upload(file.filename, file.content_type, path="temp", folder=folder)
        

    @_input_validator
    def upload(self, file:str, content_type:str, path:str=".", folder:str=""):
        if not folder:
            folder = self.root["name"]
        
        file_metadata = {"name": file, "parents": [self.folder_id_lookup(folder)]}
        
        media = MediaFileUpload(path + "/" + file, mimetype=content_type)
        
        try:
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="name")
                .execute()
            )
            return file["name"]
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

if __name__ == "__main__":
    API = DriveAPI("Textbooks")
    print("\n".join([f"{result['name']} is of type {result['mimeType']} with ID {result['id']}" for result in API.search(pageSize=100, parent=API.root["name"])]))