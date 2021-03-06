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

import abc
import docopt

from molecule import core
from molecule import util

LOG = util.get_logger(__name__)


class InvalidHost(Exception):
    """
    Exception class raised when an error occurs in :class:`.Login`.
    """
    pass


class Base(object):
    """
    An abstract base class used to define the command interface.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, command_args, args, molecule=False):
        """
        Base initializer for all :ref:`Command` classes.

        :param command_args: A list of aruments passed to the subcommand from
         the CLI.
        :param args: A dict of options, arguments and commands from the CLI.
        :param molecule: An optional instance of molecule.
        :returns: None
        """
        self.args = docopt.docopt(self.__doc__, argv=command_args)
        self.args['<command>'] = self.__class__.__name__.lower()
        self.command_args = command_args

        if not molecule:
            self.molecule = core.Molecule(self.args)
            self.main()
        else:
            self.molecule = molecule

    def main(self):
        """
        A mechanism to initialize molecule by calling its main method.  This
        can be redefined by classes which do not want this behavior
        (:class:`.Init`).

        :returns: None
        """
        c = self.molecule.config
        if not c.molecule_file_exists():
            msg = 'Unable to find {}. Exiting.'
            LOG.error(msg.format(c.molecule_file))
            util.sysexit()
        self.molecule.main()

    @abc.abstractproperty
    def execute(self):  # pragma: no cover
        pass
