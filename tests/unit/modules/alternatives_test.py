# -*- coding: utf-8 -*-
'''
    tests.unit.modules.alternatives_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.
'''

# Import python libs
import os

# Import Salt Testing libs
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath, TestsLoggingHandler
ensure_in_syspath('../../')

# Import salt libs
from salt.modules import alternatives

# Import 3rd party libs
try:
    from mock import MagicMock, patch
    HAS_MOCK = True
except ImportError:
    HAS_MOCK = False


alternatives.__salt__ = {}
alternatives.__grains__ = {'os_family': 'RedHat'}


@skipIf(HAS_MOCK is False, 'mock python module is unavailable')
class AlternativesTestCase(TestCase):

    def test_display(self):
        with patch.dict(alternatives.__grains__, {'os_family': 'RedHat'}):
            mock = MagicMock(return_value={'retcode': 0, 'stdout': 'salt'})
            with patch.dict(alternatives.__salt__, {'cmd.run_all': mock}):
                solution = alternatives.display('better-world')
                self.assertEqual('salt', solution)
                mock.assert_called_once_with(
                    'alternatives --display better-world'
                )

        with patch.dict(alternatives.__grains__, {'os_family': 'Ubuntu'}):
            mock = MagicMock(
                return_value={'retcode': 0, 'stdout': 'undoubtedly-salt'}
            )
            with patch.dict(alternatives.__salt__, {'cmd.run_all': mock}):
                solution = alternatives.display('better-world')
                self.assertEqual('undoubtedly-salt', solution)
                mock.assert_called_once_with(
                    'update-alternatives --display better-world'
                )

    @patch('os.readlink')
    def test_show_current(self, os_readlink_mock):
        os_readlink_mock.return_value = '/etc/alternatives/salt'
        ret = alternatives.show_current('better-world')
        self.assertEqual('/etc/alternatives/salt', ret)
        os_readlink_mock.assert_called_once_with(
            '/etc/alternatives/better-world'
        )

        with TestsLoggingHandler() as handler:
            os_readlink_mock.side_effect = OSError('Hell was not found!!!')
            self.assertFalse(alternatives.show_current('hell'))
            os_readlink_mock.assert_called_with('/etc/alternatives/hell')
            self.assertIn('ERROR:alternatives: path /etc/alternatives/hell '
                          'does not exist',
                          handler.messages)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(AlternativesTestCase, needs_daemon=False)
