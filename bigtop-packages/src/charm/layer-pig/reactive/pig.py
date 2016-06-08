from charmhelpers.core import hookenv
from charms.layer.bigtop_pig import Pig
from charms.reactive import is_state, set_state, remove_state, when, when_not


@when('bigtop.available')
@when_not('pig.installed')
def install_pig():
    hookenv.status_set('maintenance', 'installing pig')
    pig = Pig()
    pig.install_pig()
    pig.initial_pig_config()
    set_state('pig.installed')


@when('bigtop.available', 'pig.installed')
@when_not('pig.available')
def configure_pig():
    hookenv.status_set('maintenance', 'configuring pig')
    pig = Pig()
    hadoop_ready = is_state('hadoop.ready')
    if hadoop_ready:
        hookenv.status_set('maintenance', 'configuring pig (mapreduce)')
        hookenv.log('YARN is ready, configuring Apache Pig in MapReduce mode')
        pig.configure_yarn()
        remove_state('pig.configured.local')
        set_state('pig.configured.yarn')
        hookenv.status_set('active', 'ready (mapreduce)')
        hookenv.log('Apache Pig is ready in MapReduce mode')
    else:
        hookenv.status_set('maintenance', 'configuring pig (local)')
        hookenv.log('YARN is not ready, configuring Pig in local mode')
        pig.configure_local()
        remove_state('pig.configured.yarn')
        set_state('pig.configured.local')
        hookenv.status_set('active', 'ready (local)')
        hookenv.log('Apache Pig is ready in local mode')


@when('pig.configured.yarn')
@when_not('hadoop.ready')
def reconfigure_local():
    configure_pig()


@when('pig.configured.local')
@when('hadoop.ready')
def reconfigure_yarn(hadoop):
    configure_pig()
