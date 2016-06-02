# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from charmhelpers.core import hookenv
from charmhelpers.core import host
from jujubigdata import utils
from charms.layer.apache_bigtop_base import Bigtop
from charms import layer


class Kafka(object):
    """
    This class manages Kafka.
    """
    def __init__(self):
        self.dist_config = utils.DistConfig(
            data=layer.options('apache-bigtop-base'))

    def open_ports(self):
        for port in self.dist_config.exposed_ports('kafka'):
            hookenv.open_port(port)

    def configure_kafka(self, zk_units):
        # Get ip:port data from our connected zookeepers
        zks = []
        for unit in zk_units:
            ip = utils.resolve_private_address(unit['host'])
            zks.append("%s:%s" % (ip, unit['port']))
        zks.sort()
        zk_connect = ",".join(zks)
        service, unit_num = os.environ['JUJU_UNIT_NAME'].split('/', 1)
        kafka_port = self.dist_config.port('kafka')

        roles = ['kafka-server']
        override = {
            'kafka::server::broker_id': unit_num,
            'kafka::server::port': kafka_port,
            'kafka::server::zookeeper_connection_string': zk_connect,
        }

        bigtop = Bigtop()
        bigtop.render_site_yaml(roles=roles, overrides=override)
        bigtop.trigger_puppet()

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        host.service_start('kafka-server')

    def stop(self):
        host.service_stop('kafka-server')