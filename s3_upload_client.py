#!/usr/bin/env python

import argparse
import socket

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Network port", type=int, default=9999)
    parser.add_argument("-x", "--max_received_bytes", help="Max number of bytes", type=int, default=1024)
    parser.add_argument("-s", "--host", help="Host", default='')
    parser.add_argument("-d", "--data", help="Data to send server", default='PING')

    args = parser.parse_args()

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((args.host, args.port))
    conn.send(args.data)
    response = conn.recv(args.max_received_bytes)
    conn.close()
    print("Response from server: {}".format(response))
