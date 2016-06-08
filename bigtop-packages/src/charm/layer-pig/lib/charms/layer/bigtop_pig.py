from jujubigdata import utils
from charms.layer.apache_bigtop_base import Bigtop
from charms import layer


class Pig(object):
    """
    This class manages Pig.
    :param DistConfig dist_config: The configuration container object needed.
    """
    def __init__(self, dist_config=None):
        self.dist_config = dist_config or utils.DistConfig(data=layer.options('apache-bigtop-base'))

    def install_pig(self):
        '''
        Trigger the Bigtop puppet recipe that handles the Pig service.
        '''
        # Dirs are handled by the bigtop deb. No need to call out to
        # dist_config to do that work.
        roles = ['pig-client']

        bigtop = Bigtop()
        bigtop.render_site_yaml(roles=roles)
        bigtop.trigger_puppet()

    def initial_pig_config(self):
        '''
        Configure system-wide pig bits.
        '''
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
