<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
## Overview

This bundle provides a complete deployment of the processing components using
[Apache Spark](https://spark.apache.org/) in standalone HA mode as packaged
by [Apache Bigtop](http://bigtop.apache.org/).
These components include:

  * Spark (3 units) in HA mode
  * Zookeeper (3 units)

In addition to monitoring facilities offered by Spark (the job history server)
this bundle pairs Spark with ganglia and rsyslog to monitor cluster health
and syslog activity.

Deploying this bundle gives you a fully configured and connected Apache Spark
cluster on any supported cloud, which can be easily scaled to meet workload
demands.


## Deploying

A working Juju installation is assumed to be present. If you have not yet set
up Juju, please follow the [getting-started][] instructions
prior to deploying this bundle. Once ready, deploy this bundle with the
`juju deploy` command:

    juju deploy spark-processing

_**Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, use [juju-quickstart](https://launchpad.net/juju-quickstart) with the
following syntax: `juju quickstart spark-processing`._

You can also build all of the charms from their source layers in the
[Bigtop charm repository][].  See the [Bigtop charm README][] for instructions
on building and deploying these charms locally.

[getting-started]: https://jujucharms.com/docs/2.0/getting-started
[Bigtop charm repository]: https://github.com/apache/bigtop/tree/master/bigtop-packages/src/charm
[Bigtop charm README]: https://github.com/apache/bigtop/blob/master/bigtop-packages/src/charm/README.md

## Verifying the deployment

### Status
The applications that make up this bundle provide status messages to
indicate when they are ready:

    juju status

This is particularly useful when combined with `watch` to track the on-going
progress of the deployment:

    watch -n 0.5 juju status

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can perform a smoke test
to verify that the bundle is working as expected.

### Smoke Test
The Spark charm provide a `smoke-test` action that can be used to verify the
application is functioning as expected. Run it with the following:

    juju run-action spark/0 smoke-test

_**Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is `juju action do spark/0 smoke-test`._

You can watch the progress of the smoke test action with:

    watch -n 0.5 juju show-action-status

_**Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is `juju action status`._

Eventually, the smoke test should settle to `status: completed`.  If
it reports `status: failed`, Spark is not working as expected. Get
more information about the smoke-test action

    juju show-action-output <action-id>

_**Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is `juju action fetch <action-id>`._


## Monitoring

This bundle includes Ganglia for system-level monitoring of the spark units.
Metrics are sent to a centralized ganglia unit for easy viewing in a browser.
To view the ganglia web interface, first expose the service:

    juju expose ganglia

Now find the ganglia public IP address:

    juju status ganglia

The ganglia web interface will be available at:

    http://GANGLIA_PUBLIC_IP/ganglia


## Logging

This bundle includes rsyslog to collect syslog data from the spark unit. These
logs are sent to a centralized rsyslog unit for easy syslog analysis. One
method of viewing this log data is to simply cat syslog from the rsyslog unit:

    juju run --unit rsyslog/0 'sudo cat /var/log/syslog'

You can also forward logs to an external rsyslog processing service. See
the *Forwarding logs to a system outside of the Juju environment* section of
the [rsyslog README](https://jujucharms.com/rsyslog/) for more information.


## Scaling

This bundle was designed to scale out. By default, three spark units are
deployed. To increase the amount of Spark workers, simply add more units. To
add one unit:

    juju add-unit spark

You can also add multiple units, for example, to add four more spark workers:

    juju add-unit -n4 spark


## Contact Information

- <bigdata@lists.ubuntu.com>


## Resources

- [Apache Bigtop](http://bigtop.apache.org/) home page
- [Apache Bigtop issue tracking](http://bigtop.apache.org/issue-tracking.html)
- [Apache Bigtop mailing lists](http://bigtop.apache.org/mail-lists.html)
- [Juju Bigtop charms](https://jujucharms.com/q/apache/bigtop)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
