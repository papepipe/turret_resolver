import os
import sys
import subprocess
import logging
from unittest import TestCase

import turret

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TurretResolverTest(TestCase):

    @staticmethod
    def _get_resolved_rez_variables(package, variable):
        system = sys.platform
        if system == "win32":
            rez_cmd = 'rez-env {} -- echo %{}%'.format(package, variable)
        else:
            rez_cmd = 'rez-env {} -- printenv {}'.format(package, variable)
        process = subprocess.Popen(rez_cmd, stdout=subprocess.PIPE, shell=True)
        rez_path, err = process.communicate()
        if err or not rez_path:
            raise ImportError(
                "Failed to find Rez as a package in the current "
                "environment! Try 'rez-bind rez'!")
        else:
            rez_path = '{}'.format(rez_path.strip().replace('\\', '/'))
        return rez_path

    def setUp(self):
        os.environ[
            'TK_PIPELINE_CONFIG_LOC'] = self._get_resolved_rez_variables(
            'xzh_config', 'TK_PIPELINE_CONFIG_LOC')
        os.environ[
            'TK_PIPELINE_CONFIG_FILE'] = self._get_resolved_rez_variables(
            'xzh_config', 'TK_PIPELINE_CONFIG_FILE')

    def test_resolve(self):
        path = turret.resolver.resolve(
            'tank://xzh/asset_usd_publish?Asset=room&Step=SUF&version=latest')
        _logger.info('Resolved path: {}'.format(path))
