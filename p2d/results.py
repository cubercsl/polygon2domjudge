from . import config


class ResultConfigError(Exception):
    """Exception class for errors in result configuration."""
    pass


class Result(object):
    """
    Class representing a single result.
    """

    __RESULTS = ['accepted', 'wrong_answer', 'time_limit_exceed', 'run_time_error']

    def __init__(self, result_name, tags_list):
        """Construct result object

        Args:
            result_name (str): tag name
            tags_list (list): list containing the polygon tags.
        """
        if result_name not in Result.__RESULTS:
            raise ResultConfigError('Invalid Result Name "%s"' % result_name)
        self.result_name = result_name
        self.tags = tags_list


class Results(object):
    """A set of results."""

    def __init__(self, data=None):
        """Create a set of results from a dict.
        Args:
            data (dict): dictonary containing configuration.
                If None, resulting set of results is empty.
                See documentation of update() method below for details.
        """
        self.results = {}
        self.tags = {}
        if data is not None:
            self.update(data)

    def update(self, data):
        """Update the set with result configuration data from a dict.
        Args:
            data (dict): dictionary containing configuration.
                If this dictionary contains (possibly partial) configuration
                for a result already in the set, the configuration
                for that result will be overridden and updated.
        """
        if not isinstance(data, dict):
            raise ResultConfigError('Config file error: content must be a dictionary, but is %s.' % (type(data)))

        for (result_name, tags_list) in data.items():
            if not isinstance(result_name, str):
                raise ResultConfigError('Config file error: result names must be strings, but %s is %s.' %
                                        (result_name, type(result_name)))
            if not isinstance(tags_list, list):
                raise ResultConfigError('Config file error: tags list must be a list, but tags of result %s is %s.' %
                                        (result_name, type(tags_list)))

            if result_name not in self.results:
                self.results[result_name] = Result(result_name, tags_list)
            else:
                self.results[result_name].tags = tags_list

        self.tags.clear()
        for (result_name, result) in self.results.items():
            for tag in result.tags:
                if tag in self.tags.keys():
                    raise ResultConfigError('Result %s and %s both have tag %s.' % (result_name, self.tags[tag], tag))
                self.tags[tag] = result_name


def load_result_config():
    """Load result configuration.
    Returns:
        Results object for the set of results.
    """
    return Results(config.load_config('results.yaml'))
