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
# Apache Spark

This bundle provides a complete deployment of the processing components using
[Apache Spark](https://spark.apache.org/) in standalone HA mode as packaged
by [Apache Bigtop](http://bigtop.apache.org/).
These components include:

  * Spark (3 units) in HA mode
  * Zookeeper (3 units)

In addition to monitoring facilities offered by Spark (the job history server)
this bundle pairs Spark with an ELK stack (Elasticsearch-Logstash-Kibana)
in order to analyse Spark logs.

Deploying this bundle gives you a fully configured and connected Apache Spark
cluster on any supported cloud, which can be easily scaled to meet workload
demands.


## Deploying this bundle

In this deployment, the aforementioned components are deployed on separate
units. To deploy this bundle, simply use:

    juju deploy spark-processing

This will deploy this bundle and all the charms from the [charm store][].

> Note: With Juju versions < 2.0, you will need to use [juju-deployer][] to
deploy the bundle.

The default bundle deploys three Spark nodes. To scale the cluster, use:

    juju add-unit spark -n 2

This will add two additional Spark nodes, for a total of five.

[charm store]: https://jujucharms.com/
[juju-deployer]: https://pypi.python.org/pypi/juju-deployer/

### Verify the deployment

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with `watch` to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The Spark charm provides a `smoke-test` action that can be used to verify that
it functions as expected:

    juju action do spark/0 smoke-test
    watch -n 0.5 juju action status

Eventually, the action should settle to `status: completed`.  If not
then it means that component is not working as expected.
You can get more information about that component's smoke test:

    juju action fetch <action-id>

Using Spark job history server you can inspect the status of the curently running jobs
as well as the ones finished. The Spark and system logs of the Spark nodes are collected
and indexed at the Elasticsearch node. By navigatng to http://<kibana-host> you gain
access to the log analysis facilities of this bundle.

## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
