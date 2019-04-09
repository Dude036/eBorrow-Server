#!/usr/bin/python3
import socket
import time
import logging
from errors import error_handler

END_BYTE = b'\x7F\xFF\x7F\xFF'
BUFF_SIZE = 8192
HOST = '127.0.0.1'          # Localhost for testing
# HOST = '172.31.38.104'	    # AWS testing
# HOST = '24.11.13.224'	    # Accepts outside traffic !!THIS NEEDS TO STAY!!
PORT = 41111		        # Port to listen on (non-privileged ports are > 1023)
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mySocket.bind((HOST, PORT))


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


def network_main(decode_buffer, transmit_buffer):
    data = ''
    while True:
        mySocket.listen()
        conn, addr = mySocket.accept()
        # Got a connection.
        with conn:
            logging.debug('NETWORK :: Connected by %s' % str(addr))
            try:
                data = recv_until(conn)
                # conn.detach()
                if data == '':
                    logging.error('NETWORK :: Unterminated string received')
                    transmit_buffer.put([error_handler(18), conn])
                else:
                    # Send off to Decode
                    logging.info(
                        'NETWORK :: Received Length: ' + str(len(data)))
                    decode_buffer.put([data, conn])
            except Exception as e:
                logging.error('NETWORK :: Exception caught in network_main: ')
                logging.error(type(e))
                logging.error(e.args)
                logging.error(e)


def network_transmit(transmit_buffer):
    time.sleep(.2)
    while True:
        try:
            data, conn = transmit_buffer.get()
            logging.info('NETWORK :: Starting Transmission to ' + str(conn))
            # conn.connect(conn)
            conn.sendall(data.encode() + END_BYTE)
            conn.close()
        except OSError as e:
            logging.error('NETWORK :: Broken Pipe?')
            logging.error(type(e))
            logging.error(e.args)
            logging.error(e)
