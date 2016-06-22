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
from charms.reactive.helpers import data_changed


@when('bigtop.available')
@when_not('zookeeper.installed')
def install_zookeeper():
    '''
    After Bigtop has done the initial setup, trigger a puppet install,
    via our Zooekeeper library.

    puppet will start the service, as a side effect.

    '''
    hookenv.status_set('waiting', 'installing zookeeper')
    data_changed('zkpeer.nodes', [])  # Prime data changed
    zookeeper = Zookeeper()
    zookeeper.install()
    zookeeper.open_ports()
    set_state('zookeeper.installed')
    set_state('zookeeper.started')
    hookenv.status_set('active', 'ready {}'.format(zookeeper.quorum_check()))


@when('zookeeper.started')
def check_cluster():
    '''
    Checkup on the state of the cluster. Inform an operator that they
    need to restart if the peers have changed.

    '''
    zk = Zookeeper()
    peers = zk.read_peers(include_this_machine=False)
    if data_changed('zkpeer.nodes', sorted(peers)):
        if zk.is_zk_leader():
            note = ' (restart this node last)'
        else:
            note = ''
        message = (
            "number of zk peers has changed -- you must use "
            "the 'restart' action to perform a rolling restart to "
            "update your cluster{}".format(note))
        hookenv.status_set('active', message)


@when('zookeeper.started', 'zkclient.joined')
def serve_client(client):
    config = Zookeeper().dist_config
    port = config.port('zookeeper')
    rest_port = config.port('zookeeper-rest')  # TODO: add zookeeper REST
    client.send_port(port, rest_port)
