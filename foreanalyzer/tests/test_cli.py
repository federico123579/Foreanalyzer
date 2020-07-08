"""
tests.test_cli
~~~~~~~~~~~~~~

Test the cli module.
"""

from click.testing import CliRunner

from foreanalyzer.cli import CliConsole
from foreanalyzer.cli import main, run, config


def test_main():
    """test main command"""
    runner = CliRunner()
    res = runner.invoke(config)
    assert res.exit_code == 0
    CliConsole().debug(res.output)
