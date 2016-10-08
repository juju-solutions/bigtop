#!/usr/bin/env python3

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
        self.d.add('jdk', 'openjdk')

        self.d.relate('hbase:zookeeper', 'zk:zkclient')
        self.d.relate('plugin:hadoop-plugin', 'hbase:hadoop')
        self.d.relate('plugin:namenode', 'namenode:namenode')
        self.d.relate('slave:namenode', 'namenode:datanode')

        self.d.relate('hbase:java', 'jdk:java')
        self.d.relate('plugin:java', 'jdk:java')
        self.d.relate('namenode:java', 'jdk:java')
        self.d.relate('slave:java', 'jdk:java')
        self.d.relate('zk:java', 'jdk:java')

        self.d.setup(timeout=1800)
        self.d.sentry.wait(timeout=1800)

    def test_deploy(self):
        self.d.sentry.wait_for_messages({"hbase": "Ready"})
        hbase = self.d.sentry['hbase'][0]
        smk_uuid = hbase.action_do("smoke-test")
        output = self.d.get_action_output(smk_uuid)
        assert "Summary of timings" in output['meta']['raw']


if __name__ == '__main__':
    unittest.main()