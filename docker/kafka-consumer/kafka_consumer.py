#!/usr/bin/env python3
from time import sleep
import random

from kafka import KafkaConsumer
from json import loads
from kubernetes import client, config

consumer = KafkaConsumer(
    'riot-node-17-temperature',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

while True:
    for message in consumer:
        print('Received a new value: ' + message.value)

        replicas = random.randint(1, 42)

        # Configs can be set in Configuration class directly or using helper utility
        config.load_kube_config()

        api_instance = client.AppsV1Api()

        api_response = api_instance.patch_namespaced_deployment_scale(
            'kubernetes-bootcamp', 'default', {'spec': {'replicas': replicas}})
        print(api_response)

    sleep(1)
