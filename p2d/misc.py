import os

from . import config


class MiscConfigError(Exception):
    pass


class Misc(object):
    """Misc config object."""
    __KEYS = ['testlib', 'desc', 'out']

    def __init__(self, data):
        self.testliblib = None
        self.desc = None
        self.out = None
        self.update(data)

    def update(self, values):
        # Check that all provided values are known keys
        for unknown in set(values) - set(Misc.__KEYS):
            raise MiscConfigError('Unknown key "%s" in misc config.' % unknown)

        for (key, value) in values.items():
            # check type
            if key == 'testlib':
                if not isinstance(value, str):
                    raise MiscConfigError('testlib path must be a string but is %s' % type(value))
            elif key == 'desc':
                if not isinstance(value, str):
                    raise MiscConfigError('desc extension must be a string but is %s' % type(value))
            elif key == 'out':
                if not isinstance(value, str):
                    raise MiscConfigError('output extension path must be a string but is %s' % type(value))

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
        for res in Misc.get_resource_path(testlib):
            if os.path.isfile(res):
                self.testlib = res
        if self.testlib is None:
            raise MiscConfigError('testlib has not found.')
        if self.desc is None:
            raise MiscConfigError('desc extension has not found.')
        if self.out is None:
            raise MiscConfigError('output extension has not found.')


def load_misc_config():
    """Load misc configuration.
    Returns: Misc object for misc config.
    """
    return Misc(config.load_config('misc.yaml'))
