FROM debian:latest

ARG SENSOR_NETWORK
ARG GATEWAY_ID
ARG GATEWAY_NAME
ARG BROKER_NAME

RUN apt-get update && apt-get upgrade -y

WORKDIR /opt

RUN apt-get install -y g++ make cmake libssl-dev

RUN apt-get install -y git
RUN git config --global user.email "docker@example.com"
RUN git config --global user.name "docker"

RUN git clone https://github.com/eclipse/paho.mqtt-sn.embedded-c

WORKDIR /opt/paho.mqtt-sn.embedded-c
# RUN git checkout 3.2.0
RUN git checkout 59797127e7f3d024de576555cd4232c68e874ac6

# apply patches
COPY ./patches patches
RUN git am patches/*.patch
RUN rm -r patches

# Note: The paho MQTT-SN gateway does not like it to be moved somewhere else because it uses shared libraries
#       and expects them to exist where they have been when building the binary.
WORKDIR /opt/paho.mqtt-sn.embedded-c/MQTTSNGateway

COPY ./clients.conf .
COPY ./predefinedTopic.conf .

COPY ./gateway.conf .
RUN sed -i "s/GATEWAY_ID/$GATEWAY_ID/" gateway.conf
RUN sed -i "s/GATEWAY_NAME/$GATEWAY_NAME/" gateway.conf
RUN sed -i "s/BROKER_NAME/$BROKER_NAME/" gateway.conf

RUN ./build.sh ${SENSOR_NETWORK}

ENTRYPOINT ./bin/MQTT-SNGateway
