#!/usr/bin/python3
import socket
import simplejson as json
from pprint import pprint
import re
import time
from Crypto.PublicKey import RSA
from OpenSSL import crypto

HOST = '127.0.0.1'			# Local Host Testing
PORT = 41111				# The port used by the server

Items = json.load(open("db.json", 'r'))


def dictionary_to_byte_string(dictionary):
	return json.dumps(dictionary)


def test_add_db_item(username, private_key):
	send_buffer = []

	header = '@' + username + ':3:' + private_key.decode() + ' <{}>'
	for key, value in Items.items():

		send_buffer.append(header.format(key) + dictionary_to_byte_string(value))

	test_send_buffer(send_buffer)


def test_delete_db_item(username, private_key):
	send_buffer = []

	header = '@' + username + ':2:' + private_key.decode() + ' <{}>'
	for key, value in Items.items():

		send_buffer.append(header.format(key))

	test_send_buffer(send_buffer)



def test_send_buffer(send_buffer):
	for thing in send_buffer:
		# Send Buffer
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.connect((HOST, PORT))
			s.sendall(thing.encode())
		print("Sent:", re.match(r'(\@username:\d+:).*(<[a-zA-Z0-9]{32}>)', thing).groups())
		time.sleep(.2)


def generate_private_public_keypair():
	k = crypto.PKey()
	k.generate_key(crypto.TYPE_RSA, 4096)
	private_key = ''.join(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()
	public_key = ''.join(crypto.dump_publickey(crypto.FILETYPE_PEM, k).decode().split('\n')[1:-2]).encode()

	# Option 1
	with open('private.pem', 'wb') as outf:
		outf.write(private_key)
	with open('public.pem', 'wb') as outf:
		outf.write(public_key)
	# Option 2
	# with open('private.pem2', 'wb') as outf:
	# 	outf.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
	# with open('public.pem2', 'wb') as outf:
	# 	outf.write(crypto.dump_publickey(crypto.FILETYPE_PEM, k))


if __name__ == '__main__':
	test_add_db_item('username', open('private.pem', 'rb').read())
	test_delete_db_item('username', open('private.pem', 'rb').read())
	# generate_private_public_keypair()
