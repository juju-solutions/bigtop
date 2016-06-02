#!/usr/bin/env python3

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Apache Kafka.
    """

    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='trusty')
        cls.d.add('kafka', 'kafka')
        cls.d.add('jdk', 'openjdk')
        cls.d.add('zk', 'zookeeper')
        cls.d.relate('kafka:zookeeper', 'zk:zkclient')
        cls.d.relate('kafka:java', 'jdk:java')
        cls.d.relate('zk:java', 'jdk:java')

        cls.d.setup(timeout=900)
        cls.d.sentry.wait(timeout=1800)
        cls.unit = cls.d.sentry['kafka'][0]
        cls.d.sentry.wait_for_messages({'kafka': 'Ready'})

    def test_deploy(self):
        output, retcode = self.unit.run("pgrep -a java")
        assert 'Kafka' in output, "Kafka daemon is not started"


if __name__ == '__main__':
    unittest.main()
