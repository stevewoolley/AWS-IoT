#!/usr/bin/env python

from boto3.s3.transfer import S3Transfer
import boto3
import boto3.exceptions
import argparse
import os
import sys

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("bucket", help="S3 bucket")
    parser.add_argument("path", help="path to file")
    parser.add_argument("target", help="target file name", default=[], nargs='*')
    parser.add_argument('--delete', help="delete source file when complete", action='store_true')
    args = parser.parse_args()

    # use same filename if target not given
    if args.target:
        target = ' '.join(args.target)
    else:
        target = os.path.basename(args.path)

    # time to move it
    client = boto3.client('s3', 'us-east-1')
    transfer = S3Transfer(client)
    try:
        transfer.upload_file(args.path, args.bucket, target)
    except (OSError, IOError):
        print("Error: Wrong source file or source file path")
        sys.exit(1)
    except boto3.exceptions.S3UploadFailedError:
        print("Error: Failed to upload file to S3")
        sys.exit(1)

    if args.delete:
        os.remove(args.path)
