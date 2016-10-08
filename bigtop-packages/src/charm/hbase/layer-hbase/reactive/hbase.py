from charms.reactive import when, when_not, is_state, set_state, remove_state
from charms.layer.bigtop_hbase import HBase
from charmhelpers.core import hookenv
from charms.reactive.helpers import data_changed
from charms.layer.hadoop_client import get_dist_config


@when('bigtop.available')
@when_not('zookeeper.joined')
def waiting_for_zookeeper():
    hookenv.status_set('blocked', 'Waiting for relation to Zookeeper')
    remove_state('hbase.installed')


@when('bigtop.available', 'zookeeper.joined')
@when_not('zookeeper.ready')
def waiting_for_zookeeper_ready(zk):
    hookenv.status_set('waiting', 'Waiting for Zookeeper to become ready')
    remove_state('hbase.installed')


@when('bigtop.available', 'zookeeper.ready')
@when_not('hadoop.hdfs.ready')
def waiting_for_hdfs(zk):
    hookenv.status_set('waiting', 'Waiting for HDFS')
    remove_state('hbase.installed')


@when('bigtop.available', 'zookeeper.ready', 'hadoop.hdfs.ready')
def installing_hbase(zk, hdfs):
    zks = zk.zookeepers()
    if is_state('hbase.installed') and (not data_changed('zks', zks)):
        return

    msg = "Configuring HBase" if is_state('hbase.installed') else "Installing HBase"
    hookenv.status_set('waiting', msg)
    distcfg = get_dist_config()
    hbase = HBase(distcfg)

    hosts = {}
    nns = hdfs.namenodes()
    hosts['namenode'] = nns[0]
    hbase.configure(hosts, zks)
    set_state('hbase.installed')
    hookenv.status_set('active', 'Ready')


@when('hbase.installed', 'hbclient.joined')
def serve_client(client):
    config = get_dist_config()
    master_port = config.port('hbase-master')
    regionserver_port = config.port('hbase-region')
    thrift_port = config.port('hbase-thrift')
    client.send_port(master_port, regionserver_port, thrift_port)
