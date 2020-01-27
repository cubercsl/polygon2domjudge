import re

from . import config


class ProblemConfigError(Exception):
    """Exception class for errors in problem configuration."""
    pass


class Problem(object):
    """
    Class representing a single problem.
    """

    __KEYS = ['problem_name', 'probid', 'color', 'samples', 'validation', 'validator_flags']
    __VALIDATION = ['default', 'custom', 'custom interactive']

    def __init__(self, problem_name, problem_spec):
        """Construct problem object

        Args:
            problem_name (str): problem name
            problem_spec (dict): dictionary containing the specification
                of the problem.
        """
        if not re.match('^[a-zA-Z0-9][a-zA-Z0-9_.-]*[a-zA-Z0-9]$', problem_name):
            raise ProblemConfigError('Invalid Problem Name "%s"' % problem_name)
        self.problem_name = problem_name
        self.probid = None
        self.color = None
        self.samples = None
        self.validation = None
        self.validator_flags = None
        self.update(problem_spec)

    def update(self, values):
        """Update a problem specification with new values.
        Args:
            values (dict): dictionary containing new values for some
                subset of the problem properties.
        """
        # Check that all provided values are known keys
        for unknown in set(values) - set(Problem.__KEYS):
            raise ProblemConfigError('Unknown key "%s" specified for problem %s' % (unknown, self.problem_name))

        for (key, value) in values.items():
            # Check type
            if key == 'probid':
                if not isinstance(value, str):
                    raise ProblemConfigError('problem %s: problem code must be a string but is %s.' %
                                             (self.problem_name, type(value)))

            elif key == 'color':
                if not (isinstance(value, str) and re.match(r'#[A-Fa-f\d]{6}', value)):
                    raise ProblemConfigError('problem %s: problem color must be an RGB color but is %s.' %
                                             (self.problem_name, type(value)))
            elif key == 'samples':
                if not isinstance(value, int):
                    raise ProblemConfigError('problem %s: problem samples must be an integer but is %s.' %
                                             (self.problem_name, type(value)))
            elif key == 'validation':
                if not isinstance(value, str):
                    raise ProblemConfigError('problem %s: problem validation must be a string but is %s.' %
                                             (self.problem_name, type(value)))
                if value not in Problem.__VALIDATION:
                    raise ProblemConfigError('problem %s: unknown valudation %s.' % (self.problem_name, value))
            elif key == 'validator_flags':
                if not isinstance(value, str):
                    raise ProblemConfigError('problem %s: problem validator flags must be a string but is %s.' %
                                             (self.problem_name, type(value)))

            self.__dict__[key] = value

        self.__check()

    def __check(self):
        """Check that the problem specification is valid(all mandatory
        fields provided).
        """
        if self.probid is None:
            raise ProblemConfigError('problem %s has no probid' % self.problem_name)
        if self.color is None:
            raise ProblemConfigError('problem %s has no color' % self.problem_name)
        if self.samples is None:
            raise ProblemConfigError('problem %s has no sample' % self.problem_name)


class Problems(object):
    """A set of problems."""

    def __init__(self, data=None):
        """Create a set of problems from a dict.
        Args:
            data (dict): dictonary containing configuration.
                If None, resulting set of problems is empty.
                See documentation of update() method below for details.
        """
        self.problems = {}
        if data is not None:
            self.update(data)

    def update(self, data):
        """Update the set with problem configuration data from a dict.
        Args:
            data (dict): dictionary containing configuration.
                If this dictionary contains (possibly partial) configuration
                for a problem already in the set, the configuration
                for that problem will be overridden and updated.
        """
        if not isinstance(data, dict):
            raise ProblemConfigError('Config file error: content must be a dictionary, but is %s.' % (type(data)))

        for (problem_name, problem_spec) in data.items():
            if not isinstance(problem_name, str):
                raise ProblemConfigError('Config file error: problem names must be strings, but %s is %s.' % (
                    problem_name, type(problem_name)))

            if not isinstance(problem_spec, dict):
                raise ProblemConfigError('Config file error: problem spec must be a dictionary, but spec of problem %s is %s.'
                                         % (problem_name, type(problem_spec)))

            if problem_name not in self.problems:
                self.problems[problem_name] = Problem(problem_name, problem_spec)
            else:
                self.problems[problem_name].update(problem_spec)


def load_problem_config(rootdir):
    return Problems(config.load_config('problems.yaml', rootdir))
