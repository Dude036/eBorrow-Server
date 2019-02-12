#!/usr/bin/python3

import os
import simplejson as json

def backup_libraries():
	# Make sure the backup directory is there
	if 'backup' not in os.listdir(os.getcwd()):
		try:
			os.mkdir(os.getcwd() + '/backup')
		except OSError:
			print("Backup directory creation failed")

	# For Every File in the directory ending with json
	for file in os.listdir("."):
		if file.endswith(".json"):
			# Dump the file in the backup folder as a json file
			json.dump(json.load(open(file, 'r')), open(os.path.join('backup', file), 'w'))

	# Delete backed up users that no longer exist
	current_folder = []
	for file in os.listdir('.'):
		if file.endswith('.json'):
			current_folder.append(file)
	# Get all Unique items in the database
	unique = list(set(os.listdir("backup")) - set(current_folder))
	for u in unique:
		if os.path.exists(os.path.join('backup', u)):
			os.remove(os.path.join('backup', u))
		else:
			print("The file does not exist")
			pass


def add_to_library(lib_item, user):
	for file in os.listdir("."):
		if file.endswith(".json") and user == file[:-5]:
			# Get the file information
			stuff = json.load(open(file, 'r'))
			# print(lib_item.keys(), lib_item.values())
			stuff.update(lib_item)
			json.dump(stuff, open(file, 'w'))


def remove_from_library(lib_key, user):
	for file in os.listdir("."):
		if file.endswith(".json") and user == file[:-5]:
			stuff = json.load(open(file, 'r'))
			stuff.pop(lib_key)
			# print(stuff)
			json.dump(stuff, open(file, 'w'))


def add_user(name):
	json.dump({}, open(name + '.json', 'w'))


def delete_user(name):
	if os.path.exists(name + ".json"):
		os.remove(name + ".json")
	else:
		print("The file does not exist")
		pass


if __name__ == '__main__':
	add_to_library({"temp":1}, 'test')
	remove_from_library("temp", 'test')
	add_user('temp_user')
	backup_libraries()
	delete_user('temp_user')
	backup_libraries()
