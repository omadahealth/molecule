#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import glob
import os

import sh

from molecule import ansible_playbook
from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Testinfra(base.Base):
    def __init__(self, molecule):
        super(Testinfra, self).__init__(molecule)
        self._options = self._get_options()

    @property
    def testdir(self):
        return self._options.get('testdir')

    def execute(self, exit=True):
        options = self._options
        options = options.get('options')

        tests_glob = self._get_tests()
        if len(tests_glob) > 0:
            self._flake8(tests_glob)
            self._testinfra(tests_glob, **testinfra_options)

    def _testinfra(self,
                   tests,
                   debug=False,
                   env=os.environ.copy(),
                   out=LOG.info,
                   err=LOG.error,
                   **kwargs):
        """
        Runs testinfra and returns a sh response object.

        :param tests: List of testinfra tests.
        :param debug: Pass debug flag to testinfra.
        :param env: Environment to pass to underlying sh call.
        :param out: Function to process STDOUT for underlying sh call.
        :param err: Function to process STDERR for underlying sh call.
        :return: sh response object
        """
        kwargs['debug'] = debug
        kwargs['_env'] = env
        kwargs['_out'] = out
        kwargs['_err'] = err

<<<<<<< 427f6ba9b9a4d9a4d3dd1b289f8b4e50a141d3a9
        msg = 'Executing testinfra tests found in {}/.'.format(
            self._testinfra_dir)
=======
        if 'HOME' not in kwargs['_env']:
            kwargs['_env']['HOME'] = os.path.expanduser('~')

        msg = 'Executing testinfra tests found in {}/.'.format(self.testdir)
>>>>>>> Created a verify section of the config
        util.print_info(msg)

        return sh.testinfra(tests, **kwargs)

    def _flake8(self, tests, out=LOG.info, err=LOG.error):
        """
        Runs flake8 against specified tests.

        :param tests: List of testinfra tests.
        :param out: Function to process STDOUT for underlying sh call.
        :param err: Function to process STDERR for underlying sh call.
        :return: sh response object.
        """
        msg = 'Executing flake8 on *.py files found in {}/.'.format(
            self._testinfra_dir)
        util.print_info(msg)

        return sh.flake8(tests)

    def _get_tests(self):
        tests = '{}/test_*.py'.format(self.testdir)

        return glob.glob(tests)

    def _get_options(self):
        return util.merge_dicts(self._get_default_options(),
                                self._molecule.config.verifier_options)

    def _get_default_options(self):
        m = self._molecule
        mc = m.config.config['ansible']
        ansible = ansible_playbook.AnsiblePlaybook(mc, _env=m._env)

        try:
            dd = self._molecule.driver.testinfra_args
        except AttributeError:
            dd = {}
        defaults = {
            'testdir': 'tests',
            'options': {
                'env': ansible.env,
                'debug': m._args.get('--debug', False),
                'sudo': m._args.get('--sudo', False)
            }
        }
        defaults['options'].update(dd)

        return defaults
