#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import os
import sh

from molecule import util

LOG = util.get_logger(__name__)


class AnsiblePlaybook(object):
    def __init__(self, args, _env=None, _out=LOG.info, _err=LOG.error):
        """
        Sets up requirements for ansible-playbook, and returns None.

        :param args: A dict containing arguments to pass to ansible-playbook.
        :param _env: An optional environment to pass to underlying :func:`sh`
         call.
        :param _out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param _err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: None
        """
        self._playbook = None
        self._ansible = None
        self._cli = {}
        self._cli_pos = []
        self.env = _env if _env else os.environ.copy()

        # process arguments passed in (typically from molecule.yml's ansible block)
        for k, v in args.iteritems():
            self.parse_arg(k, v)

        # defaults can be redefined with call to add_env_arg() before baking
        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

        # passed through to sh, not ansible-playbook
        self.add_cli_arg('_out', _out)
        self.add_cli_arg('_err', _err)

    def bake(self):
        """
        Bake ansible-playbook command so it's ready to execute, and returns
        None.

        :return: None
        """
        self._ansible = sh.ansible_playbook.bake(
            self._playbook, *self._cli_pos, _env=self.env, **self._cli)

    def parse_arg(self, name, value):
        """
        Adds argument to CLI or environment, and returns None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """

        # skip `requirements_file` since it used by ansible-galaxy only
        if name == 'requirements_file':
            return

        if name == 'raw_env_vars':
            for k, v in value.iteritems():
                self.add_env_arg(k, v)
            return

        if name == 'host_key_checking':
            self.add_env_arg('ANSIBLE_HOST_KEY_CHECKING', str(value).lower())
            return

        if name == 'raw_ssh_args':
            self.add_env_arg('ANSIBLE_SSH_ARGS', ' '.join(value))
            return

        if name == 'config_file':
            self.add_env_arg('ANSIBLE_CONFIG', value)
            return

        if name == 'playbook':
            self._playbook = value
            return

        if name == 'host_vars' or name == 'group_vars':
            return

        # verbose is weird, must be -vvvv not verbose=vvvv
        if name == 'verbose' and value:
            # for cases where someone passes in verbose: True
            if value is True:
                value = 'vvvv'
            self._cli_pos.append('-' + value)
            return

        self.add_cli_arg(name, value)

    def add_cli_arg(self, name, value):
        """
        Adds argument to CLI passed to ansible-playbook, and returns None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        if value:
            self._cli[name] = value

    def remove_cli_arg(self, name):
        """
        Removes CLI argument, and returns None.

        :param name: A string containing the name of argument to be removed.
        :return: None
        """
        self._cli.pop(name, None)

    def add_env_arg(self, name, value):
        """
        Adds argument to environment passed to ansible-playbook, and returns
        None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        self.env[name] = value

    def remove_env_arg(self, name):
        """
        Removes environment argument, and returns None.

        :param name: A string containing the name of argument to be removed.
        :return: None
        """
        self.env.pop(name, None)

    def execute(self, hide_errors=False):
        """
        Executes ansible-playbook, and returns command's stdout.

        :param hide_errors: An optional bool to toggle output of errors.
        :return: The command's output, otherwise sys.exit on command failure.
        """
        if self._ansible is None:
            self.bake()

        try:
            return None, self._ansible().stdout
        except (sh.ErrorReturnCode, sh.ErrorReturnCode_2) as e:
            if not hide_errors:
                LOG.error('ERROR: {}'.format(e))

            return e.exit_code, None
