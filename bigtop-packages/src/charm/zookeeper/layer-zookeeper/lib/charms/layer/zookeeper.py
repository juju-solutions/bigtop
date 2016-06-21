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

import json
import shutil

from charmhelpers.core import host
from charms import layer
from charms.layer.apache_bigtop_base import Bigtop
from jujubigdata.utils import DistConfig
from charmhelpers.core.hookenv import (open_port, close_port, log,
                                       unit_private_ip, local_unit)


def format_node(unit, node_ip):
    '''
    Given a juju unit name and an ip address, return a tuple
    containing an id and formatted ip string suitable for passing to
    puppet, which will write it out to zoo.cfg.

    '''
    return (unit.split("/")[1], "{ip}:2888:3888".format(ip=node_ip))


class Zookeeper(object):
    '''
    Utility class for managing Zookeeper tasks like configuration, start,
    stop, and adding and removing nodes.

    '''
    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

        self._roles = ['zookeeper-server', 'zookeeper-client']
        self._hosts = {}

    def _read_peers(self):
        '''
        Read out the list of peers available.

        Typically, we do this before triggering puppet to update
        zoo.cfg with a list of peers, usually because a peer has
        joined or left.

        The first item in this list should always be the node that
        this code is executing on. We take care of that by writing the
        node to the list of peers first, by default, before we ever
        see another peer (see self._override), and then we are always
        careful to preserve the order of the list thereafter.

        '''
        with open("./resources/ensemble.json", "r") as ensemble_file:
            peers = json.loads(ensemble_file.read())['ensemble']
        if not peers:
            this_node = format_node(local_unit(), unit_private_ip())
            peers = [this_node]

        return peers

    def _write_peers(self, peers):
        '''
        Update the peer list for this peer.

        '''
        shutil.copyfile(
            './resources/ensemble.json',
            './resources/ensemble.bak'
        )
        with open("./resources/ensemble.json", "r") as ensemble_file:
            content = json.loads(ensemble_file.read())
        with open("./resources/ensemble.json", "w") as ensemble_file:
            content['ensemble'] = peers
            ensemble_file.write(json.dumps(content))

    @property
    def dist_config(self):
        '''
        Charm level config.

        '''
        return self._dist_config

    @property
    def _override(self):
        '''
        Return a dict of keys and values that will override puppet's
        defaults.

        '''
        override = {
            "hadoop_zookeeper::server::myid": local_unit().split("/")[1],
            "hadoop_zookeeper::server::ensemble": self._read_peers()
        }

        return override

    def install(self):
        '''
        Write out the config, then run puppet.

        After this runs, we should have a configured and running service.

        '''
        bigtop = Bigtop()
        log("Rendering site yaml with overrides: {}".format(self._override))
        bigtop.render_site_yaml(self._hosts, self._roles, self._override)
        bigtop.trigger_puppet()

    def start(self):
        '''
        Request that our service start. Normally, puppet will handle this
        for us.

        '''
        host.service_start('zookeeper-server')

    def stop(self):
        '''
        Stop Zookeeper.

        '''
        host.service_stop('zookeeper-server')

    def open_ports(self):
        '''
        Expose the ports in the configuration to the outside world.

        '''
        for port in self.dist_config.exposed_ports('zookeeper'):
            open_port(port)

    def close_ports(self):
        '''
        Close off communication from the outside world.

        '''
        for port in self.dist_config.exposed_ports('zookeeper'):
            close_port(port)

    def add_nodes(self, node_list):
        '''
        Add node(s).

        Will stage a config update. For now, an ops person must
        manually restart, with the restart action, for it to take
        effect.

        '''
        peers = self._read_peers()
        log("Adding a node. New node_list: {}".format(node_list))
        nodes = [format_node(*node) for node in node_list]
        for node in nodes:
            if node not in peers:
                peers.append(node)

        self._write_peers(peers)

    def remove_nodes(self, node_list):
        '''
        Remove node(s).

        Will stage a config update. For now, an ops person must
        manually restart, with the restart action, for it to take
        effect.

        '''
        peers = self._read_peers()
        nodes = [format_node(*node) for node in node_list]
        peers = [peer for peer in peers if peer not in nodes]
        self._write_peers(peers)

    def quorum_check(self):
        '''
        Returns a string reporting the node count. Append a message
        informing the user if the node count is too low for good quorum,
        or is even (meaning that one of the nodes is redundant for
        quorum).

        '''
        node_count = len(self._read_peers())
        count_str = "{} zk nodes".format(node_count)
        if node_count < 3:
            return " ({}; less than 3 nodes is suboptimal)".format(count_str)
        if node_count % 2 == 0:
            return " ({}; even number is suboptimal)".format(count_str)
        return "({})".format(count_str)
