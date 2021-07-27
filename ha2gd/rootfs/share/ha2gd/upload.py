import os
from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth
from datetime import datetime

def upload(path, folder_id):

	""" Initial Authentication, local """
	gauth = GoogleAuth()
	gauth.LocalWebserverAuth()

	#Upload handler for folder path and Grdrive folder
	upload_handler(gauth, path, folder_id)

	with open('./update_log.txt', 'a') as update_log:
		update_log.write( '\n' + 'Synced with GDrive on ' + str(datetime.now()))

def upload_handler(gauth, os_root_path, gdrive_root_folder_id):
	# Google authentication 
	drive = GoogleDrive(gauth)
	dir_dict = {os_root_path: gdrive_root_folder_id}
	item_list = drive.ListFile({'q': "'{gdrive_root_folder_id}' in parents and trashed=false".format(gdrive_root_folder_id=gdrive_root_folder_id)}).GetList()
	titles = []
	for item in item_list:
		titles.append(item['title'])
	#print(type(item_list))

	#For each dir path starting from os_root_path by os.walk()
	for dirpath, dirnames, files in os.walk(os_root_path):
		print(dirpath, dirnames)
		#print(type(files))
		for file in files:
			#print(dir_dict, file, str('in ' + dirpath))
			if file not in titles:
				new_file = drive.CreateFile({'title': file, "parents": [{"kind": "drive#fileLink", "id": dir_dict[dirpath]}]})  # Create GoogleDriveFile instance to parentID.
				file_path = os.path.join(dirpath, file)
				new_file.SetContentFile(file_path) # Set content of the file from given string.
				print(new_file)
				new_file.Upload()
	for item in item_list:
		if item['title'] not in files:
			delete_item = drive.CreateFile({'id': item['id']})
			delete_item.Delete()
			print('Deleted title: %s, id: %s' % (item['title'], item['id']))


import csv
with open('folder_sync_registrer.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
    	upload(row[0], row[1])
    	




	

