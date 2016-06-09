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
        cls.pig = cls.d.sentry['pig'][0]

    def smoke_test(self):
        """Smoke test validates Pig is working in local or yarn mode."""
        unit_name = self.pig.info['unit_name']
        uuid = self.d.action_do(unit_name, 'smoke-test')
        result = self.d.action_fetch(uuid)
        # pig smoke-test sets outcome=success on success
        if (result['outcome'] != "success"):
            error = "Pig smoke-test failed"
            amulet.raise_status(amulet.FAIL, msg=error)


if __name__ == '__main__':
    unittest.main()
