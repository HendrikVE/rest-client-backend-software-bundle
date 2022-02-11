FROM maven:3.8.4-openjdk-11 as builder

RUN apt-get update && apt-get dist-upgrade -y

WORKDIR /build

RUN apt-get install -y git
RUN git config --global user.email "docker@example.com"
RUN git config --global user.name "docker"

RUN git clone https://github.com/eclipse/californium
COPY ./patches patches

WORKDIR /build/californium
RUN git checkout 3.4.0
RUN git am ../patches/*.patch

# RUN mvn dependency:go-offline

RUN mvn package -Dmaven.test.skip=true

FROM openjdk:11

RUN apt-get update && apt-get dist-upgrade -y

COPY --from=builder /build/californium/demo-apps/cf-proxy2/target/cf-proxy2-3.4.0.jar /opt/californium/cf-proxy2.jar
