#!/usr/bin/python3

import os
import simplejson as json
from User import User
import hashlib
import logging


def retrieve_user(username):
    """
    A function to return a database from a username
    :param username: a string of a username to retrieve
    :return: If user exists in the database:
                A user object
             Else:
                None
    """
    database = None
    if username.endswith(".json"):
        username = username[:-5]

    try:
        if find_user(username):
            file = os.path.join('db', username + '.json')
            database = User(username, json_data=json.load(open(file, 'r')))
    except IOError as e:
        logging.error("Database unable to read '" + username + "'.")
    finally:
        return database


def find_user(username):
    """
    Finds if a user exists in the Key database
    :param username: str: Some username
    :return True: If the User has a database
            False: Otherwise
    """
    key_lib = json.load(open('keys.db', 'r'))
    return True if username in list(key_lib.keys()) else False


def auto_backup():
    """ auto_backup()
    Automatically calls backup at some specified interval. Currently, setup to check every minute and backup every 10 minutes
    """
    from time import sleep
    from datetime import datetime
    backup_interval = 2
    # Make sure the backup directory and the db directory exist
    if 'backup' not in os.listdir(os.getcwd()):
        try:
            os.mkdir(os.getcwd() + '/backup')
        except OSError:
            logging.error("Backup directory creation failed")
    if 'db' not in os.listdir(os.getcwd()):
        try:
            os.mkdir(os.getcwd() + '/db')
        except OSError:
            logging.error("Backup directory creation failed")

    while True:
        if datetime.utcnow().minute % backup_interval == 0:
            backup_libraries()
        sleep(60)


def backup_libraries():
    """ backup_libraries()
    Backs up the database into a folder called backups
    """
    # Make sure the backup directory is there
    if 'backup' not in os.listdir(os.getcwd()):
        try:
            os.mkdir(os.getcwd() + '/backup')
        except OSError:
            logging.error("Backup directory creation failed")

    # For Every File in the database directory ending with json
    for file in os.listdir("db"):
        if file.endswith(".json"):
            logging.info("Backing up: %s" % file)
            # Dump the file in the backup folder as a json file
            class_output = retrieve_user(file)
            if class_output is not None:
                class_output.to_backup()


def add_user(name, private_key, public_key):
    """ add_user()
    Adds a user to the Database
    :param name: str: new Username to be added
    :param private_key: str: Self-explanitory
    :param public_key: str: Self-explanitory
    :return True: Adds a user to the database
            False: Otherwise
    """
    # Validate if the Username Exists
    if find_user(name):
        logging.error("User already in database")
        logging.info("Send error to the user")
        return False
    else:
        # Create and store Empty User Item
        user = User(name)
        user.to_file()
        # Save the Private and Public Key under the Key Library
        user_keys = json.load(open('keys.db', 'r'))
        user_keys[name] = {
            "private": hashlib.md5(private_key.encode()).hexdigest(),
            "public": hashlib.md5(public_key.encode()).hexdigest()
        }
        json.dump(user_keys, open('keys.db', 'w'), indent=2)
        return True


def delete_user(name):
    """ delete_user()
    deletes a user from the Database
    name: str: Username to be removed
    Returns:
            True: Adds a user to the database
            False: Otherwise
    """
    # Check if the file exists
    if os.path.exists(os.path.join('db', name + ".json")):
        # Try and remove
        os.remove(os.path.join('db', name + ".json"))

        # Remove from the Key DB
        user_keys = json.load(open('keys.db', 'r'))
        user_keys.pop(name)
        json.dump(user_keys, open('keys.db', 'w'), indent=2)
        return True
    else:
        logging.info("The file does not exist")
        return False


if __name__ == '__main__':
    backup_libraries()
