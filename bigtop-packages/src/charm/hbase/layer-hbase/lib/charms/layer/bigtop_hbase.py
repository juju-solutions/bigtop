from charmhelpers.core import hookenv
from charmhelpers.core import unitdata
from jujubigdata import utils
from charms.layer.apache_bigtop_base import Bigtop


class HBase(object):

    def __init__(self, dist_config):
        self.dist_config = dist_config

    def setup(self):
        self.open_ports()

    def configure(self, hosts, zk_units):
        if not unitdata.kv().get('hbase.bootstrapped', False):
            self.setup()
            unitdata.kv().set('hbase.bootstrapped', True)

        zks = []
        for unit in zk_units:
            ip = utils.resolve_private_address(unit['host'])
            zks.append(ip)
        zks.sort()
        zk_connect = ",".join(zks)

        roles = ['hbase-server', 'hbase-master', 'hbase-client']

        override = {
            'hadoop_hbase::common_config::zookeeper_quorum': zk_connect,
            'hadoop_hbase::deploy::auxiliary': False
        }

        bigtop = Bigtop()
        bigtop.render_site_yaml(hosts, roles, override)
        bigtop.trigger_puppet()

    def open_ports(self):
        for port in self.dist_config.exposed_ports('hbase'):
            hookenv.open_port(port)

    def close_ports(self):
        for port in self.dist_config.exposed_ports('hbase'):
            hookenv.close_port(port)
