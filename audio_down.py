import os
import time
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SERVICE_ACCOUNT_FILE = 'service_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


GOOGLE_MIME_TYPES = {
    'application/vnd.google-apps.spreadsheet': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ext': '.xlsx'
    },
    'application/vnd.google-apps.document': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'ext': '.docx'
    }
}



def download_file_with_retry(authed_session, f_id, full_save_path, f_name, mime_type, max_retries=3):

    is_google_doc = mime_type in GOOGLE_MIME_TYPES
    
    if is_google_doc:
        ext = GOOGLE_MIME_TYPES[mime_type]['ext']
        if not full_save_path.endswith(ext):
            full_save_path += ext
            
        export_mime = GOOGLE_MIME_TYPES[mime_type]['export_mime']
        url = f"https://www.googleapis.com/drive/v3/files/{f_id}/export"
        params = {"mimeType": export_mime}
    else:
        url = f"https://www.googleapis.com/drive/v3/files/{f_id}"
        params = {"alt": "media"}

    if os.path.exists(full_save_path):
        return True

    for attempt in range(1, max_retries + 1):
        try:
            with authed_session.get(url, params=params, stream=True, timeout=(10, 30)) as r:
                r.raise_for_status()
                
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(full_save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=512*1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                print(f"  -> Down: {percent}%", end='\r')
                            else:
                                print(f"  -> Down: {downloaded // 1024} КБ", end='\r')
                                
            print(f"\n[Success] Save: {full_save_path}")
            return True
            
        except (Exception, KeyboardInterrupt) as e:
            print(f"\n {f_name}. Error: {type(e).__name__}")
            
            if os.path.exists(full_save_path):
                try: os.remove(full_save_path)
                except: pass
                
            if attempt < max_retries:
                time.sleep(2)
            else:
                return False
            

def download_all_from_folder(folder_id, local_destination_dir):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    authed_session = AuthorizedSession(creds)

    if not os.path.exists(local_destination_dir):
        os.makedirs(local_destination_dir)

    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false",
            "fields": "files(id, name, mimeType)",
            "pageSize": 100
        }
        
        response = authed_session.get(url, params=params, timeout=20)
        response.raise_for_status()
        files = response.json().get('files', [])

        if not files:
            print("Empty.")
            return

        for file_info in files:
            f_id = file_info['id']
            f_name = file_info['name']
            f_mime = file_info['mimeType']
            
            full_save_path = os.path.join(local_destination_dir, f_name)
            
            if not f_mime in GOOGLE_MIME_TYPES and os.path.exists(full_save_path):
                continue
                
            download_file_with_retry(authed_session, f_id, full_save_path, f_name, f_mime)

    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА]: {e}")



