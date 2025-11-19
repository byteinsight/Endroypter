"""
Paho-MATT Documentation: https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
Getting Started Guide: http://www.steves-internet-guide.com/mosquitto-broker/
Starting Mosquitto: sudo systemctl start mosquitto.service
Stopping Mosquitto: sudo systemctl stop mosquitto.service
source venv/bin/activate

"""
from datetime import datetime
import json
import os
import paho.mqtt.client as mqtt  # Version 2.10 installed.
import random
import string
import time


class MqttClient:
    client = None
    dbClient = None
    location_name = None
    irl_key = None

    def __init__(self, app_context, remote=False):

        # Create a logger
        self.app_context = app_context
        self.logger = app_context.logger

        # If remote is True then we use the specified client_id else its the iRacing Cust ID
        if remote:
            client_id = f"C{self.app_context.config.system.MQTT_REMOTE_CLIENT}"
        else:
            client_id = f"C{self.app_context.config.user.IRACE_CUSTID}"
            self.irl_key = self.app_context.config.user.IRACE_INSIGHT_KEY

        # We need the port number later when we connect
        self.port = int(self.app_context.config.system.MQTT_PORT)
        self.prime_topic = self.app_context.config.system.MQTT_PRIME_TOPIC

        # Create instance of client with client ID
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, transport="websockets")

        # Set username and password before connecting and starting the loop.
        self.client.username_pw_set(username=self.app_context.config.system.MQTT_USERNAME, password=self.app_context.config.system.MQTT_PASSWORD)

        # Set all our callbacks
        self.client.on_connect = self.on_connect_callback
        self.client.on_publish = self.on_publish_callback
        self.client.on_disconnect = self.on_disconnect_callback
        self.client.on_subscribe = self.on_subscribe_callback
        self.client.on_message = self.on_message_callback
        self.client.on_log = self.on_log_callback

    ###### CALLBACKS START #####

    def on_connect_callback(self, client, userdata, flags, reason_code, properties):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_connect
        The callback called when the broker responds to our connection request.
        :param client:
        :param userdata:
        :param flags:
        :param reason_code:
        :param properties:
        :return:
        """
        if reason_code == 0 and client.is_connected():
            self.logger.info(f"on_connect: Broker Connected - flags: {str(flags)}; Result code: {str(reason_code)}")
            return True
        else:
            self.logger.error(f"on_connect: Failed to Connect - flags: {str(flags)}; Result code: {str(reason_code)}")
            return False

    def on_message_callback(self, client, userdata, message):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_message
        The callback called when a message has been received on a topic that the client subscribes to.
        :param client:
        :param userdata:
        :param message:
        :return:
        """
        self.logger.info(f"on_message received from {message.topic} QOS:{message.qos} retain:{message.retain} - `{message.payload.decode()}` ")

    def on_publish_callback(self, client, userdata, mid, reason_code, properties):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_publish
        When the message has been published to the Broker an acknowledgement is sent that results in the on_publish callback being called.
        The on_publish callback function must receive three parameters (client, userdata and mid), version 2 needs 2 more (reason_code, properties).
        :param client:
        :param userdata:
        :param mid:
        :param reason_code:
        :param properties:
        :return:
        """
        if reason_code != "Success":
            self.logger.warning(f"on_publish response: Mid:{mid}; RC:{reason_code}.")
        pass

    def on_subscribe_callback(self, client, userdata, mid, reason_code_list, properties):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_subscribe

        :param client:
        :param userdata:
        :param mid:
        :param reason_code_list:
        :param properties:
        :return:
        """
        self.logger.info(f"on_subscribe response: Mid:{mid}; RC:{str(reason_code_list)}.")

    def on_disconnect_callback(self, client, userdata, disconnect_flags, reason_code, properties):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_disconnect
        If you only publish messages at infrequent intervals then you will probably want to disconnect the client between publishing.
        You can use the disconnect method along with the on_disconnect callback for this e.g.  client1.on_disconnect = on_disconnect
        Called with client1.disconnect()

        :param client: the client instance for this callback
        :param userdata: the private user data as set in Client() or user_data_set()
        :param disconnect_flags:
        :param reason_code: https://eclipse.dev/paho/files/paho.mqtt.python/html/types.html#paho.mqtt.reasoncodes.ReasonCode
        :param properties:
        :return:
        """
        self.logger.info(f"on_disconnect: {str(disconnect_flags)} result code: {reason_code}")

    def on_log_callback(self, client, obj, level, message):
        """
        https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html#paho.mqtt.client.Client.on_log
        :param client:
        :param obj:
        :param level:
        :param message:
        :return:
        """
        self.logger.debug(f"on_log: Level:{level} with {message}")

    ###### CALLBACKS END #####

    def save_message(self, topic, message_dict):

        filepath = os.path.join(self.app_context.paths.SAVES_PATH, str(message_dict['SessionID'], ) + ".json")
        self.logger.info(f"Save Message for SessionID: {message_dict['SessionID'],} in {filepath}")

        message = json.dumps({topic: message_dict})
        with open(filepath, "a") as f:
            f.write(f"{message}\n")

    def publish_message(self, topic, message_dict, message_header=None):
        """
        Publish Message is called by the user.
        :param topic:
        :param message_dict:
        :param message_header:
        :return:
        """

        # If a message dictionary has been provided
        if message_dict:

            # Append the message header if provided.
            if message_header:
                message_dict = message_dict | message_header

                # Add our IRI Key
                message_dict['IRIKey'] = self.irl_key

            # Dump the json to a string and send message
            message = json.dumps(message_dict)

            # If the config tells us to save the message
            if self.app_context.config.user.SAVE_DATA:
                self.save_message(topic, message_dict)

            self.client.connect(self.app_context.config.system.MQTT_BROKER_ADDRESS, port=self.port)  # connect to broker
            self.logger.info(f"Publish Called with {topic} and {message}")
            self.client.publish(topic, message)

    def subscribe_to_topic(self, topic=None):
        """
        Subscribes to the given topic or the prime topic as per config.
        :param topic:
        :return:
        """
        if not topic:
            topic = self.config['MQTT']['prime_topic']

        try:
            self.client.subscribe(topic, 0)

            self.logger.info(f"subscribe_to_topic `{topic}`")

        except Exception as error:
            self.logger.error(self.logger.info(f"subscribe_to_topic: Error `{topic}` {str(error)}"))

    def stop_the_loop(self):
        self.client.loop_stop()
        self.logger.info("stop - no longer listening for updates")

    def subscriber_test(self, topic=None):
        self.logger.info(f"subscriber_test")
        self.client.connect(self.config['MQTT']['broker_address'], port=self.port, keepalive=60)  # connect to broker
        self.subscribe_to_topic(topic)
        self.client.loop_forever()

    def publisher_test(self):

        try:
            # infinite loop
            while True:
                # We will use the current time and a unique string for the test message.
                date = datetime.now()
                unique_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

                # Publish the message under the give topic.
                mqtt_client.publish_message(self.prime_topic, f"Code:{unique_string} at {date.strftime('%X')}")

                # Sleeping for 5 second not to cause overloading issues.
                time.sleep(5)

        # press ctrl+c to exit
        except KeyboardInterrupt:
            pass

    def can_we_mqtt(self, session_id):
        """
        session_id != 0 → live session
        session_id == 0 and allow_replay_posting == True → debugging a replay
        allow_replay_posting == False and session_id == 0 → block MQTT
        :param session_id:
        :return:
        """
        mqtt_enabled = self.app_context.config.user.MQTT_ENABLE
        allow_replay = self.app_context.config.system.MQTT_ALLOW_REPLAY_POSTING

        if mqtt_enabled and (session_id != 0 or allow_replay):
            return True
        return False


if __name__ == '__main__':
    """ MAIN """

    # Our config that would normally come from the config file.
    # Our iracing custid is used as our client id with the MQTT Broker
    mini_config = {
        'debug': True,
        'logs_folder': ".",
        'iRacing': {'CUSTID': 784461},
        'MQTT': {
            'activate': True,
            'broker_address': "194.164.95.88",
            'port': 1883,
            'username': "jim_clark",
            'password': "karmic6",
            'remote_client': "remote_666",
            'prime_topic': "core_topic"
        }

    }

    # Create a MQTT Client (Class Above)
    mqtt_client = MqttClient(mini_config)

    # Run the client
    mqtt_client.publisher_test()
