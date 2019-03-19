#!/usr/bin/python3
import socket
import simplejson as json
import re
import time
from numpy.random import randint, choice
from OpenSSL import crypto

HOST = '127.0.0.1'			# Local Host Testing
# HOST = '3.90.142.252'			# AWS Testing
PORT = 41111				# The port used by the server

Items = json.load(open("db.json", 'r'))


def dictionary_to_byte_string(dictionary):
    return json.dumps(dictionary)


def test_send_buffer(send_buffer, end_byte=b'\x7F\xFF\x7F\xFF'):
    for thing in send_buffer:
        # Send Buffer
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((HOST, PORT))
            s.sendall(thing.encode() + end_byte)
            s.close()
        print("Sent:", re.match(r'(\@[\S]+)\:(\d+)', thing).groups())
        time.sleep(.2)


def test_create_new_user(username, private_key, public_key):
    header = '@' + username + ':0'
    packet = "{\"private\":\"" + private_key.decode() + "\", \"public\":\"" + \
        public_key.decode() + "\"}"
    test_send_buffer([header + ' ' + packet])


def test_delete_new_user(username, private_key, public_key):
    header = '@' + username + ':1'
    packet = "{\"Delete\":1, \"public\":\"" + public_key.decode() + "\", \"private\":\"" + private_key.decode() + "\"}"
    test_send_buffer([header + ' ' + packet])


def test_delete_db_item(username, private_key):
    send_buffer = []

    header = '@' + username + ':2'
    for key, value in Items.items():
        packet = '{"Key":"' + key + '", "private": "' + private_key.decode() + '"}'
        send_buffer.append(header + ' ' + packet)

    test_send_buffer(send_buffer)


def test_add_db_item(username, private_key):
    send_buffer = []

    header = '@' + username + ':3'
    for key, value in Items.items():
        packet = '{"' + key + '":' + dictionary_to_byte_string(value) + ', "private": "' + private_key.decode() + '"}'
        send_buffer.append(header + ' ' + packet)

    test_send_buffer(send_buffer)


def test_add_many_db_item(username, private_key):
    header = '@' + username + ':3'
    packet = '{'
    for key, value in Items.items():
        packet += '"' + key + '":' + dictionary_to_byte_string(value) + ', '
    packet += '"private": "' + private_key.decode() + '"}'

    test_send_buffer([header + ' ' + packet])


def test_recieve_all_data(username, public_key):
    header = '@' + username + ':4'
    packet = '{"public":"' + public_key.decode() + '"}'
    test_send_buffer([header + ' ' + packet])


def test_recieve_some_data(username, public_key):
    header = '@' + username + ':4'
    packet = ''
    for key, value in Items.items():
        packet += '"' + key + '": 1, '
    packet += '"public":"' + public_key.decode() + '"}'
    test_send_buffer([header + ' ' + packet])


def test_ownership_change(username, private_key, item, friend_username, friend_public):
    # TODO: Impliment Test Here
    header = '@' + username + ':6' + private_key.decode()
    packet = '<' + list(item.keys())[0] + '>{"New Owner": "' + \
        friend_username + '", "Public Key": "' + friend_public.decode() + '"}'
    test_send_buffer([header + ' ' + packet])


def generate_private_public_keypair():
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    private_key = ''.join(crypto.dump_privatekey(
        crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()
    public_key = ''.join(crypto.dump_publickey(
        crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()

    return private_key, public_key


if __name__ == '__main__':
    from time import sleep
    print("Generating Key Pairs")
    private_key_1, public_key_1 = generate_private_public_keypair()
    private_key_2, public_key_2 = generate_private_public_keypair()

    test_username_1 = 'username_1'
    test_username_2 = 'username_2'

    # Make Both Users
    test_create_new_user(test_username_1, private_key_1, public_key_1)
    # sleep(1)
    test_create_new_user(test_username_2, private_key_2, public_key_2)
    input(format("Press Enter to Continue", '^100s'))

    # Add all items to user 1
    test_add_db_item(test_username_1, private_key_1)
    input(format("Press Enter to Continue", '^100s'))

    # Remove Items
    test_delete_db_item(test_username_1, private_key_1)
    input(format("Press Enter to Continue", '^100s'))

    test_delete_new_user(test_username_1, private_key_1, public_key_1)
    sleep(.2)
    test_delete_new_user(test_username_2, private_key_2, public_key_2)
