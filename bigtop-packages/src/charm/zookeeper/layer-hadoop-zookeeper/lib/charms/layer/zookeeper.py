'''
zookeeper.py
'''

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
    stop, incrementing and decrementing quorum.

    '''
    def __init__(self, dist_config=None):
        self._dist_config = dist_config or DistConfig(
            data=layer.options('apache-bigtop-base'))

        self._roles = ['zookeeper-server', 'zookeeper-client']
        self._hosts = {}
        self._peers = []

    def _read_peers(self):
        '''
        Refresh this class' idea of what peers are available.

        Typically, we do this before triggering puppet to update
        zoo.cfg with a list of peers, usually because a peer has
        joined or left.

        The first item in this list should always be the node that
        this code is executing on. We take care of that by writing the
        node to the list of peers first, by default, before we ever
        see another peer (see self._override), and then we are always
        careful to preserve the order of the list thereafter.

        '''
        # Reset -- the state in this class is secondary to the state
        # in the real world.
        self._peers = []

        # TODO: Instead of getting the list of peers from the config,
        # just inspect our peers via the charm tools.
        with open("/usr/lib/zookeeper/conf/zoo.cfg", "r") as zoo_cfg:
            for line in zoo_cfg.readlines():
                if line.startswith("server."):
                    peer = line.strip().split("=")
                    peer[0] = int(peer[0].split(".")[1])
                    self._peers.append(tuple(peer))

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
            "hadoop_zookeeper::server::myid": local_unit().split("/")[1]
        }
        if self._peers:
            override["hadoop_zookeeper::server::ensemble"] = self._peers
        else:
            this_node = (format_node(local_unit(), unit_private_ip()))
            override["hadoop_zookeeper::server::ensemble"] = [this_node]

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

    def increase_quorum(self, node_list):
        '''
        Add a nodes.

        Will trigger a config update and restart.

        '''
        self._read_peers()
        log("Increasing quorum with node_list: {}".format(node_list))
        nodes = [format_node(*node) for node in node_list]
        for node in nodes:
            if node not in self._peers:
                self._peers.append(node)

        self.install()   # update config and trigger puppet

    def decrease_quorum(self, node_list):
        '''
        Remove nodes.

        Will trigger a config update and restart.

        '''
        self._read_peers()
        nodes = [format_node(*node) for node in node_list]
        self._peers = [peer for peer in self._peers if peer not in nodes]

        self.install()  # update config and trigger puppet
