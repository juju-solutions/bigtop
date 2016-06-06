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

from charmhelpers.core import hookenv
from charms.layer.zookeeper import Zookeeper
from charms.reactive import set_state, when, when_not


@when('bigtop.available')
@when_not('zookeeper.installed')
def install_zookeeper():
    '''
    After Bigtop has done the initial setup, trigger a puppet install,
    via our Zooekeeper library.

    puppet will start the service, as a side effect.

    '''
    hookenv.status_set('waiting', 'Installing Zookeeper')
    zookeeper = Zookeeper()
    zookeeper.install()
    zookeeper.open_ports()
    set_state('zookeeper.installed')
    set_state('zookeeper.started')
    hookenv.status_set('active', 'Ready')


@when('zookeeper.started', 'zkpeer.joined')
def add_node(zkpeer):
    """Add a zookeeper peer.

    Add the unit that just joined, restart Zookeeper, and remove the
    '.joined' state so we don't fall in here again (until another peer joins).
    """
    hookenv.status_set('waiting', 'Configuring Zookeeper: adding nodes.')
    nodes = zkpeer.get_nodes()  # single node since we dismiss .joined below
    zookeeper = Zookeeper()
    zookeeper.add_nodes(nodes)
    zkpeer.dismiss_joined()
    hookenv.log("Added Zookeeper peer. You must manually perform a rolling "
                "restart in order for the change to take effect.")
    hookenv.status_set('active', 'New nodes added. Run the "restart" action to use them.')


@when('zookeeper.started', 'zkpeer.departed')
def remove_node(zkpeer):
    """Remove a zookeeper peer.

    Remove the unit that just departed, restart Zookeeper, and remove the
    '.departed' state so we don't fall in here again (until another peer leaves).
    """
    hookenv.status_set('waiting', 'Configuring Zookeeper: removing nodes.')
    nodes = zkpeer.get_nodes()  # single node since we dismiss .departed below
    zookeeper = Zookeeper()
    zookeeper.remove_nodes(nodes)
    zkpeer.dismiss_departed()
    hookenv.log("Removed Zookeeper peer. You must manually perform a rolling "
                "restart in order for the change to take effect.")
    hookenv.status_set(
        'active', 'Nodes have gone away. Run the "restart" action to update the cluster.')


@when('zookeeper.started', 'zkclient.joined')
def serve_client(client):
    config = Zookeeper().dist_config
    port = config.port('zookeeper')
    rest_port = config.port('zookeeper-rest')  # TODO: add zookeeper REST
    client.send_port(port, rest_port)
