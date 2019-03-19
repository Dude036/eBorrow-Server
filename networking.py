#!/usr/bin/python3
import socket
import time

END_BYTE = b'\x7F\xFF\x7F\xFF'
BUFF_SIZE = 8192
PORT = 41111		# Port to listen on (non-privileged ports are > 1023)


def recv_until(sock):
    """ recv_until
    Read in data until a certian byte is recieved.
    sock: socket object: the socket to recieve data on.
    """
    total_data = []
    # data = b''
    start = time.time()
    timeout = 20
    while True:
        data = sock.recv(BUFF_SIZE)
        if END_BYTE in data:
            total_data.append(data[:data.find(END_BYTE)])
            break
        total_data.append(data)
        if len(total_data) > 1:
            # check if end_of_data was split
            last_pair = total_data[-2] + total_data[-1]
            if END_BYTE in last_pair:
                total_data[-2] = last_pair[:last_pair.find(END_BYTE)]
                total_data.pop()
                break
        if time.time() - start > timeout:
            return ''
    return ''.join([thing.decode() for thing in total_data])


def network_main(decode_buffer, error_buffer):
    HOST = '127.0.0.1'			# Localhost for testing
    # HOST = '172.31.38.104'	    # AWS testing
    # HOST = '192.168.1.166'	    # Accepts outside traffic !!THIS NEEDS TO STAY!!
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
                    data = recv_until(conn)
                    if data == '':
                        print("Unterminated string received")
                        error_buffer.put([18, addr])
                    else:
                        # Send off to Decode
                        print("Recieved:", "Length:", len(data))
                        decode_buffer.put([data, addr])
                except Exception as e:
                    print(type(e))
                    print(e.args)
                    print(e)


def network_transmit(transmit_buffer):
    while True:
        data, addr = transmit_buffer.get()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((addr, PORT))
            s.sendall(data.encode() + END_BYTE)
            s.close()
