#!/usr/bin/env python3

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

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Apache HBase.
    """
    def setUp(self):
        self.d = amulet.Deployment(series='trusty')
        self.d.add('hbase', 'hbase')
        self.d.add('zk', 'zookeeper')
        self.d.add('namenode', 'hadoop-namenode')
        self.d.add('slave', 'hadoop-slave')
        self.d.add('plugin', 'hadoop-plugin')
        self.d.add('openjdk', 'openjdk')

        self.d.relate('hbase:zookeeper', 'zk:zkclient')
        self.d.relate('plugin:hadoop-plugin', 'hbase:hadoop')
        self.d.relate('plugin:namenode', 'namenode:namenode')
        self.d.relate('slave:namenode', 'namenode:datanode')

        self.d.relate('hbase:java', 'openjdk:java')
        self.d.relate('plugin:java', 'openjdk:java')
        self.d.relate('namenode:java', 'openjdk:java')
        self.d.relate('slave:java', 'openjdk:java')
        self.d.relate('zk:java', 'openjdk:java')

        self.d.setup(timeout=1800)
        self.d.sentry.wait(timeout=1800)

    def test_deploy(self):
        self.d.sentry.wait_for_messages({"hbase": "ready"})
        hbase = self.d.sentry['hbase'][0]
        smk_uuid = hbase.action_do("smoke-test")
        output = self.d.get_action_output(smk_uuid)
        assert "Summary of timings" in output['meta']['raw']


if __name__ == '__main__':
    unittest.main()
