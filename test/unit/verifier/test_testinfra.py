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

import pytest

from molecule.verifier import testinfra


@pytest.fixture()
def testinfra_instance(molecule_instance):
    return testinfra.Testinfra(molecule_instance)


@pytest.fixture
def mocked_code_verifier(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._flake8')


@pytest.fixture
def mocked_test_verifier(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._testinfra')


@pytest.fixture
def mocked_get_tests(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._get_tests')

def test_testdir(testinfra_instance):
    assert 'tests' == testinfra_instance.testdir


def test_get_options(testinfra_instance):
    assert isinstance(testinfra_instance._get_options(), dict)


def test_get_default_options(molecule_instance, testinfra_instance):
    molecule_instance.config.config['ansible'] = {'inventory_file':
                                                  'test-inventory'}
    molecule_instance._env = {'FOO': 'BAR'}
    resp = testinfra_instance._get_default_options().get('options')

    assert not resp['debug']
    assert not resp['sudo']
    assert 'test-inventory' == resp['ansible-inventory']
    assert 'ansible' == resp['connection']

    assert '1' == resp['env']['PYTHONUNBUFFERED']
    assert 'BAR' == resp['env']['FOO']
    assert 'true' == resp['env']['ANSIBLE_FORCE_COLOR']


def test_execute(mocked_test_verifier, mocked_get_tests, testinfra_instance):
    molecule_instance._env = {'FOO': 'BAR'}
    mocked_test_stat.return_value = ['/test/1', '/test/2']
    testinfra_instance.execute()

    mocked_code_verifier.assert_called_once_with(['/test/1', '/test/2'])
    assert (['/test/1', '/test/2'], ) == mocked_test_verifier.call_args[0]

    ca = mocked_test_verifier.call_args[1]
    assert not ca['debug']
    assert not ca['sudo']
    assert 'test/inventory_file' == ca['ansible-inventory']
    assert 'ansible' == ca['connection']

    assert '1' == ca['env']['PYTHONUNBUFFERED']
    assert 'bar' == ca['env']['FOO']
    assert 'true' == ca['env']['ANSIBLE_FORCE_COLOR']
    assert 'test/config_file' == ca['env']['ANSIBLE_CONFIG']
    assert 'false' == ca['env']['ANSIBLE_HOST_KEY_CHECKING']
    assert 'false' == ca['env']['ANSIBLE_HOST_KEY_CHECKING']
    assert ('-o UserKnownHostsFile=/dev/null '
            '-o IdentitiesOnly=yes '
            '-o ControlMaster=auto '
            '-o ControlPersist=60s') == ca['env']['ANSIBLE_SSH_ARGS']


def test_execute_overriden_options(mocker, molecule_instance,
                                   testinfra_instance):
    mocked_test_stat = mocker.patch(
        'molecule.verifier.testinfra.Testinfra._get_tests')
    mocked_testinfra = mocker.patch(
        'molecule.verifier.testinfra.Testinfra._testinfra')

    mocked_test_stat.return_value = ['/test/1', '/test/2']
    molecule_instance.config.config['verifier']['options'] = {
        'sudo': True,
        'debug': True
    }
    testinfra_instance._options = testinfra_instance._get_options()
    testinfra_instance.execute()

    ca = mocked_testinfra.call_args[1]
    assert ca['debug']
    assert ca['sudo']


def test_execute_no_tests(mocked_code_verifier, mocked_test_verifier,
                          mocked_get_tests, testinfra_instance):
    mocked_get_tests.return_value = []
    testinfra_instance.execute()

    assert not mocked_code_verifier.called
    assert not mocked_test_verifier.called


def test_testinfra(mocker, mocked_get_tests, testinfra_instance):
    mocked = mocker.patch('sh.testinfra')
    args = ['/tmp/ansible-inventory']
    kwargs = {'debug': True, 'out': None, 'err': None}
    testinfra_instance._testinfra(*args, **kwargs)

    assert ('/tmp/ansible-inventory', ) == mocked.call_args[0]

    ca = mocked.call_args[1]
    assert ca.get('debug')


def test_flake8(mocker, testinfra_instance):
    mocked = mocker.patch('sh.flake8')
    args = ['test1.py', 'test2.py']
    testinfra_instance._flake8(args)

    mocked.assert_called_once_with(args)


def test_get_tests(testinfra_instance):
    assert [] == testinfra_instance._get_tests()
