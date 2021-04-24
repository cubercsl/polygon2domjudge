import logging
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree
from argparse import ArgumentParser

import yaml

from . import checkers
from . import misc
from . import problems
from . import results
from ._version import __version__


class ProcessError(Exception):
    pass


class ProblemAspect:
    errors = 0
    warnings = 0
    basename_regex = re.compile('^[a-zA-Z0-9][a-zA-Z0-9_.-]*[a-zA-Z0-9]$')

    def error(self, msg):
        ProblemAspect.errors += 1
        logging.error('in %s: %s', self, msg)
        raise ProcessError(msg)

    def warning(self, msg):
        if ProblemAspect.consider_warnings_errors:
            self.error(msg)
            return
        ProblemAspect.warnings += 1
        logging.warning('in %s: %s', self, msg)

    def msg(self, msg):
        print(msg)

    def info(self, msg):
        logging.info(': %s', msg)

    def debug(self, msg):
        logging.debug(': %s', msg)

    def check_basename(self, path):
        basename = os.path.basename(path)
        if not self.basename_regex.match(basename):
            self.error("Invalid name '%s' (should match '%s')" % (basename, self.basename_regex.pattern))


class ProblemConfig(ProblemAspect):
    __DEFAULT_CONFIG = problems.Problem('DEFAULT', {
        'probid': 'PROB01',
        'color': '#000000',
        'samples': 1
    })

    def __init__(self, problem):
        self.debug('Parse \'problem.xml\'')
        self._problem = problem
        self.configfile = os.path.join(problem.probdir, 'problem.xml')
        self._data = None
        if os.path.isfile(self.configfile):
            config = Problem.problem_config.problems.get(problem.shortname)
            if config is None:
                self.warning('Can not find config of %s, use default.' % problem.shortname)
                config = ProblemConfig.__DEFAULT_CONFIG
            self._data = xml.etree.ElementTree.parse(self.configfile)
            self.name = self._data.find('names').find('name').attrib['value']
            self.timelimit = str(float(self._data.find('judging').find('testset').find('time-limit').text) / 1000.0)
            self.checker = self._data.find('assets').find('checker')
            self.interactor = self._data.find('assets').find('interactor')
            self.probid = config.probid
            self.color = config.color
            self.samples = config.samples
            self.validation = config.validation
            self.validator_flags = config.validator_flags
            self.debug('Problem Name: %s' % self.name)
            self.debug('Time Limit: %s' % self.timelimit)

    def __str__(self):
        return 'problem configuration'

    def process(self):
        self.info('Add \'domjudge-problem.ini\'')
        ini_file = os.path.join(self._problem.tmpdir, 'domjudge-problem.ini')
        ini_content = [
            '  probid = %s' % self.probid,
            '  name = %s' % self.name.replace("'", "`"),
            '  timelimit = %s' % self.timelimit,
            '  color = %s' % self.color
        ]
        [*map(self.info, ini_content)]
        with open(ini_file, 'w', encoding='utf-8') as f:
            f.writelines(map(lambda s: s.strip() + '\n', ini_content))


class ProblemStatement(ProblemAspect):

    def __init__(self, problem):
        raise NotImplementedError
    # TODO


class OutputValidator(ProblemAspect):

    def __init__(self, problem):
        self._problem = problem
        if problem.config.validation is not None:
            if problem.config.validation == 'default':
                self._source = None
            elif problem.config.validation == 'custom' and problem.config.checker is not None:
                self._source = os.path.join(problem.probdir, problem.config.checker.find('source').attrib['path'])
            elif problem.config.validation == 'custom interactive' and problem.is_interactive:
                self._source = os.path.join(problem.probdir, problem.config.interactor.find('source').attrib['path'])
            else:
                self.error('No checker/interactor found')
        else:
            if problem.is_interactive:
                self._source = os.path.join(problem.probdir, problem.config.interactor.find('source').attrib['path'])
            elif problem.config.checker is not None:
                self._source = os.path.join(problem.probdir, problem.config.checker.find('source').attrib['path'])
            else:
                self.error('No checker/interactor found')

    def __str__(self):
        return 'output validators'

    def process(self):
        self.info('Add output validator')
        if not self._source.endswith('.cpp'):
            self.error('only support checker/interactor written with testlib.')
        testlib = Problem.misc_config.testlib
        data = {}
        with open(os.path.join(self._problem.tmpdir, 'problem.yaml'), 'w', encoding='utf-8') as yaml_file:
            if self._problem.is_interactive:
                self.info('Use custom interactor')
                data['validation'] = 'custom interactive'
                yaml.safe_dump(data, yaml_file)
                self._problem.ensure_dir('output_validators', 'interactor')
                shutil.copyfile(testlib, os.path.join(self._problem.tmpdir,
                                                      'output_validator', 'interactor', 'testlib.h'))
                shutil.copyfile(self._source, os.path.join(self._problem.tmpdir,
                                                           'output_validator', 'interactor', 'interactor.cpp'))
            else:
                checker_name = Problem.checker_config.detect_checker(self._source)
                if self._source is None:
                    self.info('  Use default checker')
                    data['validation'] = 'default'
                    if self._problem.config.validator_flags is not None:
                        data['validator_flags'] = self._problem.config.validator_flags
                    yaml.safe_dump(data, yaml_file, default_flow_style=False)
                elif checker_name is not None:
                    self.info('  find std checker: std::%s' % checker_name)
                    data['validation'] = 'default'
                    validator_flags = Problem.checker_config.checkers[checker_name].validator_flags
                    if validator_flags is not None:
                        data['validator_flags'] = validator_flags
                    yaml.safe_dump(data, yaml_file, default_flow_style=False)
                else:
                    self.info('Use custom checker')
                    data['validation'] = 'custom'
                    yaml.safe_dump(data, yaml_file, default_flow_style=False)
                    self._problem.ensure_dir('output_validators', 'checker')
                    shutil.copyfile(testlib, os.path.join(self._problem.tmpdir,
                                                          'output_validator', 'checker', 'testlib.h'))
                    shutil.copyfile(self._source, os.path.join(self._problem.tmpdir,
                                                               'output_validator', 'checker', 'interactor.cpp'))


class TestCases(ProblemAspect):

    def __init__(self, problem):
        self._problem = problem
        if problem.config.samples >= 100:
            self.error('Too many samples')
        self._samples = ['{0:02d}'.format(i + 1) for i in range(problem.config.samples)]
        self._tests = os.path.join(problem.probdir, 'tests')

    def __str__(self):
        return 'test cases'

    def _check_newlines(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
        if data.find('\r') != -1:
            self.warning('The file %s contains non-standard line breaks.' % filename)
        if len(data) > 0 and data[-1] != '\n':
            self.warning("The file %s does not end with '\\n'." % filename)

    def process(self):
        self.info('Add tests')
        self._problem.ensure_dir('data', 'sample')
        self._problem.ensure_dir('data', 'secret')

        for test in filter(lambda x: not x.endswith(Problem.misc_config.out), os.listdir(self._tests)):
            input_src = os.path.join(self._tests, test)
            output_src = os.path.join(self._tests, test + Problem.misc_config.out)
            self._check_newlines(input_src)
            self._check_newlines(output_src)
            if test in self._samples:
                input_dst = os.path.join(self._problem.tmpdir, 'data', 'sample', '%s.in' % test)
                output_dst = os.path.join(self._problem.tmpdir, 'data', 'sample', '%s.ans' % test)
                self.info('  sample: %s.(in/ans)' % test)
            else:
                input_dst = os.path.join(self._problem.tmpdir, 'data', 'secret', '%s.in' % test)
                output_dst = os.path.join(self._problem.tmpdir, 'data', 'secret', '%s.ans' % test)
                self.info('  secret: %s.(in/ans)' % test)
            try:
                shutil.copyfile(input_src, input_dst)
                shutil.copyfile(output_src, output_dst)
            except FileNotFoundError:
                self.error('data not found')


class Submissions(ProblemAspect):

    def __init__(self, problem):
        self._problem = problem
        self._submissions = os.path.join(problem.probdir, 'solutions')

    def __str__(self):
        return 'submissions'

    def __get_submission(self, desc):
        result = {}
        desc_file = os.path.join(self._submissions, desc)
        with open(desc_file, 'r', encoding='utf-8') as f:
            for _ in f.readlines():
                key, value = _.strip().split(': ', maxsplit=2)
                if key == 'File name':
                    result[key] = value
                elif key == 'Tag':
                    if value not in Problem.result_config.tags.keys():
                        self.warning('Unknown tag: %s, treat as \'accepted\'')
                    result[key] = Problem.result_config.tags.get(value, 'accepted')
        if not ('File name' in result.keys() or 'Tag' in result.keys()):
            self.error('The description file %s has error.' % os.path.basename(desc_file))
        return result['File name'], result['Tag']

    def process(self):
        self.info('Add jury solutions')
        for result in Problem.result_config.results.keys():
            self._problem.ensure_dir('submissions', result)

        for desc in filter(lambda x: x.endswith(Problem.misc_config.desc), os.listdir(self._submissions)):
            submission, result = self.__get_submission(desc)
            src = os.path.join(self._submissions, submission)
            dst = os.path.join(self._problem.tmpdir, 'submissions', result, submission)
            try:
                shutil.copyfile(src, dst)
                self.info('  %s (Expected Result: %s)' % (submission, result))
            except FileNotFoundError:
                self.error('submission not found')


class Problem(ProblemAspect):
    problem_config = None
    checker_config = checkers.load_checker_config()
    result_config = results.load_result_config()
    misc_config = misc.load_misc_config()

    def __init__(self, probdir):
        self.probdir = os.path.realpath(probdir)
        self.shortname = os.path.basename(probdir)
        # self.check_basename(self.shortname)

    def __enter__(self):

        ProblemAspect.errors = 0
        ProblemAspect.warnings = 0

        self.tmpdir = tempfile.mkdtemp(prefix='%s-domjudge' % self.shortname)
        if not os.path.isdir(self.probdir):
            self.error("Problem directory '%s' not found" % self.probdir)
            self.shortname = None
            return self

        try:
            # self.statement = ProblemStatement(self)
            self.config = ProblemConfig(self)
            self.is_interactive = self.config.interactor is not None
            self.output_validator = OutputValidator(self)
            self.testdata = TestCases(self)
            self.submissions = Submissions(self)
        except Exception: # maybe the directory is not a valid problem package
            self.shortname = None

        return self

    def __exit__(self, exc_type, exc_value, exc_trace_back):
        shutil.rmtree(self.tmpdir)

    def __str__(self):
        return self.shortname

    def ensure_dir(self, *paths):
        if not os.path.exists(os.path.join(self.tmpdir, *paths)):
            os.makedirs(os.path.join(self.tmpdir, *paths))

    def run(self, args=None):
        if self.shortname is None:
            return [1, 0]
        if args is None:
            args = default_args()

        try:
            part_mapping = {
                'config': self.config,
                # 'statement': self.statement,
                'validator': self.output_validator,
                'data': self.testdata,
                'submissions': self.submissions
            }
            for part in part_mapping.keys():
                self.msg('Add %s' % part)
                part_mapping[part].process()

            self.msg('Make archive')
            shutil.make_archive(self.shortname, 'zip', self.tmpdir)

        except ProcessError:
            pass

        return [ProblemAspect.errors, ProblemAspect.warnings]


def argparser():
    parser = ArgumentParser(description='Process Polygon Package to Domjudge Package.')
    parser.add_argument('problemsetdir', help='path of the polygon packages')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-l', '--log_level', default='info',
                        help='set log level (debug, info, warning, error, critical)')
    parser.add_argument('-e', '--werror', action='store_true', help='consider warnings as errors')
    return parser


def default_args():
    return argparser().parse_args([None])


def main():
    args = argparser().parse_args()

    fmt = "%(levelname)s %(message)s"

    logging.basicConfig(stream=sys.stdout, format=fmt, level=eval("logging." + args.log_level.upper()))

    ProblemAspect.consider_warnings_errors = args.werror
    total_errors = 0

    Problem.problem_config = problems.load_problem_config(os.path.realpath(args.problemsetdir))

    error_list = []
    for _ in os.listdir(args.problemsetdir):
        problemdir = os.path.join(args.problemsetdir, _)
        if os.path.isdir(problemdir):
            print('Loading problem %s' % os.path.basename(os.path.realpath(problemdir)))
            with Problem(problemdir) as prob:
                [errors, warnings] = prob.run(args)

                def p(x):
                    return '' if x == 1 else 's'

                print("%s finished: %d error%s, %d warning%s" %
                      (prob.shortname, errors, p(errors), warnings, p(warnings)))
                if errors:
                    error_list.append(os.path.basename(os.path.realpath(problemdir)))
                total_errors += errors

    if error_list:
        print('These problem got errors:')
        for item in error_list:
            print('  ' + item)

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
