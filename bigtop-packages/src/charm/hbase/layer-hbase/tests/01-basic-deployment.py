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
        self.d.setup(timeout=900)
        self.d.sentry.wait(timeout=1800)

    def test_deploy(self):
        self.d.sentry.wait_for_messages({"hbase": "Waiting on relation to Java"})


if __name__ == '__main__':
    unittest.main()
