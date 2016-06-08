from jujubigdata import utils
from charms.layer.apache_bigtop_base import Bigtop
from path import Path
from charmhelpers.core import unitdata
from charms import layer


class Pig(object):
    def __init__(self, dist_config):
        self.dist_config = dist_config #or utils.DistConfig(data=layer.options('apache-bigtop-base'))

    def install_pig(self):
        roles = ['hadoop-client']

        bigtop = Bigtop()
        bigtop.render_site_yaml(roles=roles)
        bigtop.trigger_puppet()

        roles = ['pig-client']

        bigtop.render_site_yaml(roles=roles)
        bigtop.trigger_puppet()

        pig_bin = self.dist_config.path('pig') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if pig_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], pig_bin])
            env['PIG_CONF_DIR'] = self.dist_config.path('pig_conf')
            env['PIG_HOME'] = self.dist_config.path('pig')
            env['HADOOP_CONF_DIR'] = self.dist_config.path('hadoop_conf')

    def configure_local(self):
        """In local mode, configure Pig with PIG_HOME as the classpath."""
        with utils.environment_edit_in_place('/etc/environment') as env:
            env['PIG_CLASSPATH'] = env['PIG_HOME']

    def configure_yarn(self):
        """In mapred mode, configure Pig with HADDOP_CONF as the classpath."""
        with utils.environment_edit_in_place('/etc/environment') as env:
            env['PIG_CLASSPATH'] = env['HADOOP_CONF_DIR']

