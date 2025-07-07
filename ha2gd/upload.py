import os
import sys
import shutil
from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth
from datetime import datetime
from signal import signal, SIGPIPE, SIG_DFL 

signal(SIGPIPE,SIG_DFL) 
g_history_days = 9 #days to keep history on Google Drive
l_history_days = 3 #days to keep history locally
logfile = "update_log.txt"
workdir = "/share/ha2gd/"
os_root = "/media/cctv/cctv/entrance/"
gdrive_root_id = "" #fill it by own value
os.environ['TZ'] = "" #fill it by own value


def upload_handler(gauth, os_root_path, gdrive_root_folder_id):

  drive = GoogleDrive(gauth)
  gdrive_item_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(gdrive_root_folder_id)}).GetList()
  g_folders = {}
  for item in gdrive_item_list:
    if item['mimeType'].endswith('vnd.google-apps.folder'):
      g_folders[item['title']] = item['id']

  if len(g_folders) > g_history_days:
    oldest_folder = min(g_folders.keys())
    delete_item = drive.CreateFile({'id': g_folders[oldest_folder]})
    delete_item.Delete()
    with open(workdir + logfile, 'a') as update_log:
      update_log.write( '\n' + 'Deleted gdrive folder: %s %s' % (oldest_folder, str(datetime.now())))
    g_folders.pop(oldest_folder, None)

  l_folders = os.listdir(os_root_path)
#  l_folders = [d for d in os.listdir(os_root_path) if os.path.isdir(d)]

  if len(l_folders) > l_history_days:
    shutil.rmtree(os_root_path + min(l_folders))
    with open(workdir + logfile, 'a') as update_log:
      update_log.write( '\n' + 'Deleted local folder: %s %s' % (min(l_folders), str(datetime.now())))
    l_folders.remove(min(l_folders))

  for l_folder in l_folders:
    if l_folder not in g_folders.keys():
      new_g_folder_id = create_folder(drive, l_folder, gdrive_root_folder_id)
      with open(workdir + logfile, 'a') as update_log:
        update_log.write( '\n' + 'Created new gdrive folder: %s %s' % (l_folder, str(datetime.now())))
      g_folders[l_folder] = new_g_folder_id

  newest_folder = max(g_folders.keys())
#  print(newest_folder)
  g_folder_item_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(g_folders[newest_folder])}).GetList()
  g_folder_item_names = []
  for item in g_folder_item_list:
    g_folder_item_names.append(item['title'])

  os_item_list = os.listdir(os_root_path + newest_folder)
#  print(os_item_list)
  for item in os_item_list:
    if item not in g_folder_item_names:
      new_file = drive.CreateFile({'title': item, "parents": [{"kind": "drive#fileLink", "id": g_folders[newest_folder]}]})
      file_path = os.path.join(os_root_path + newest_folder, item)
      new_file.SetContentFile(file_path)
      new_file.Upload()
      with open(workdir + logfile, 'a') as update_log:
        update_log.write( '\n' + 'Uploaded file to GD: %s %s' % (item, str(datetime.now())))


def create_folder(drive, folder_name, parent_folder_id):
    
  folder_metadata = {
      'title': folder_name,
      'mimeType': 'application/vnd.google-apps.folder',
      'parents': [{"kind": "drive#fileLink", "id": parent_folder_id}]
    }

  folder = drive.CreateFile(folder_metadata)
  folder.Upload()
  return folder['id']


def rotate_log():
  if os.path.exists(workdir + logfile)
    file_size = os.path.getsize(workdir + logfile)
  
    if file_size > 524288:
      os.rename(workdir + logfile, f"{workdir}{logfile}.{datetime.now():%Y%m%d}")


gauth = GoogleAuth()
gauth.LoadCredentialsFile(workdir + 'credentials.json')
if gauth.credentials is None:
  # Authenticate if they're not there
  # This is what solved the issues:
  gauth.GetFlow()
  gauth.flow.params.update({'access_type': 'offline'})
  gauth.flow.params.update({'approval_prompt': 'force'})

  gauth.LocalWebserverAuth()

elif gauth.access_token_expired:
  # Refresh them if expired
  gauth.Refresh()
else:
  # Initialize the saved creds
  gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile(workdir + 'credentials.json')

#gauth.LocalWebserverAuth()
upload_handler(gauth, os_root, gdrive_root_id)
rotate_log()
