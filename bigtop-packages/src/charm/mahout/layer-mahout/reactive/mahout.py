from charms.reactive import when, when_not, is_state, set_state
from charms.layer.apache_bigtop_base import Bigtop
from charmhelpers.core import hookenv


@when('bigtop.available')
@when_not('mahout.intalled')
def install_mahout():
    hookenv.status_set('maintenance', 'installing Mahout')
    bigtop = Bigtop()
    bigtop.render_site_yaml(
        roles=[
            'mahout-client',
        ],
    )
    bigtop.trigger_puppet()
    hookenv.status_set('active', 'ready')
    set_state('mahout.installed')
