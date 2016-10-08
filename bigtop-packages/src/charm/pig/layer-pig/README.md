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

Apache Pig is a platform for creating MapReduce programs used with Hadoop.
It consists of a high-level language (Pig Latin) for expressing data analysis
programs, coupled with infrastructure for evaluating these programs. Learn more
at [pig.apache.org](http://pig.apache.org).

This charm deploys the Pig component of the Apache Bigtop platform and
supports running Pig in two execution modes:

 * Local Mode: Pig runs using your local host and file system. Specify local
   mode using the -x flag: `pig -x local`
 * Mapreduce Mode: Pig runs using a Hadoop cluster and HDFS. This is the default
   mode; you can, optionally, specify it using the -x flag:
   `pig` or `pig -x mapreduce`


## Usage

This charm is intended to be deployed via the
[apache-analytics-pig](https://jujucharms.com/apache-analytics-pig) bundle:

    juju quickstart apache-analytics-pig

This will deploy the Apache Hadoop platform with Apache Pig available to
execute Pig Latin jobs on your data. Once deployment is complete, you can run
Pig in a variety of modes:

### Local Mode

Run Pig in local mode on the Pig unit with the following:

    juju ssh pig/0
    pig -x local

### MapReduce Mode

MapReduce mode is the default for Pig. To run in this mode, ssh to the Pig unit
and run pig as follows:

    juju ssh pig/0
    pig


## Status and Smoke Test

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with `watch` to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can perform a "smoke test"
to verify that Spark is working as expected using the built-in `smoke-test`
action:

    juju action do pig/0 smoke-test

After a few seconds or so, you can check the results of the smoke test:

    juju action status

You will see `status: completed` if the smoke test was successful, or
`status: failed` if it was not.  You can get more information on why it failed
via:

    juju action fetch <action-id>


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
