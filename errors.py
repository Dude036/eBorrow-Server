import logging
'''
Error Handler
'''

ERROR_CODES = {
    0: 'All Clear',
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
    20: 'Invalid Data type received',
    99: 'Unknown Error Occurred. Unable to resolve error'
}


def construct_error(code):
    if code == 0:
        return '!Error:0 {}'
    elif code not in list(ERROR_CODES.keys()):
        logging.debug("ERR HAN :: Error Code passed not found")
        return '!Error:99 {"Description":"' + ERROR_CODES[99] + '"}'
    else:
        return '!Error:' + str(code) + ' {"Description":"' + ERROR_CODES[code] + '"}'


def error_handler(code):
    if code not in list(ERROR_CODES.keys()):
        logging.warning("ERR HAN :: Error Code " + str(code) + " Not found")
        code = 99

    if code != 0:
        logging.error("ERR HAN :: Error Code Received: %i" % code)
    return construct_error(code)


