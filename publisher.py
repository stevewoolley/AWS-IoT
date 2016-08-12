import logging
import util
import paho.mqtt.publish as publish
from paho.mqtt.client import MQTTv311
import ssl
import json


class Publisher:
    """A MQTT Publisher object"""

    def __init__(self, endpoint, root_ca, key, cert, port=8883, log_level=logging.INFO):
        self.endpoint = endpoint
        self.root_ca = root_ca
        self.key = key
        self.cert = cert
        self.port = port
        self.logger = util.set_logger(level=log_level)

    @staticmethod
    def publish(topic, obj, qos=1):
        publish.single(topic, payload=json.dumps(obj), qos=qos,
                       hostname=self.endpoint,
                       port=self.port,
                       tls={'ca_certs': self.root_ca,
                            'certfile': self.cert,
                            'keyfile': self.key,
                            'tls_version': ssl.PROTOCOL_TLSv1_2
                            },
                       protocol=MQTTv311
                       )
