#!/usr/bin/python3

import os
import simplejson as json


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
    backup_interval = 10
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
            print("Backup directory creation failed")

    # For Every File in the directory ending with json or db
    for file in os.listdir("."):
        if file.endswith(".json") or file.endswith(".db"):
            print("Backing up:", file)
            # Dump the file in the backup folder as a json file
            output = safe_db_load(file)
            safe_db_dump(output, os.path.join('backup', file))


def add_to_library(lib_item, user):
    """ add_to_library()
    Adds an Item to a users database
    :param lib_item: dict_item: {Key, Value} dict item pair
    :param user : str: A string of the username
    :return True: Successfully added
            False: Otherwise
    """
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


def remove_from_library(lib_key, user):
    """ remove_from_library
    Removes an item from a user's database
    :param lib_key: dict_key: A dictionary key to be removed
    :param user: str: The username of the owner of the database
    :return True: Successfully removed
            False: Otherwise
    """
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
        print("User already in database")
        print("Send error to the user")
        return False
    else:
        # Create Empty Database
        safe_db_dump({}, name + '.json')
        # Save the Private and Public Key under the Key Library
        user_keys = json.load(open('keys.db', 'r'))
        user_keys[name] = {"private": private_key, "public": public_key}
        json.dump(user_keys, open('keys.db', 'w'), indent=2)
        return True


def delete_user(name):
    """ delete_user()
    deletes a user to the Database
    name: str: Username to be removed
    Returns:
            True: Adds a user to the database
            False: Otherwise
    """
    if os.path.exists(name + ".json"):
        os.remove(name + ".json")
        user_keys = json.load(open('keys.db', 'r'))
        user_keys.pop(name)
        json.dump(user_keys, open('keys.db', 'w'), indent=2)
        return True
    else:
        print("The file does not exist")
        return False


# TODO: Add this to the User Class
def ownership_change(item_key, former_owner, future_owner):
    """ ownership_change
    item_key: str: Some Item key in the database of former owner
    former_owner: str: username of the former owner of the item
    future_owner: str: username of the new item recipient 
    """
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
