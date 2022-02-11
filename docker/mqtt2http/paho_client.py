#!/usr/bin/env python3
from uuid import UUID

import paho.mqtt.client as mqtt
import cbor2
import os
import http.client
import json
import ssl

MQTT_HOST = os.getenv('MQTT_BROKER_HOST', default='host.docker.internal')
MQTT_PORT = int(os.getenv('MQTT_BROKER_PORT', default=1883))

HTTP_HOST = os.getenv('HTTP_HOST', default='host.docker.internal')

CLIENT_PEM_PASSWORD = os.getenv('CLIENT_PEM_PASSWORD', default=None)

CONFIG_CALL_KAFKA = False
# CONFIG_CALL_KAFKA = True

KEY_REQUEST_ID = 0
KEY_QUERY_STRING = 1
KEY_CONTENT_TYPE = 2
KEY_ACCEPT = 3
KEY_TARGET_CONTENT_TYPE = 4
KEY_TARGET_ACCEPT = 5
KEY_AUTHORIZATION = 6
KEY_BODY = 7
KEY_HTTP_STATUS = 8

method_dict = {
    0: 'GET',
    1: 'POST',
    2: 'PUT',
    3: 'PATCH',
    4: 'DELETE',
}

HTTP_HEADER_ACCEPT = "accept"
HTTP_HEADER_AUTHORIZATION = "authorization"
HTTP_HEADER_CONTENT_TYPE = "content-type"

CONTENT_TYPE_NOT_SET = 0
CONTENT_TYPE_TEXT_PLAIN = 1
CONTENT_TYPE_APPLICATION_JSON = 2
CONTENT_TYPE_APPLICATION_CBOR = 3
CONTENT_TYPE_APPLICATION_VND_KAFKA_JSON_V2_JSON = 4
CONTENT_TYPE_APPLICATION_VND_KAFKA_V2_JSON = 5

content_type_dict = {
    CONTENT_TYPE_NOT_SET: None,
    CONTENT_TYPE_TEXT_PLAIN: 'text/plain',
    CONTENT_TYPE_APPLICATION_JSON: 'application/json',
    CONTENT_TYPE_APPLICATION_CBOR: 'application/cbor',
    CONTENT_TYPE_APPLICATION_VND_KAFKA_JSON_V2_JSON: 'application/vnd.kafka.json.v2+json',
    CONTENT_TYPE_APPLICATION_VND_KAFKA_V2_JSON: 'application/vnd.kafka.v2+json',
}

content_type_dict_inv = {v: k for k, v in content_type_dict.items()}


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))

    for method in method_dict.values():
        client.subscribe('%s/#' % method)


def on_message(client, userdata, msg):

    try:
        method = msg.topic[:msg.topic.index('/')]
        url = msg.topic[msg.topic.index('/'):]
    except ValueError as e:
        print('ERROR %s' % e)
        return

    if method not in method_dict.values():
        print('ERROR method %s not allowed' % method)

    is_response_topic = '^' in msg.topic
    if is_response_topic:
        return

    cbor = cbor2.loads(msg.payload)
    print(cbor)

    uuid_bytes = cbor.get(KEY_REQUEST_ID, None)

    data = {
        KEY_REQUEST_ID: None if uuid_bytes is None else UUID(bytes=uuid_bytes),
        KEY_QUERY_STRING: cbor.get(KEY_QUERY_STRING, None),
        KEY_CONTENT_TYPE: content_type_dict[cbor.get(KEY_CONTENT_TYPE, CONTENT_TYPE_NOT_SET)],
        KEY_ACCEPT: content_type_dict[cbor.get(KEY_ACCEPT, CONTENT_TYPE_NOT_SET)],
        KEY_TARGET_CONTENT_TYPE: content_type_dict[cbor.get(KEY_TARGET_CONTENT_TYPE, CONTENT_TYPE_NOT_SET)],
        KEY_TARGET_ACCEPT: content_type_dict[cbor.get(KEY_TARGET_ACCEPT, CONTENT_TYPE_NOT_SET)],
        KEY_AUTHORIZATION: cbor.get(KEY_AUTHORIZATION, None),
    }

    if data[KEY_CONTENT_TYPE] is not None:
        if 'application/cbor' in data[KEY_CONTENT_TYPE]:
            data[KEY_BODY] = cbor2.loads(cbor.get(KEY_BODY, None))
        elif 'text/plain' in data[KEY_CONTENT_TYPE]:
            data[KEY_BODY] = cbor.get(KEY_BODY, None)
        else:
            print('A: Unsupported content type')
            return

    print(data)

    if CONFIG_CALL_KAFKA:
        client_pem = '/opt/mqtt2http/mqtt2http.keystore.pem'
        server_pem = '/opt/mqtt2http/kafka.truststore.pem'

        try:
            context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = False  # FOR DEVELOPEMENT ONLY!
            context.load_verify_locations(server_pem)
            context.load_cert_chain(certfile=client_pem, keyfile=client_pem, password=CLIENT_PEM_PASSWORD)
        except ssl.SSLError as e:
            print(e)

        conn = http.client.HTTPSConnection(HTTP_HOST, port=8084, context=context)
    else:
        # call django
        conn = http.client.HTTPConnection('::1', port=8000)

    headers = {}
    payload = None

    if data[KEY_TARGET_ACCEPT] is not None:
        headers[HTTP_HEADER_ACCEPT] = data[KEY_TARGET_ACCEPT]
    elif data[KEY_ACCEPT] is not None:
        headers[HTTP_HEADER_ACCEPT] = data[KEY_ACCEPT]

    if data[KEY_TARGET_CONTENT_TYPE] is not None:
        headers[HTTP_HEADER_CONTENT_TYPE] = data[KEY_TARGET_CONTENT_TYPE]

        # convert python dict to string
        if data[KEY_TARGET_CONTENT_TYPE].endswith('json'):
            payload = json.dumps(data[KEY_BODY])
        else:
            print('B: Unsupported content type')
            return

    elif data[KEY_CONTENT_TYPE] is not None:
        headers[HTTP_HEADER_CONTENT_TYPE] = data[KEY_CONTENT_TYPE]

        # convert python dict to string
        if data[KEY_CONTENT_TYPE].endswith('json'):
            payload = json.dumps(data[KEY_BODY])
        elif data[KEY_CONTENT_TYPE].endswith('text/plain'):
            payload = data[KEY_BODY]
        else:
            print('C: Unsupported content type')
            return

    if data[KEY_AUTHORIZATION] is not None:
        headers[HTTP_HEADER_AUTHORIZATION] = data[KEY_AUTHORIZATION]

    conn.request(method, url, payload, headers)

    if data[KEY_REQUEST_ID] is None:
        # the user is not interested in a response => skip
        return

    response = conn.getresponse()

    http_response_body = response.read().decode()
    body = None
    body_content_type = None

    if len(http_response_body) > 0:

        if data[KEY_ACCEPT] is not None:

            print("HTTP content-type: " + str(response.getheader(HTTP_HEADER_CONTENT_TYPE)))
            print("Accept content-type: " + data[KEY_ACCEPT])

            if response.getheader(HTTP_HEADER_CONTENT_TYPE) == data[KEY_ACCEPT]:
                # content-types match => use as is
                body = http_response_body
                print("A body_content_type = " + str(body_content_type))
                body_content_type = content_type_dict_inv.get(response.getheader(HTTP_HEADER_CONTENT_TYPE))
            else:
                # content-types don't match => translate

                # convert string to python dict
                if response.getheader(HTTP_HEADER_CONTENT_TYPE).endswith('json'):
                    http_response_dict = json.loads(http_response_body)

                    # Todo: remove this hack once we can send more than ~500 bytes to the RIOT node
                    if '/api/auth/login/' in msg.topic or '/api/auth/registration/' in msg.topic:

                        if 'refresh_token' in http_response_dict:
                            before = cbor2.dumps(http_response_dict)
                            print('\n')
                            print('cbor encoded body length before: %d' % len(before))

                            del http_response_dict['refresh_token']

                            after = cbor2.dumps(http_response_dict)
                            print('cbor encoded body length after: %d' % len(after))
                            print('\n')

                    # convert python dict to string
                    if data[KEY_ACCEPT].endswith('cbor'):
                        body = cbor2.dumps(http_response_dict)
                        body_content_type = CONTENT_TYPE_APPLICATION_CBOR
                    else:
                        print('E: Unsupported content type')
                        return
                elif 'text/plain' in response.getheader(HTTP_HEADER_CONTENT_TYPE):
                    body = http_response_body
                    body_content_type = CONTENT_TYPE_TEXT_PLAIN
                else:
                    print('D: Unsupported content type')
                    return
        else:
            body = http_response_body
            print("B body_content_type = " + str(body_content_type))
            body_content_type = content_type_dict_inv.get(response.getheader(HTTP_HEADER_CONTENT_TYPE))

    response_payload_dict = {
        KEY_HTTP_STATUS: response.status,
        KEY_CONTENT_TYPE: body_content_type,
        KEY_BODY: body,
    }
    response_payload = cbor2.dumps(response_payload_dict)

    print("response_payload_dict = " + str(response_payload_dict))

    response_topic = msg.topic + '^' + str(data[KEY_REQUEST_ID])
    print("response_topic = " + response_topic)

    client.publish(response_topic, payload=response_payload, qos=2, retain=False)


client = mqtt.Client(client_id="mqtt2http")
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
