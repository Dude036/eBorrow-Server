#!/usr/bin/python3

import simplejson as json
import socket
from pprint import pprint
import re
from multiprocessing import Process, Queue
import time
from database import add_to_library, remove_from_library, add_user, delete_user

decode_buffer = Queue()

def recvall(sock):
	''' Recieves all the data in the network buffer	'''
	BUFF_SIZE = 1024
	data = b''
	while True:
		part = sock.recv(BUFF_SIZE)
		data += part
		if len(part) < BUFF_SIZE:
			# either 0 or end of data
			break
	return data


def main():
	global decode_buffer
	# HOST = '127.0.0.1'			# Localhost for testing
	HOST = '172.31.38.104'		# AWS testing
	# HOST = '192.168.1.166'	# Accepts outside traffic !!THIS NEEDS TO STAY!!
	PORT = 41111		# Port to listen on (non-privileged ports are > 1023)
	data = ''

	while True:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# Setup
			s.bind((HOST, PORT))
			s.listen()
			conn, addr = s.accept()
			# Got a connection.
			with conn:
				print('Connected by', addr)
				try:
					data = recvall(conn)
				except Exception as e:
					print(type(e))
					print(e.args)
					print(e)
			print("Recieved:", "Length:", len(data))
			# pprint(data)
			# Send off to Decode
			decode_buffer.put([data.decode(), addr])
			# pprint(decode_buffer)


def read_key(item):
	delimit = -1
	for pos in range(len(item)-1):
		if item[pos] == '|' and item[pos+1] == '|':
			delimit = pos
			break
	return delimit


def verify_key(username, key, public=True):
	all_keys = json.load(open('keys.json'))
	if username not in list(all_keys.keys()):
		return False
	elif public:
		return all_keys[username]['public'] == key
	else:
		return all_keys[username]['private'] == key


def find_user(username):
	found = False
	for file in os.listdir("."):
		if file.endswith(".json") and user == file[:-5]:
			found = True
	return found


def decoding():
	global decode_buffer
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
			print("Dismissing invalid packet format")
			print("Sending Error to:", addr)
			continue

		# Every command starts with the Username, It's easy to get that out of the way
		# Extract Username
		delimit_pos = 0
		for point in header:
			if point == ':':
				break
			else:
				delimit_pos += 1

		# No Delimiter = New User Application
		if delimit_pos == 0:
			add_user(header[1:])
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
		if packet_id == 1:
			# Delete User from Database
			pass
		elif packet_id == 2:
			# Remove an Item from database
			header = header[3:]
			if verify_key(username, header, public=False):
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
			# Remove the Header information
			header = header[3:]
			# print(header)
			if verify_key(username, header, public=False):
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
			# send specific Data tp the User
			pass
		elif packet_id == 6:
			# Update Item Ownership
			pass
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



if __name__ == '__main__':
	runnables = [Process(target=main), Process(target=decoding)]

	for r in runnables:
		print("Beginning:", str(r))
		r.start()

	for r in runnables:
		r.join()
		print("Ended:", str(r))
