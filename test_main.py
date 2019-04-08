#!/usr/bin/python3
import socket
import simplejson as json
import re
import time
from numpy.random import randint, choice
from OpenSSL import crypto
import unittest
from time import sleep
import os
from networking import recv_until


def generate_private_public_keypair():
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    private_key = ''.join(crypto.dump_privatekey(
        crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()
    public_key = ''.join(crypto.dump_publickey(
        crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()

    return private_key, public_key


class NetworkingTest(unittest.TestCase):
    """docstring for NetworkingTest"""
    def __init__(self):
        super(NetworkingTest, self).__init__()
        self.HOST = '127.0.0.1'           # Local Host Testing
        # self.HOST = '24.11.13.224'          # Home Network
        self.PORT = 41111                   # The port used by the server
        self.Remote = False                  # This should be false if you're testing on a local network

        self.Items = json.load(open("db.json", 'r'))
        print("Generating Key Pairs")

        self.private_key_1, self.public_key_1 = generate_private_public_keypair()
        self.private_key_2, self.public_key_2 = generate_private_public_keypair()

        self.test_username_1 = 'username_1'
        self.test_username_2 = 'username_2'

    @staticmethod
    def dictionary_to_byte_string(dictionary):
        return json.dumps(dictionary)

    def send_buffer(self, send_buffer, end_byte=b'\x7F\xFF\x7F\xFF'):
        for thing in send_buffer:
            # Send Buffer
            s = socket.create_connection((self.HOST, self.PORT))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.sendall(thing.encode() + end_byte)
            print("Sent:", re.match(r'(\@[\S]+)\:(\d+)', thing).groups())
            # Wair for server clap back
            time.sleep(1)
            data = recv_until(s)
            s.close()
        return data

    def test_create_new_user(self):
        header = '@' + self.test_username_1 + ':0'
        packet = "{\"private\":\"" + self.private_key_1.decode() + "\", \"public\":\"" + self.public_key_1.decode() + "\"}"
        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)
        if self.Remote:
            pass
        else:
            time.sleep(1)
            self.assertTrue(os.path.exists(os.path.join('db', 'username_1.json')))

        header = '@' + self.test_username_2 + ':0'
        packet = "{\"private\":\"" + self.private_key_2.decode() + "\", \"public\":\"" + self.public_key_2.decode() + "\"}"
        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)
        if self.Remote:
            pass
        else:
            time.sleep(1)
            self.assertTrue(os.path.exists(os.path.join('db', 'username_2.json')))

    def test_delete_new_user(self):
        header = '@' + self.test_username_1 + ':1'
        packet = "{\"Delete\":1, \"public\":\"" + self.public_key_1.decode() + "\", \"private\":\"" + self.private_key_1.decode() + "\"}"
        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)
        if self.Remote:
            pass
        else:
            time.sleep(1)
            self.assertFalse(os.path.exists(os.path.join('db', 'username_1.json')))

        header = '@' + self.test_username_2 + ':1'
        packet = "{\"Delete\":1, \"public\":\"" + self.public_key_2.decode() + "\", \"private\":\"" + self.private_key_2.decode() + "\"}"
        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)
        if self.Remote:
            pass
        else:
            time.sleep(1)
            self.assertFalse(os.path.exists(os.path.join('db', 'username_2.json')))

    def test_delete_db_item(self):
        send_buffer = []

        header = '@' + self.test_username_1 + ':2'
        for key, value in self.Items.items():
            packet = '{"Key":"' + key + '", "private": "' + self.private_key_1.decode() + '"}'
            send_buffer.append(header + ' ' + packet)

        data_recv = self.send_buffer(send_buffer)
        self.assertIn('!Error:0', data_recv)

    def test_delete_many_db_item(self):
        header = '@' + self.test_username_1 + ':2'
        packet = '{"Key":['
        for key, value in self.Items.items():
            packet += '"' + key + '",'
        # Remove the last comma from the packet
        packet = packet[:-1]
        packet += '], "private": "' + self.private_key_1.decode() + '"}'

        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)

    def test_add_db_item(self):
        send_buffer = []

        header = '@' + self.test_username_1 + ':3'
        for key, value in self.Items.items():
            packet = '{"' + key + '":' + self.dictionary_to_byte_string(value) + ', "private": "' + self.private_key_1.decode() + '"}'
            send_buffer.append(header + ' ' + packet)

        data_recv = self.send_buffer(send_buffer)
        self.assertIn('!Error:0', data_recv)

    def test_add_many_db_item(self):
        header = '@' + self.test_username_1 + ':3'
        packet = '{'
        for key, value in self.Items.items():
            packet += '"' + key + '":' + self.dictionary_to_byte_string(value) + ', '
        packet += '"private": "' + self.private_key_1.decode() + '"}'

        data_recv = self.send_buffer([header + ' ' + packet])
        self.assertIn('!Error:0', data_recv)

    def test_recieve_all_data(self):
        header = '@' + self.test_username_1 + ':4'
        packet = '{"public":"' + self.public_key_1.decode() + '"}'
        self.send_buffer([header + ' ' + packet])

    def test_recieve_some_data(self):
        header = '@' + self.test_username_1 + ':5'
        packet = {}
        keys = []
        for key in list(self.Items.keys())[:5]:
            packet[key] = 1
            keys.append(key)
        packet["public"] = self.public_key_1.decode()
        data_recv = self.send_buffer([header + ' ' + self.dictionary_to_byte_string(packet)])
        for k in keys:
            self.assertIn(k, data_recv)

    def test_ownership_change(self):
        # TODO: Impliment Test Here
        pass

    def main(self):
        # Make Both Users
        self.test_create_new_user()
        input(format("Press Enter to Continue", '^100s'))

        # Add all items to user 1
        self.test_add_many_db_item()
        input(format("Press Enter to Continue", '^100s'))

        # Verify they Exist in username_1's inventory
        self.test_recieve_some_data()
        input(format("Press Enter to Continue", '^100s'))

        # Remove Items
        self.test_delete_many_db_item()
        input(format("Press Enter to Continue", '^100s'))

        self.test_delete_new_user()


if __name__ == '__main__':
    TestingCases = NetworkingTest()
    TestingCases.main()

