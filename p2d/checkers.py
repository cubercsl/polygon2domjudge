import re

from . import config


class CheckerConfigError(Exception):
    """Exception class for errors in checker configuration."""
    pass


class Checker(object):
    """
    Class representing a single checker.
    """

    __KEYS = ['checker_name', 'md5sum', 'validator_flags']

    def __init__(self, checker_name, checker_spec):
        """Construct checker object

        Args:
            checker_name (str): checker name
            checker_spec (dict): dictionary containing the specification
                of the checker. 
        """
        if not re.match(r'\w', checker_name):
            raise CheckerConfigError('Invalid Checker Name "%s"' % checker_name)
        self.checker_name = checker_name
        self.md5sum = None
        self.validator_flags = None
        self.update(checker_spec)

    def update(self, values):
        """Update a checker specification with new values.
        Args:
            values (dict): dictionary containing new values for some
                subset of the checker properties.
        """
        # Check that all provided values are known keys
        for unknown in set(values) - set(Checker.__KEYS):
            raise CheckerConfigError('Unknown key "%s" specified for checker %s' % (unknown, self.checker_name))

        for (key, value) in values.items():
            # Check type
            if key == 'md5sum':
                if not isinstance(value, str):
                    raise CheckerConfigError('Checker %s: md5sum must be a string but is %s.' %
                                             (self.checker_name, type(value)))
                elif len(value) != 32:
                    raise CheckerConfigError('Checker %s: md5sum is invalid.' % self.checker_name)

            elif key == 'validator_flags':
                if not isinstance(value, str):
                    raise CheckerConfigError('Checker %s: validator flags must be a string but is %s.' %
                                             (self.checker_name, type(value)))

            self.__dict__[key] = value

        self.__check()

    def __check(self):
        """Check that the checker specification is valid(all mandatory
        fields provided).
        """
        if self.md5sum is None:
            raise CheckerConfigError('Checker %s has no md5 sum' % self.checker_name)


class Checkers(object):
    """A set of checkers."""

    def __init__(self, data=None):
        """Create a set of checkers from a dict.
        Args:
            data (dict): dictonary containing configuration.
                If None, resulting set of checkers is empty.
                See documentation of update() method below for details.
        """
        self.checkers = {}
        self.md5sums = {}
        if data is not None:
            self.update(data)

    def update(self, data):
        """Update the set with checker configuration data from a dict.
        Args:
            data (dict): dictionary containing configuration.
                If this dictionary contains (possibly partial) configuration
                for a checker already in the set, the configuration
                for that checker will be overridden and updated.
        """
        if not isinstance(data, dict):
            raise CheckerConfigError('Config file error: content must be a dictionary, but is %s.' % (type(data)))

        for (checker_name, checker_spec) in data.items():
            if not isinstance(checker_name, str):
                raise CheckerConfigError('Config file error: checker names must be strings, but %s is %s.' % (
                    checker_name, type(checker_name)))

            if not isinstance(checker_spec, dict):
                raise CheckerConfigError('Config file error: checker spec must be a dictionary, but spec of checker %s is %s.'
                                         % (checker_name, type(checker_spec)))

            if checker_name not in self.checkers:
                self.checkers[checker_name] = Checker(checker_name, checker_spec)
            else:
                self.checkers[checker_name].update(checker_spec)

        self.md5sums.clear()
        for (checker_name, checker) in self.checkers.items():
            if checker.md5sum in self.md5sums:
                raise CheckerConfigError('Checkers %s and %s both have md5sum %s.' %
                                         (checker_name, self.md5sums[checker.md5sum], checker.md5sum))
            self.md5sums[checker.md5sum] = checker_name


def load_checker_config():
    """Load checker configuration.
    Returns:
        Checkers object for the set of checkers.
    """
    return Checkers(config.load_config('checkers.yaml'))
