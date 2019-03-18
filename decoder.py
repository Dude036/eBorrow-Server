from networking import decode_buffer
import re
from database import add_to_library, remove_from_library, add_user, delete_user, ownership_change
from errors import error_buffer
import simplejson as json


def read_key(item):
    delimit = -1
    for pos in range(len(item)-1):
        if item[pos] == '|' and item[pos+1] == '|':
            delimit = pos
            break
    return delimit


def verify_key(username, key, public=True):
    all_keys = json.load(open('keys.db'))
    if username not in list(all_keys.keys()):
        return False
    elif public:
        return all_keys[username]['public'] == key
    else:
        return all_keys[username]['private'] == key


def decoding():
    while True:
        # Wait for the Queue to be filled. Recieves the Item and the Address
        item, addr = decode_buffer.get()
        print("Starting Decoding process.")
        print("Extracting User Information")

        # Split the item into Header and Packet
        header = None
        packet = None
        match = re.match(r'([^ ]*) (.*)', item)
        if match is not None:
            header = match.group(1)
            packet = match.group(2)
        else:
            # Send Data to addr about the error
            print("Dismissing: Invalid header format")
            print("Sending Error to:", addr)
            # error_buffer.put([])
            continue

        # Every command starts with the Username, It's easy to get that out of the way
        # Extract Username
        delimit_pos = 0
        for point in header:
            if point == ':':
                break
            else:
                delimit_pos += 1

        # No Delimiter = Error in the Header
        if delimit_pos == 0:
            # Send Data to addr about the error
            print("Dismissing: Invalid header format")
            print("Sending Error to:", addr)
            continue

        # Set Username
        username = header[:delimit_pos]
        print("Username:", username)
        # Remove the '@' and remove username from the header
        username = username[1:]
        header = header[delimit_pos:]

        # Get Packet ID number
        match = re.match(r':(\d+):', header)
        if match is not None:
            packet_id = int(match.group(1))
        else:
            # Send Data to addr about the error
            print("Dismissing: No packet ID")
            print("Sending Error to:", addr)
            continue
        print('Processing Packet ID:', packet_id)
        ''' --- Interpretted Commands --- '''
        if packet_id == 0:
            # New User Application
            packet = json.loads(packet)
            secret_key = packet['private']
            public_key = packet['public']
            add_user(username, secret_key, public_key)
        elif packet_id == 1:
            # Delete User from Database
            packet = json.loads(packet)
            secret_key = header[3:]
            public_key = packet["public"]
            if packet["Delete"] == 1:
                if verify_key(username, secret_key, public=False):
                    if verify_key(username, public_key, public=True):
                        delete_user(username)
                    else:
                        print("Incorrect Public Key")
                else:
                    print("Incorrect Private Key")
            else:
                print("Unspecified Deletion command")

        elif packet_id == 2:
            # Remove an Item from database
            if verify_key(username, header[3:], public=False):
                sha_key = packet[1:33]
                res = remove_from_library(sha_key, username)
                if not res:
                    print("Key not found in Library")
                    print("Sending Error to:", addr)
                    continue
            else:
                print("Dismissing: incorrect key Value pair")
                print("Sending Error to:", addr)
                continue

        elif packet_id == 3:
            # Add an Item to database
            # print(header)
            if verify_key(username, header[3:], public=False):
                # add_to_library(username, key)
                sha_key = packet[1:33]
                value = packet[34:]
                add_to_library({sha_key: json.loads(value)}, username)
            else:
                print("Dismissing: incorrect key Value pair")
                print("Sending Error to:", addr)
                continue

        elif packet_id == 4:
            # Send all the Users' Data to the user
            pass
        elif packet_id == 5:
            # send specific Data to the User
            pass
        elif packet_id == 6:
            # Update Item Ownership
            if verify_key(username, header[3:], public=False):
                item_key = packet[1:33]
                json_data = json.loads(packet[34:])
                if verify_key(json_data['New Owner'], json_data['Public Key'], public=True):
                    ownership_change(item_key, username,
                                     json_data['New Owner'])
                else:
                    print("Invalid Public Key")
            else:
                print('Invalid Private key')
        # ''' --- PIPED COMMADS --- '''
        elif packet_id == 100:
            # the database
            pass
        elif packet_id == 101:
            # Remove an Item from the database
            pass
        else:
            # Unrecognised Packet ID
            print("Dismissing: Unrecognised packet ID")
            print("Sending Error to:", addr)
            continue
