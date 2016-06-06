'''
Reactive handlers for Zookeeper.
'''

from charmhelpers.core import hookenv
from charms.layer.zookeeper import Zookeeper
from charms.reactive import set_state, when, when_not
from jujubigdata.utils import DistConfig


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
def quorum_add(zkpeer):
    """Add a zookeeper peer.

    Add the unit that just joined, restart Zookeeper, and remove the
    '.joined' state so we don't fall in here again (until another peer joins).
    """
    hookenv.status_set('waiting', 'Configuring Zookeeper: adding nodes.')
    nodes = zkpeer.get_nodes()  # single node since we dismiss .joined below
    zookeeper = Zookeeper()
    zookeeper.increase_quorum(nodes)
    zkpeer.dismiss_joined()
    hookenv.status_set('active', 'Ready')


@when('zookeeper.started', 'zkpeer.departed')
def quorum_remove(zkpeer):
    """Remove a zookeeper peer.

    Remove the unit that just departed, restart Zookeeper, and remove the
    '.departed' state so we don't fall in here again (until another peer leaves).
    """
    hookenv.status_set('waiting', 'Configuring Zookeeper: removing nodes.')
    nodes = zkpeer.get_nodes()  # single node since we dismiss .departed below
    zookeeper = Zookeeper()
    zookeeper.decrease_quorum(nodes)
    zkpeer.dismiss_departed()
    hookenv.status_set('active', 'Ready')


@when('zookeeper.started', 'zkclient.joined')
def serve_client(client):
    config = DistConfig()
    port = config.port('zookeeper')
    rest_port = config.port('zookeeper-rest')  # TODO: add zookeeper REST
    client.send_port(port, rest_port)
