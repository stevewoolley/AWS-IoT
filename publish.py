import argparse
import logging
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


def set_logger(name='iot', level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename="/var/log/%s.log" % name,
                        filemode='a')
    return logging.getLogger()


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-w", "--websocket", help="Use MQTT over WebSocket", action='store_true')
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="IoT topic", required=True)
parser.add_argument("-m", "--message", help="Message", default="{}")
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
args = parser.parse_args()

# Set logger
logger = set_logger(level=args.log_level)

# AWSIoTMQTTClient connection configuration
client = None
if args.websocket:
    client = AWSIoTMQTTClient(args.clientID, useWebsocket=True)
    client.configureEndpoint(args.endpoint, 443)
    client.configureCredentials(args.rootCA)
else:
    client = AWSIoTMQTTClient(args.clientID)
    client.configureEndpoint(args.endpoint, 8883)
    client.configureCredentials(args.rootCA, args.key, args.cert)
client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec

# Connect
client.connect()
# time.sleep(2)  # may not be needed but seems to be more reliable push if wait after connect

# Publish
result = client.publish(args.topic, args.message, 1)
logger.info("publishing to topic: %s message: %s result: %s"
            % (args.topic, args.message, result))
