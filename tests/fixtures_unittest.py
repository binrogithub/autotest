#!/usr/bin/python

import os
import re
import unittest


class fixture_config_test(unittest.TestCase):
    def test_fixture_contains_region_and_endpoint(self):
        fixture_path = os.path.join(
            os.path.dirname(__file__), 'fixtures', 'config.yaml')
        with open(fixture_path, 'r') as fixture_file:
            text = fixture_file.read()

        self.assertRegex(text, r'(?m)^region:\s*\S+')
        self.assertRegex(text, r'(?m)^endpoint:\s*$')
        self.assertRegex(text, r'(?m)^\s+base_domain:\s*\S+')


if __name__ == '__main__':
    unittest.main()
