#!/usr/bin/env python3

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Apache Bigtop Pig.
    """

    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='trusty')
        cls.d.add('pig', 'pig')
        cls.d.add('jdk', 'openjdk')
        cls.d.relate('pig:java', 'jdk:java')

        cls.d.setup(timeout=900)
        cls.d.sentry.wait(timeout=1800)
        cls.unit = cls.d.sentry['pig'][0]


if __name__ == '__main__':
    unittest.main()
