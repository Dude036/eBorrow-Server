'''
Error Handler
'''

ERROR_CODES = {
    1: 'Invalid Packet Format',
    2: 'Invalid/Unrecognized Packet ID',
    3: 'Invalid User Private Key',
    4: 'Invalid User Public Key',
    5: 'Invalid Header Format',
    6: 'Invalid Packet Format',
    7: 'Unspecified Deletion Key',
    8: 'Key not found in User Database',
    9: 'Incorrect Key Value Pair',
    10: 'Incorrect Key hash',
    11: 'Missing Private Key',
    12: 'Missing Public Key',
    13: 'Illegal Character',
    14: 'Unable to Write to Database',
    15: 'Unable to Read Database',
    16: 'Username already exists',
    17: 'Username not found',
    18: 'Unterminated Transmission Buffer Received',
    19: 'Invalid JSON',
    99: 'Unknown Error Occurred. Unable to resolve error'
}


def error_handler(error_buffer, transmit_buffer):
    # global error_buffer
    while True:
        code, addr = error_buffer.get()
        print("Starting Error Notification")
        if code not in list(ERROR_CODES.keys()):
            print("Error Code Not found")
            continue

        # Valid Key, set to the Key reference
        print("Code:", code)
        print("Message:", ERROR_CODES[code])
