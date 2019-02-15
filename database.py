#!/usr/bin/python3

import os
import simplejson as json
from pprint import pprint

''' safe_db_dump()
Safely save a database file
database: dict: A dictionary to be saved 
filename: str: A string filename, including '.json'
'''
def safe_db_dump(database, filename):
	try:
		json.dump(database, open(filename, 'w'))
	except IOError as e:
		print("Database unable to write to '" + filename + "'.")


''' safe_db_load()
Safely load a database
filename: str: A string filename, including '.json'
Return: 
	None: if the specified file doesn't exist or is a corrupted json database
	dict: the loaded json
'''
def safe_db_load(filename):
	database = None
	try:	
		if find_user(filename[:-5]):
			database = json.load(open(filename, 'r'))
	except IOError as e:
		print("Database unable to read '" + filename + "'.")
	finally:
		return database

''' find_user()
Finds if a user exists in the home directory
username: str: Some username
Return: 
	True: If the User has a database
	False: Otherwise
'''
def find_user(username):
	found = False
	for file in os.listdir("."):
		if file.endswith(".json") and username == file[:-5]:
			found = True
			break
	return found


''' backup_libraries()
Backs up the database into a folder called backups
'''
def backup_libraries():
	# Make sure the backup directory is there
	if 'backup' not in os.listdir(os.getcwd()):
		try:
			os.mkdir(os.getcwd() + '/backup')
		except OSError:
			print("Backup directory creation failed")

	# For Every File in the directory ending with json or db
	for file in os.listdir("."):
		if file.endswith(".json") or file.endswith(".db"):
			print("Backing up:", file)
			# Dump the file in the backup folder as a json file
			output = safe_db_load(file)
			safe_db_dump(output, os.path.join('backup', file))

	# Delete backed up users that no longer exist
	current_folder = []
	for file in os.listdir('.'):
		if file.endswith('.json') or file.endswith('.db'):
			current_folder.append(file)
	# Get all Unique items in the database
	unique = list(set(os.listdir("backup")) - set(current_folder))
	for u in unique:
		if os.path.exists(os.path.join('backup', u)):
			os.remove(os.path.join('backup', u))
		else:
			print("The file does not exist")
			pass

		
''' add_to_library()
Adds an Item to a users database
lib_item: dict_item: {Key, Value} dict item pair
user : str: A string of the username
Returns:
	True: Successfully added
	False: Otherwise
'''
def add_to_library(lib_item, user):
	exists = False
	for file in os.listdir("."):
		if file.endswith(".json") and file[:-5] == user:
			# Get the file information
			stuff = safe_db_load(file)
			if stuff is None:
				# Nothing loaded
				break
			stuff.update(lib_item)
			safe_db_dump(stuff, file)
			exists = True
	return exists


''' remove_from_library
Removes an item from a user's database
lib_key: dict_key: A dictionary key to be removed
user: str: The username of the owner of the database
Returns:
	True: Successfully removed
	False: Otherwise
'''
def remove_from_library(lib_key, user):
	for file in os.listdir("."):
		if file.endswith(".json") and user == file[:-5]:
			# print(file)
			stuff = safe_db_load(file)
			if lib_key in list(stuff.keys()):
				stuff.pop(lib_key)
				# print(stuff)
				safe_db_dump(stuff, file)
				return True
			else:
				print("Key not found")
				return False


''' add_user()
Adds a user to the Database
name: str: new Username to be added 
private_key: str: Self-explanitory
public_key: str: Self-explanitory
Returns:
	True: Adds a user to the database
	False: Otherwise
'''
def add_user(name, private_key, public_key):
	# Validate if the Username Exists
	if find_user(name):
		print("User already in database")
		print("Send error to the user")
		return False
	else:
		# Create Empty Database
		safe_db_dump({}, name + '.json')
		# Save the Private and Public Key under the Key Library
		user_keys = json.load(open('keys.db', 'r'))
		user_keys[name] = {"private": private_key, "public": public_key}
		json.dump(user_keys, open('keys.db', 'w'), indent = 2)
		return True


''' delete_user()
deletes a user to the Database
name: str: Username to be removed
Returns:
	True: Adds a user to the database
	False: Otherwise
'''
def delete_user(name):
	if os.path.exists(name + ".json"):
		os.remove(name + ".json")
		user_keys = json.load(open('keys.db', 'r'))
		user_keys.pop(name)
		json.dump(user_keys, open('keys.db', 'w'), indent = 2)
		return True
	else:
		print("The file does not exist")
		return False


''' ownership_change
item_key: str: Some Item key in the database of former owner
former_owner: str: username of the former owner of the item
future_owner: str: username of the new item recipient 
'''
def ownership_change(item_key, former_owner, future_owner):
	if not find_user(former_owner):
		print("User not in database")
		print("Send error to the user")
		return False
	elif not find_user(future_owner):
		print("User not in database")
		print("Send error to the user")
		return False
	else:
		# Get the two databses
		former_owner_db = safe_db_load(former_owner + '.json')
		future_owner_db = safe_db_load(future_owner + '.json')
		# Get the item and change the current owner
		ret_val = former_owner_db.pop(item_key)
		ret_val.update({'Current Owner': future_owner})
		future_owner_db.update({item_key: ret_val})
		# Save the databses
		safe_db_dump(former_owner_db, former_owner + '.json')
		safe_db_dump(future_owner_db, future_owner + '.json')
		return True


if __name__ == '__main__':
	backup_libraries()
