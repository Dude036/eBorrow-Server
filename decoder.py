import re
from database import add_user, delete_user, ownership_change, retrieve_user
import simplejson as json
import hashlib
import logging


def verify_key(username, key, public=True):
    """
    A function to determine if a user's key is valid
    :param username: Username's keys
    :param key: the actual key value to be tested
    :param public: bool: True = Test public Key
                        False = Test private Key
    :return: bool: True = Valid key
                  False = Invalid Key
    """
    all_keys = json.load(open('keys.db'))
    if username not in list(all_keys.keys()):
        return False
    elif public:
        return all_keys[username]['public'] == hashlib.md5(key.encode()).hexdigest()
    else:
        return all_keys[username]['private'] == hashlib.md5(key.encode()).hexdigest()


def decoding(decode_buffer, error_buffer, transmit_buffer):
    while True:
        # Wait for the Queue to be filled. Recieves the Item and the Address
        item, addr = decode_buffer.get()
        logging.info("Starting Decoding process.")
        logging.info("Extracting User Information")

        # Split the item into Header and Packet
        header = None
        packet = None
        match = re.match(r'([^ ]*) (.*)', item)
        if match is not None:
            header = match.group(1)
            packet = match.group(2)
        else:
            # Send Data to addr about the error
            logging.error("Dismissing: Invalid header format")
            logging.info("Sending Error to: %s" % addr)
            error_buffer.put([1, addr])
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
            logging.error("Dismissing: Invalid header format")
            logging.info("Sending Error to: %s" % addr)
            error_buffer.put([5, addr])
            continue

        # Set Username
        username = header[:delimit_pos]
        logging.debug("Username: %s : Connected" % username)
        # Remove the '@' and remove username from the header
        username = username[1:]
        header = header[delimit_pos:]

        # Get Packet ID number
        match = re.match(r':(\d+)', header)
        if match is not None:
            packet_id = int(match.group(1))
        else:
            # Send Data to addr about the error
            logging.error("Dismissing: No packet ID")
            logging.info("Sending Error to: %s" % addr)
            error_buffer.put([2, addr])
            continue
        logging.debug('Processing Packet ID: %s' % packet_id)

        try:
            packet = json.loads(packet)
        except Exception:
            logging.error("unable to decode JSON")
            error_buffer.put([19, addr])
            continue

        if 0 <= packet_id < 100:
            interpretted(username, packet_id, packet, addr, error_buffer, transmit_buffer)
        elif 100 <= packet_id <= 199:
            piped(username, packet_id, packet, addr, error_buffer, transmit_buffer)
        else:
            logging.error("Unrecognized Packet ID")
            error_buffer.put([2, addr])
            continue


def interpretted(username, packet_id, packet, addr, error_buffer, transmit_buffer):
    """
    Interpretted commands for the server. These range from the values 0 <= packey_id <= 99 in Networking.md
    :param username: Username of the subject
    :param packet_id: Packet identifier. Determines how the packet is handled
    :param packet: The actual packet dictionary
    :param addr: the IP address to return to
    :param error_buffer:
    :param transmit_buffer:
    """
    if packet_id == 0:
        # New User Application
        secret_key = packet['private']
        public_key = packet['public']
        add_user(username, secret_key, public_key)

    elif packet_id == 1:
        # Delete User from Database
        secret_key = packet['private']
        public_key = packet["public"]
        if packet["Delete"] == 1:
            if verify_key(username, secret_key, public=False):
                if verify_key(username, public_key, public=True):
                    if delete_user(username):
                        logging.debug("%s Deleted" % username)
                    else:
                        logging.error("User not found in database")
                        error_buffer.put([17, addr])
                else:
                    logging.error("Incorrect public Key")
                    error_buffer.put([4, addr])
            else:
                logging.error("Incorrect private Key")
                error_buffer.put([3, addr])
        else:
            logging.error("Unspecified Deletion command")
            error_buffer.put([7, addr])

    elif packet_id == 2:
        # Remove an Item from database
        if verify_key(username, packet['private'], public=False):
            user = retrieve_user(username)
            if user is None:
                logging.error("User not found in the database")
                error_buffer.put([17, addr])
                return
            if isinstance(packet['Key'], str):
                if not user.remove_from_inventory(packet['Key']):
                    logging.error("Key not found in Library")
                    logging.error("Sending Error to:", addr)
                    error_buffer.put([8, addr])
            elif isinstance(packet['Key'], list):
                for item in packet['Key']:
                    if not user.remove_from_inventory(item):
                        logging.error("Key not found in Library")
                        logging.error("Sending Error to:", addr)
                        error_buffer.put([8, addr])
            else:
                logging.error("Value not acceptable data type")
                error_buffer.put([20, addr])
            user.to_file()
        else:
            logging.error("Incorrect private Key")
            error_buffer.put([3, addr])

    elif packet_id == 3:
        # Add an Item to database
        if verify_key(username, packet['private'], public=False):
            packet.pop("private")
            user = retrieve_user(username)
            if user is None:
                logging.error("User not found in the database")
                error_buffer.put([17, addr])
                return
            for key, value in packet.items():
                user.add_to_inventory({key: value})
            user.to_file()
        else:
            logging.error("Incorrect private Key")
            error_buffer.put([3, addr])

    elif packet_id == 4:
        # Send all the Users' Data to the user

        if verify_key(username, packet['public'], public=True):
            if packet['Library'] == 1:
                user = retrieve_user(username)
                if user is None:
                    logging.error("User not found in the database")
                    error_buffer.put([17, addr])
                    return
                transmit_buffer.put([user.send_items(list(user.Inventory.keys())), addr])
            else:
                logging.error("Invalid Packet Format")
                error_buffer.put([1, addr])
        else:
            prilogging.errornt("Incorrect private Key")
            error_buffer.put([3, addr])

    elif packet_id == 5:
        # send specific Data to the User
        if verify_key(username, packet['public'], public=True):
            packet.pop('Publid')
            new_header = '@' + username + ':200'
            user = retrieve_user(username)
            if user is None:
                logging.error("User not found in the database")
                error_buffer.put([17, addr])
                return
            new_packet = {}
            for key in list(packet.keys()):
                try:
                    new_packet[key] = user.Inventory[key]
                except KeyError:
                    logging.error("Unable to find specific Key")
                    error_buffer.put([8, addr])

            transmit_buffer.put([new_header + ' ' + json.dumps(new_packet), addr])
        else:
            logging.error("Incorrect private Key")
            error_buffer.put([3, addr])
    elif packet_id == 6:
        # Update Item Ownership
        # Currently under development
        pass


def piped(username, packet_id, packet, addr, error_buffer, transmit_buffer):
    """
    Piped commands. These are currently still being disputed on how they should be implimented
    :param username: Username of the subject
    :param packet_id: Packet identifier. Determines how the packet is handled
    :param packet: The actual packet dictionary
    :param addr: the IP address to return to
    :param error_buffer:
    :param transmit_buffer:
    """
    if packet_id == 100:
        # Acquisition Request
        # Still Developing process
        pass

    elif packet_id == 101:
        # Friend Request
        pass

    elif packet_id == 102:
        # Add Friend
        pass

    elif packet_id == 103:
        # Delete Request
        pass
