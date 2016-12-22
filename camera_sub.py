#!/usr/bin/env python

import argparse
import json
import util
import datetime
import os
import ssl
import paho.mqtt.client as mqtt
from cloud_tools import Publisher
#from camera import Camera

STORAGE_DIRECTORY = '/tmp'
SNAP_FILENAME = 'snapshot.png'
DATE_FORMAT = '%Y_%m_%d_%H_%M_%S'
MQTT_PORT = 8883
MQTT_KEEPALIVE = 60


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    # if camera.snap('/'.join((STORAGE_DIRECTORY, SNAP_FILENAME))):
    #     filename, file_extension = os.path.splitext(SNAP_FILENAME)
    #     f = "{}_{}{}".format(datetime.datetime.now().strftime(DATE_FORMAT), args.source, file_extension)
    #     Publisher(args.endpoint, args.rootCA, args.key, args.cert, client_id=args.clientID).report(t,
    #                                                                                                {'last_snapshot': f})
    #     util.copy_to_s3(camera.filename, args.bucket, f)


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_connect(mqttc, obj, flags, rc):
    print "Connected to %s:%s" % (mqttc._host, mqttc._port)


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_log(mqttc, obj, level, string):
    print(string)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
    parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
    parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)
    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-b", "--bucket", help="S3 snapshot bucket", default=None)
    args = parser.parse_args()

    # camera = Camera(rotation=args.rotation, horizontal_resolution=args.horizontal_resolution,
    #                 vertical_resolution=args.vertical_resolution)

    # client connect
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_log = on_log

    client.tls_set(args.rootCA, certfile=args.cert, keyfile=args.key, cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_SSLv23)
    client.connect(args.endpoint, MQTT_PORT, MQTT_KEEPALIVE)

    for t in args.topic:
        client.subscribe(t, 0)

    # loop forever
    client.loop_forever()
