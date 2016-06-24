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

from charms.reactive import when, when_not
from charms.reactive import is_state, set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.bigtop_zeppelin import Zeppelin


@when('bigtop.available')
def report_status():
    hadoop_joined = is_state('hadoop.joined')
    hadoop_ready = is_state('hadoop.ready')
    hive_joined = is_state('hive.connected')
    hive_ready = is_state('hive.available')
    if not hadoop_joined:
        hookenv.status_set('blocked',
                           'waiting for relation to hadoop plugin')
    elif not hadoop_ready:
        hookenv.status_set('waiting',
                           'waiting for hadoop')
    elif hive_joined and not hive_ready:
        hookenv.status_set('waiting',
                           'waiting for hive')


@when('bigtop.available', 'hadoop.ready')
@when_not('zeppelin.installed')
def initial_setup(hadoop):
    hookenv.status_set('maintenance', 'installing zeppelin')
    zeppelin = Zeppelin()
    zeppelin.install()
    zeppelin.initial_zeppelin_config()
    zeppelin.copy_tutorial('flume-tutorial')
    zeppelin.copy_tutorial('hdfs-tutorial')
    # restart to re-index the notebooks
    zeppelin.restart()
    zeppelin.open_ports()
    set_state('zeppelin.installed')
    hookenv.status_set('active', 'ready')


@when('zeppelin.installed', 'hive.ready')
@when_not('zeppelin.hive.configured')
def configure_hive(hive):
    zeppelin = Zeppelin()
    zeppelin.configure_hive(hive)
    set_state('zeppelin.hive.configured')


@when('zeppelin.installed', 'zeppelin.hive.configured')
@when_not('hive.ready')
def unconfigure_hive():
    zeppelin = Zeppelin()
    zeppelin.configure_hive(None)
    remove_state('zeppelin.hive.configured')


@when('zeppelin.installed', 'spark.ready')
@when_not('zeppelin.spark.configured')
def configure_spark(spark):
    zeppelin = Zeppelin()
    zeppelin.configure_spark(spark)
    set_state('zeppelin.spark.configured')


@when('zeppelin.installed', 'zeppelin.spark.configured')
@when_not('spark.ready')
def unconfigure_spark():
    zeppelin = Zeppelin()
    zeppelin.configure_spark(None)
    remove_state('zeppelin.spark.configured')


@when('zeppelin.installed')
@when_not('hadoop.ready')
def stop_zeppelin():
    zeppelin = Zeppelin()
    zeppelin.stop()
    zeppelin.close_ports()
    remove_state('zeppelin.installed')
