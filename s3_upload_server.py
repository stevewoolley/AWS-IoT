#!/usr/bin/env python

import argparse
import socket
import logging
import sys
from boto3.s3.transfer import S3Transfer
import boto3.exceptions
import os
from Queue import *
from threading import Thread

LOG_FILE = '/var/log/iot.log'
Q = Queue()


def upload(myfile):
    try:
        transfer.upload_file(myfile, args.bucket, os.path.basename(myfile))
    except (OSError, IOError):
        logging.error("Error: Wrong source file or source file path: {}", myfile)
    except boto3.exceptions.S3UploadFailedError:
        logging.error("Error: Failed to upload file to S3: {}", myfile)


# each worker does this
def pull_from_queue():
    while True:
        item = Q.get()
        upload(item)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bucket", help="S3 bucket", required=True)
    parser.add_argument("-p", "--port", help="Network port", type=int, default=9999)
    parser.add_argument("-w", "--workers", help="Number of workers", type=int, default=1)
    parser.add_argument("-n", "--max_connections", help="Max number connections", type=int, default=5)
    parser.add_argument("-s", "--host", help="Host", default='127.0.0.1')
    parser.add_argument("-x", "--max_received_bytes", help="Max number of bytes", type=int, default=1024)
    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    # initialize s3 connection
    client = boto3.client('s3')
    transfer = S3Transfer(client)

    # create socket, bind, and listen
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((args.host, args.port))
    serversocket.listen(args.max_connections)

    # init the worker(s)
    for i in range(args.workers):
        t = Thread(target=pull_from_queue)
        t.daemon = True
        t.start()

    try:
        while True:
            conn, addr = serversocket.accept()
            data = conn.recv(args.max_received_bytes)
            logging.info("Received from client: {}".format(data))
            Q.put(data)
            conn.send('SUCCESS')
            conn.close()
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
