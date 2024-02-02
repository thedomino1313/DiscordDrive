import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveAPI:
    root = {"name":None, "id":None}

    SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.activity", "https://www.googleapis.com/auth/drive.metadata"]
    def __init__(self, root):
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

            results = (
                self.service.files()
                .list(pageSize=1, q=f"mimeType='application/vnd.google-apps.folder' and trashed = false and 'me' in owners and name contains '{self.root['name']}'", orderBy="folder, name", fields="nextPageToken, files(id, name)")
                .execute()
            )
            item = results.get("files", [])

            if not item:
                print("No folders found, check the root name.")
                return
            item = item[0]
            self.root = item
            print(f"Found folder '{self.root['name']}' with id '{self.root['id']}'")
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f"An error occurred: {error}")


if __name__ == "__main__":
  API = DriveAPI("RPI")