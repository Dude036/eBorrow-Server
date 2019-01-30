#!/usr/bin/python3

import simplejson as json
import socket
from pprint import pprint
import re
from multiprocessing import Process, Queue
import time

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
	# HOST = '127.0.0.1'	# Localhost for testing
	HOST = '192.168.1.166'	# Accepts outside traffic !!THIS NEEDS TO STAY!!
	PORT = 41111		# Port to listen on (non-privileged ports are > 1023)
	data = ''

	while True:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
			decode_buffer.put(data.decode())
			# pprint(decode_buffer)


def decoding():
	global decode_buffer
	while True:
		item = decode_buffer.get()
		print("Starting Decoding process.")
		print("Extracting User Information")

		# Extract Username
		username = item[:item.index(':')]
		print("Username:", username)
		item = item[item.index(':')+1:]

		# Extract Key
		user_key = item[:item.index(' ')]
		print("key:", user_key)
		item = item[item.index(' ')+1:]

		# Extract Dictionary
		print("Extracting Data")
		matches = re.findall(r'\<([0-9a-f]{32})\> (\{[^\}]*\}[^\}]*\})', item)
		# pprint(item, stream=open("data.log", 'w'))
		# print(matches[0])
		for match in matches:
			if match:
				# Add to the Database
				print("Hash:", match[0])
				# print(match.group(2))
				pprint(json.loads(match[1]))
			else:
				# Add to the Error Queue
				print("There was an Error processing the item:")
				# pprint(item)


if __name__ == '__main__':
	runnables = [Process(target=main), Process(target=decoding)]

	for r in runnables:
		print("Beginning:", str(r))
		r.start()

	for r in runnables:
		r.join()
		print("Ended:", str(r))
