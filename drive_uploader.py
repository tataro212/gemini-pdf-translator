"""
Google Drive Uploader Module for Ultimate PDF Translator

Handles Google Drive integration and file uploads
"""

import os
import logging
from config_manager import config_manager

logger = logging.getLogger(__name__)

class GoogleDriveUploader:
    """Handles Google Drive uploads with authentication and error handling"""
    
    def __init__(self):
        self.drive_settings = config_manager.google_drive_settings
        self.credentials_file = self.drive_settings['credentials_file']
        self.target_folder_id = self.drive_settings['target_folder_id']
        self.drive = None
        self._initialize_drive()
    
    def _initialize_drive(self):
        """Initialize Google Drive connection"""
        try:
            # Check if required files exist
            if not os.path.exists("client_secrets.json"):
                logger.warning("Google Drive upload not available. 'client_secrets.json' not found.")
                return
            
            # Try to import and initialize PyDrive2
            from pydrive2.auth import GoogleAuth
            from pydrive2.drive import GoogleDrive
            
            # Authenticate
            gauth = GoogleAuth()
            
            # Try to load saved credentials
            if os.path.exists(self.credentials_file):
                gauth.LoadCredentialsFile(self.credentials_file)
            
            if gauth.credentials is None:
                # Authenticate if they're not there
                logger.info("Google Drive authentication required...")
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Refresh them if expired
                logger.info("Refreshing Google Drive credentials...")
                gauth.Refresh()
            else:
                # Initialize the saved creds
                gauth.Authorize()
            
            # Save the current credentials to a file
            gauth.SaveCredentialsFile(self.credentials_file)
            
            # Initialize Google Drive
            self.drive = GoogleDrive(gauth)
            logger.info("Google Drive initialized successfully")
            
        except ImportError:
            logger.warning("PyDrive2 not available. Install with: pip install PyDrive2")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive: {e}")
    
    def upload_to_google_drive(self, filepath_to_upload, filename_on_drive, gdrive_folder_id=None):
        """Upload file to Google Drive"""
        if not self.drive:
            logger.warning("Google Drive not initialized. Skipping upload.")
            return None
        
        if gdrive_folder_id is None:
            gdrive_folder_id = self.target_folder_id
        
        if not gdrive_folder_id:
            logger.warning("No Google Drive folder ID specified. Skipping upload.")
            return None
        
        try:
            logger.info(f"--- Uploading to Google Drive: {filename_on_drive} ---")
            
            # Check if file exists
            if not os.path.exists(filepath_to_upload):
                logger.error(f"File not found for upload: {filepath_to_upload}")
                return None
            
            # Create file metadata
            file_metadata = {
                'title': filename_on_drive,
                'parents': [{'id': gdrive_folder_id}]
            }
            
            # Create and upload file
            drive_file = self.drive.CreateFile(file_metadata)
            drive_file.SetContentFile(filepath_to_upload)
            drive_file.Upload()
            
            # Get file info
            file_id = drive_file['id']
            file_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            logger.info(f"Successfully uploaded to Google Drive: {filename_on_drive}")
            logger.info(f"Google Drive URL: {file_url}")
            
            return {
                'file_id': file_id,
                'file_url': file_url,
                'filename': filename_on_drive
            }
            
        except Exception as e:
            logger.error(f"Google Drive upload failed: {e}")
            return None
    
    def upload_multiple_files(self, file_list, folder_id=None):
        """Upload multiple files to Google Drive"""
        if not self.drive:
            logger.warning("Google Drive not initialized. Skipping uploads.")
            return []
        
        results = []
        
        for file_info in file_list:
            filepath = file_info.get('filepath')
            filename = file_info.get('filename')
            
            if not filepath or not filename:
                logger.warning(f"Invalid file info: {file_info}")
                continue
            
            result = self.upload_to_google_drive(filepath, filename, folder_id)
            if result:
                results.append(result)
        
        logger.info(f"Uploaded {len(results)} out of {len(file_list)} files to Google Drive")
        return results
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a new folder in Google Drive"""
        if not self.drive:
            logger.warning("Google Drive not initialized. Cannot create folder.")
            return None
        
        try:
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [{'id': parent_folder_id}]
            
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            
            folder_id = folder['id']
            folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
            
            logger.info(f"Created Google Drive folder: {folder_name}")
            logger.info(f"Folder URL: {folder_url}")
            
            return {
                'folder_id': folder_id,
                'folder_url': folder_url,
                'folder_name': folder_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Drive folder: {e}")
            return None
    
    def list_files_in_folder(self, folder_id):
        """List files in a Google Drive folder"""
        if not self.drive:
            logger.warning("Google Drive not initialized. Cannot list files.")
            return []
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            file_list = self.drive.ListFile({'q': query}).GetList()
            
            files = []
            for file in file_list:
                files.append({
                    'id': file['id'],
                    'title': file['title'],
                    'mimeType': file['mimeType'],
                    'createdDate': file['createdDate'],
                    'modifiedDate': file['modifiedDate']
                })
            
            logger.info(f"Found {len(files)} files in Google Drive folder")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            return []
    
    def is_available(self):
        """Check if Google Drive upload is available"""
        return self.drive is not None
    
    def get_upload_summary(self, uploaded_files):
        """Generate upload summary report"""
        if not uploaded_files:
            return "No files were uploaded to Google Drive."
        
        summary = f"""
📤 GOOGLE DRIVE UPLOAD SUMMARY
=============================
✅ Successfully uploaded: {len(uploaded_files)} files

Files uploaded:
"""
        
        for file_info in uploaded_files:
            filename = file_info.get('filename', 'Unknown')
            file_url = file_info.get('file_url', 'No URL')
            summary += f"• {filename}\n  📎 {file_url}\n"
        
        if self.target_folder_id:
            folder_url = f"https://drive.google.com/drive/folders/{self.target_folder_id}"
            summary += f"\n📁 Target folder: {folder_url}\n"
        
        summary += "=============================\n"
        
        return summary

# Global Google Drive uploader instance
drive_uploader = GoogleDriveUploader()
