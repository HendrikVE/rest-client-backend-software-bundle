#!/usr/bin/env python
import os
import shutil
import subprocess
import time
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class TransportConfig(Enum):
    COAP = auto(),
    COAP_SECURE = auto(),
    MQTT = auto(),
    MQTT_SN = auto(),


class IpVersionConfig(Enum):
    IPV4_ONLY = auto(),
    IPV6_ONLY = auto(),
    IPV4_IPV6_DUAL = auto(),


@dataclass
class BuildConfig:
    board: str
    transport_config: TransportConfig
    ip_version_config: IpVersionConfig

    def __str__(self):
        return 'BuildConfig(%s, %s, %s)' % (self.board, self.transport_config, self.ip_version_config)


def validate_config(config):

    # test for valid enum members
    if config.transport_config.value not in [e.value for e in TransportConfig]:
        raise ValueError('Invalid transport_config %s' % config.transport_config)

    if config.ip_version_config.value not in [e.value for e in IpVersionConfig]:
        raise ValueError('Invalid ip_version_config %s' % config.ip_version_config)


# BOARD = 'esp32-wroom-32'
# BOARD = 'native'
BOARD = 'nucleo-f207zg'

# Todo: add experiment name to dst dir

compilation_configs = [
    # transport CoAP with different IP versions
    BuildConfig(BOARD, TransportConfig.COAP, IpVersionConfig.IPV4_ONLY),
    BuildConfig(BOARD, TransportConfig.COAP, IpVersionConfig.IPV6_ONLY),
    BuildConfig(BOARD, TransportConfig.COAP, IpVersionConfig.IPV4_IPV6_DUAL),

    # transport CoAPS with different IP versions
    BuildConfig(BOARD, TransportConfig.COAP_SECURE, IpVersionConfig.IPV4_ONLY),
    BuildConfig(BOARD, TransportConfig.COAP_SECURE, IpVersionConfig.IPV6_ONLY),
    BuildConfig(BOARD, TransportConfig.COAP_SECURE, IpVersionConfig.IPV4_IPV6_DUAL),

    # transport MQTT with different IP versions
    BuildConfig(BOARD, TransportConfig.MQTT, IpVersionConfig.IPV4_ONLY),
    BuildConfig(BOARD, TransportConfig.MQTT, IpVersionConfig.IPV6_ONLY),
    BuildConfig(BOARD, TransportConfig.MQTT, IpVersionConfig.IPV4_IPV6_DUAL),

    # transport MQTT-SN with different IP versions
    BuildConfig(BOARD, TransportConfig.MQTT_SN, IpVersionConfig.IPV4_ONLY),
    BuildConfig(BOARD, TransportConfig.MQTT_SN, IpVersionConfig.IPV6_ONLY),
    BuildConfig(BOARD, TransportConfig.MQTT_SN, IpVersionConfig.IPV4_IPV6_DUAL),
]

start = time.time()

for config in compilation_configs:
    print("Build for config: " + config.__str__())

    try:
        validate_config(config)
    except ValueError as e:
        print(e)
        continue

    my_env = os.environ.copy()
    my_env['BOARD'] = config.board
    my_env['PORT'] = 'tap0'
    my_env['DEVELHELP'] = '0'
    my_env['ENABLE_DEBUG'] = '0'
    my_env['USEMODULE'] = 'stdio_null'

    if config.ip_version_config == IpVersionConfig.IPV4_ONLY:
        my_env['IPV4'] = '1'
        my_env['IPV6'] = '0'
    elif config.ip_version_config == IpVersionConfig.IPV6_ONLY:
        my_env['IPV4'] = '0'
        my_env['IPV6'] = '1'
    elif config.ip_version_config == IpVersionConfig.IPV4_IPV6_DUAL:
        my_env['IPV4'] = '1'
        my_env['IPV6'] = '1'

    ip_version_str = config.ip_version_config.name

    # Todo: allow more than one transport at the same time
    if config.transport_config == TransportConfig.COAP:
        my_env['TRANSPORT_COAP'] = '1'
    elif config.transport_config == TransportConfig.COAP_SECURE:
        my_env['TRANSPORT_COAP_SECURE'] = '1'
    elif config.transport_config == TransportConfig.MQTT:
        my_env['TRANSPORT_MQTT'] = '1'
    elif config.transport_config == TransportConfig.MQTT_SN:
        my_env['TRANSPORT_MQTT_SN'] = '1'

    transport_str = config.transport_config.name

    riot_repository_dir = os.getenv('RIOT_REPOSITORY_DIR', os.path.join(SCRIPT_DIR, 'RIOT'))

    app_dir = os.path.join(riot_repository_dir, 'examples', 'rest_client')

    p = Popen(['make', '-j'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
              universal_newlines=True,  # text mode
              cwd=app_dir,
              env=my_env)

    filename = 'rest-client.elf'
    base_dir = os.path.join(SCRIPT_DIR, 'built_elffiles')
    destination_dir = os.path.join(base_dir, config.board, transport_str, ip_version_str)

    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    for line in p.stdout:
        print(line, end='')

    for line in p.stderr:
        print('ERROR: %s' % line, end='')

    line = p.stderr.readline()
    if not line == '':
        print(line)
        for line in p.stderr:
            print('ERROR: %s' % line, end='')
        continue

    src_file = os.path.join(app_dir, 'bin', config.board, filename)
    dst_file = os.path.join(destination_dir, filename)

    shutil.copy2(src_file, dst_file)

stop = time.time()
print('compilation took %d s' % (stop-start))

# Todo: print a table with all elf file sizes
print('END')

