import os
import sys

from . import config


class TestConfigError(Exception):
    pass


class Tests(object):
    """Tests config object."""
    __KEYS = ['testlib', 'desc', 'out']

    def __init__(self, data):
        self.testlib = None
        self.desc = None
        self.out = None
        self.update(data)

    def update(self, values):
        # Check that all provided values are known keys
        for unknown in set(values) - set(Tests.__KEYS):
            raise TestConfigError('Unknown key "%s" in tests config.' % unknown)

        for (key, value) in values.items():
            # check type
            if key == 'testlib':
                if not isinstance(value, str):
                    raise TestConfigError('testlib path must be a string but is %s' % type(value))
            elif key == 'desc':
                if not isinstance(value, str):
                    raise TestConfigError('desc extension must be a string but is %s' % type(value))
            elif key == 'out':
                if not isinstance(value, str):
                    raise TestConfigError('output extension path must be a string but is %s' % type(value))

            self.__dict__[key] = value

        self.__check()

    @staticmethod
    def get_resource_path(res):
        if res is None:
            return []
        return [
            os.path.join(os.path.split(os.path.realpath(__file__))[0], 'res', res),
            os.path.join(os.getcwd(), res)
        ]

    def __check(self):
        testlib, self.testlib = self.testlib, None
        for res in Tests.get_resource_path(testlib):
            if os.path.isfile(res):
                self.testlib = res
        if self.testlib is None:
            raise TestConfigError('testlib has not found.')
        if self.desc is None:
            raise TestConfigError('desc extension has not found.')
        if self.out is None:
            raise TestConfigError('output extension has not found.')

            


def load_test_config():
    """Load test configuration.
    Returns: Tests object for tests config.
    """
    return Tests(config.load_config('tests.yaml'))
