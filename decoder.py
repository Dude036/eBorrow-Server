import re
from database import add_user, delete_user, retrieve_user
import simplejson as json
from errors import error_handler
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


def decoding(decode_buffer, transmit_buffer):
    while True:
        # Wait for the Queue to be filled. Recieves the Item and the Address
        item, addr = decode_buffer.get()
        logging.info("DECODER :: Starting Decoding process.")
        logging.info("DECODER :: Extracting User Information")

        # Split the item into Header and Packet
        match = re.match(r'([^ ]*) (.*)', item)
        if match is not None:
            header = match.group(1)
            packet = match.group(2)
        else:
            # Send Data to addr about the error
            logging.error("DECODER :: Dismissing: Invalid header format")
            logging.info("DECODER :: Sending Error to: %s" % addr)
            transmit_buffer.put([error_handler(1), addr])
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
            logging.error("DECODER :: Dismissing: Invalid header format")
            logging.info("DECODER :: Sending Error to: %s" % addr)
            transmit_buffer.put([error_handler(5), addr])
            continue

        # Set Username
        username = header[:delimit_pos]
        logging.debug("DECODER :: Username: %s : Connected" % username)
        # Remove the '@' and remove username from the header
        username = username[1:]
        header = header[delimit_pos:]

        # Get Packet ID number
        match = re.match(r':(\d+)', header)
        if match is not None:
            packet_id = int(match.group(1))
        else:
            # Send Data to addr about the error
            logging.error("DECODER :: Dismissing: No packet ID")
            logging.info("DECODER :: Sending Error to: %s" % addr)
            transmit_buffer.put([error_handler(2), addr])
            continue
        logging.debug('DECODER :: Processing Packet ID: %s' % packet_id)

        try:
            packet = json.loads(packet)
        except Exception as e:
            logging.error("DECODER :: Unable to decode JSON")
            transmit_buffer.put([error_handler(19), addr])
            continue

        if 0 <= packet_id < 100:
            interpretted(username, packet_id, packet, addr, transmit_buffer)
        elif 100 <= packet_id <= 199:
            piped(username, packet_id, packet, addr, transmit_buffer)
        else:
            logging.error("DECODER :: Unrecognized Packet ID")
            transmit_buffer.put([error_handler(2), addr])
            continue


def interpretted(username, packet_id, packet, addr, transmit_buffer):
    """
    Interpretted commands for the server. These range from the values 0 <= packey_id <= 99 in Networking.md
    :param username: Username of the subject
    :param packet_id: Packet identifier. Determines how the packet is handled
    :param packet: The actual packet dictionary
    :param addr: the connection object to return to
    :param transmit_buffer: This is the buffer to send information back to the user
    """
    if packet_id == 0:
        # New User Application
        # Not necessary to return anything for this function
        secret_key = packet['private']
        public_key = packet['public']
        if add_user(username, secret_key, public_key):
            transmit_buffer.put([error_handler(0), addr])
        else:
            transmit_buffer.put([error_handler(16), addr])

    elif packet_id == 1:
        # Delete User from Database
        # Not necessary to return anything for this function
        secret_key = packet['private']
        public_key = packet["public"]
        if packet["Delete"] == 1:
            if verify_key(username, secret_key, public=False):
                if verify_key(username, public_key, public=True):
                    if delete_user(username):
                        logging.debug("DECODER :: %s Deleted" % username)
                        transmit_buffer.put([error_handler(0), addr])
                    else:
                        logging.error("DECODER :: User not found in database")
                        transmit_buffer.put([error_handler(17), addr])
                else:
                    logging.error("DECODER :: Incorrect public Key")
                    transmit_buffer.put([error_handler(4), addr])
            else:
                logging.error("DECODER :: Incorrect private Key")
                transmit_buffer.put([error_handler(3), addr])
        else:
            logging.error("DECODER :: Unspecified Deletion command")
            transmit_buffer.put([error_handler(7), addr])

    elif packet_id == 2:
        # Remove an Item from database
        # Not necessary to return anything for this function
        if verify_key(username, packet['private'], public=False):
            user = retrieve_user(username)
            if user is None:
                logging.error("DECODER :: User not found in the database")
                transmit_buffer.put([error_handler(17), addr])
                return
            if isinstance(packet['Key'], str):
                if not user.remove_from_inventory(packet['Key']):
                    logging.error("DECODER :: Key not found in Library")
                    transmit_buffer.put([error_handler(8), addr])
                else:
                    transmit_buffer.put([error_handler(0), addr])
            elif isinstance(packet['Key'], list):
                for item in packet['Key']:
                    if not user.remove_from_inventory(item):
                        logging.error("DECODER :: Key not found in Library")
                        logging.error("DECODER :: Sending Error to:", addr)
                        transmit_buffer.put([error_handler(8), addr])
                    else:
                        transmit_buffer.put([error_handler(0), addr])
            else:
                logging.error("DECODER :: Value not acceptable data type")
                transmit_buffer.put([error_handler(20), addr])
            user.to_file()
        else:
            logging.error("DECODER :: Incorrect private Key")
            transmit_buffer.put([error_handler(3), addr])

    elif packet_id == 3:
        # Add an Item to database
        # Not necessary to return anything for this function
        if verify_key(username, packet['private'], public=False):
            packet.pop("private")
            user = retrieve_user(username)
            if user is None:
                logging.error("DECODER :: User not found in the database")
                transmit_buffer.put([error_handler(17), addr])
                return
            for key, value in packet.items():
                user.add_to_inventory({key: value})
            user.to_file()
            transmit_buffer.put([error_handler(0), addr])
        else:
            logging.error("DECODER :: Incorrect private Key")
            transmit_buffer.put([error_handler(3), addr])

    elif packet_id == 4:
        # Send all the Users' Inventory to the user
        # Instead of a Zero code, it'll return the asked for information.
        if verify_key(username, packet['public'], public=True):
            if packet['Library'] == 1:
                user = retrieve_user(username)
                if user is None:
                    logging.error("DECODER :: User not found in the database")
                    transmit_buffer.put([error_handler(17), addr])
                    return
                # Send back the user's data
                transmit_buffer.put(
                    [user.send_items(list(user.Inventory.keys())), addr])
            else:
                logging.error("DECODER :: Invalid Packet Format")
                transmit_buffer.put([error_handler(1), addr])
        else:
            logging.error("DECODER :: Incorrect private Key")
            transmit_buffer.put([error_handler(3), addr])

    elif packet_id == 5:
        # Send specific Data to the User
        # Instead of a Zero code, it'll return the asked for information.
        if verify_key(username, packet['public'], public=True):
            packet.pop('public')
            new_header = '@' + username + ':200'
            user = retrieve_user(username)
            if user is None:
                logging.error("DECODER :: User not found in the database")
                transmit_buffer.put([error_handler(17), addr])
                return
            new_packet = {}
            for key in list(packet.keys()):
                try:
                    new_packet[key] = user.Inventory[key]
                except KeyError:
                    logging.error("DECODER :: Unable to find specific Key")
                    transmit_buffer.put([error_handler(8), addr])
                    return
            # Send the user's data back
            transmit_buffer.put(
                [new_header + ' ' + json.dumps(new_packet), addr])
        else:
            logging.error("DECODER :: Incorrect private Key")
            transmit_buffer.put([error_handler(3), addr])
            return
    elif packet_id == 6:
        # Update Item Ownership
        # Returns an error Packet
        # Extract Owner's User object and verify private Key
        try:
            owner_key = packet.pop('private')
        except KeyError:
            logging.error("DECODER :: Missing Private Key from Json object")
            transmit_buffer.put([error_handler(7), addr])
            return

        if verify_key(username, owner_key, public=False):
            owner = retrieve_user(username)
            if owner is None:
                logging.error("DECODER :: User not found in the database")
                transmit_buffer.put([error_handler(17), addr])
                return
            # Extract Borrower's User object and verify public Key
            try:
                borrower_key = packet.pop('public')
                borrower_username = packet.pop('New Owner')
            except KeyError:
                logging.error(
                    "DECODER :: Missing public Key or New Owner from Json object")
                transmit_buffer.put([error_handler(7), addr])
                return
            if verify_key(borrower_username, borrower_key, public=True):
                borrower = retrieve_user(username)
                if borrower is None:
                    logging.error("DECODER :: User not found in the database")
                    transmit_buffer.put([error_handler(17), addr])
                    return
                # Get the Hash and Schedule
                try:
                    schedule = packet.pop('Schedule')
                    item_key = packet.pop('Key')
                except KeyError:
                    logging.error(
                        "DECODER :: Missing Schedule or key from Json object")
                    transmit_buffer.put([error_handler(7), addr])
                    return
                ret_code = owner.ownership_change(borrower, item_key, schedule)
                transmit_buffer.put([error_handler(ret_code), addr])
            else:
                logging.error("DECODER :: Incorrect Friend public Key")
                transmit_buffer.put([error_handler(3), addr])
                return
        else:
            logging.error("DECODER :: Incorrect User private Key")
            transmit_buffer.put([error_handler(3), addr])
            return
    elif packet_id == 7:
        # Send Messages to the User
        # Requires a clap back
        try:
            user_key = packet.pop("private")
        except KeyError:
            logging.error("DECODER :: Missing private key from Json object")
            transmit_buffer.put([error_handler(7), addr])
            return
        if verify_key(username, user_key, public=False):
            user = retrieve_user(username)
            transmit_buffer.put([user.send_messages(), addr])
        else:
            logging.error("DECODER :: Incorrect User private Key")
            transmit_buffer.put([error_handler(3), addr])
            return
    elif packet_id == 8:
        # Send Exchanges to the User
        # Currently under development
        pass
    elif packet_id == 9:
        # Delete all the User's messages
        # Returns an Error Packet
        try:
            user_key = packet.pop("private")
        except KeyError:
            logging.error("DECODER :: Missing private key from Json object")
            transmit_buffer.put([error_handler(7), addr])
            return
        if verify_key(username, user_key, public=False):
            logging.info("DECODER :: Deleted " + username +
                         "'s messages per request")
            user = retrieve_user(username)
            user.clear_messages()
            transmit_buffer.put([error_handler(0), addr])
        else:
            logging.error("DECODER :: Incorrect User private Key")
            transmit_buffer.put([error_handler(3), addr])
            return
    elif packet_id == 10:
        # Send all pending friend requests
        # Returns packet 204 or an Error Packet
        try:
            user_key = packet.pop("private")
        except KeyError:
            logging.error("DECODER :: Missing private key from Json object")
            transmit_buffer.put([error_handler(7), addr])
            return
        if verify_key(username, user_key, public=False):
            logging.info("DECODER :: ")
            user = retrieve_user(username)
            new_header = '@' + username + ':204'
            transmit_buffer.put([new_header + ' ' + user.send_pending_friends(), addr])
        else:
            logging.error("DECODER :: Incorrect User private Key")
            transmit_buffer.put([error_handler(3), addr])
            return
    elif packet_id == 11:
        # Send all pending friend requests
        # Returns packet 204 or an Error Packet
        try:
            user_key = packet.pop("private")
        except KeyError:
            logging.error("DECODER :: Missing private key from Json object")
            transmit_buffer.put([error_handler(7), addr])
            return
        if verify_key(username, user_key, public=False):
            logging.info("DECODER :: ")
            user = retrieve_user(username)
            new_header = '@' + username + ':203'
            transmit_buffer.put([new_header + ' ' + user.send_pending_exchanges(), addr])
        else:
            logging.error("DECODER :: Incorrect User private Key")
            transmit_buffer.put([error_handler(3), addr])
            return

    logging.debug("DECODER :: Successfully decoded id: " + str(packet_id))


def piped(username, packet_id, packet, addr, transmit_buffer):
    """
    Piped commands. These are currently still being disputed on how they should be implimented
    :param username: Username of the subject
    :param packet_id: Packet identifier. Determines how the packet is handled
    :param packet: The actual packet dictionary
    :param addr: the connection object to return to
    :param transmit_buffer: This is the buffer to send information back to the user
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
