import os
import json
import io

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "..", "service_account.json")
OAUTH_TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "token.json")

class GoogleDriveConnector:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        """Initializes Google Drive API service using service_account.json or oauth credentials."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", CREDENTIALS_FILE)
            if os.path.exists(creds_path):
                creds = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=creds)
            elif os.path.exists(OAUTH_TOKEN_FILE):
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_file(
                    OAUTH_TOKEN_FILE,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            self.service = None

    def is_configured(self) -> bool:
        return self.service is not None

    def list_files(self, query: str = "", max_results: int = 10) -> str:
        """Lists files from Google Drive."""
        if not self.service:
            return (
                "Google Drive belum terhubung. Silakan letakkan file 'service_account.json' atau 'token.json' "
                "di root folder project hermes-agentic."
            )
        try:
            q = "trashed = false"
            if query:
                q += f" and (name contains '{query}' or fullText contains '{query}')"
            
            results = self.service.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return "Tidak ada file yang ditemukan di Google Drive."
            
            output = ["Daftar File Google Drive:"]
            for f in files:
                size_str = f" ({f.get('size')} bytes)" if 'size' in f else ""
                output.append(f"- **{f['name']}** (ID: `{f['id']}`, Type: {f['mimeType']}{size_str})")
            return "\n".join(output)
        except Exception as e:
            return f"Error listing Google Drive files: {str(e)}"

    def read_file(self, file_id: str) -> str:
        """Reads content of a document or file from Google Drive."""
        if not self.service:
            return "Google Drive belum terhubung. File 'service_account.json' diperlukan."
        try:
            from googleapiclient.http import MediaIoBaseDownload
            
            file_meta = self.service.files().get(fileId=file_id, fields="name, mimeType").execute()
            mime_type = file_meta.get("mimeType", "")
            file_name = file_meta.get("name", file_id)
            
            # Handle Google Docs / Sheets exports
            if mime_type == "application/vnd.google-apps.document":
                request = self.service.files().export_media(fileId=file_id, mimeType="text/plain")
            elif mime_type == "application/vnd.google-apps.spreadsheet":
                request = self.service.files().export_media(fileId=file_id, mimeType="text/csv")
            else:
                request = self.service.files().get_media(fileId=file_id)
                
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
                
            fh.seek(0)
            content = fh.read().decode('utf-8', errors='ignore')
            return f"### Konten File: {file_name}\n\n{content[:5000]}" + ("\n...[Truncated]" if len(content) > 5000 else "")
        except Exception as e:
            return f"Error reading file {file_id}: {str(e)}"

    def upload_text_file(self, name: str, content: str, folder_id: str = "") -> str:
        """Creates or uploads a new text file to Google Drive."""
        if not self.service:
            return "Google Drive belum terhubung. File 'service_account.json' diperlukan."
        try:
            from googleapiclient.http import MediaInMemoryUpload
            
            file_metadata = {'name': name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
                
            media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain', resumable=True)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink').execute()
            return f"File '{file.get('name')}' berhasil diunggah ke Google Drive! (ID: `{file.get('id')}`)"
        except Exception as e:
            return f"Error uploading file to Google Drive: {str(e)}"
