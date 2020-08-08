# ~~~~ cli.py ~~~~
# forenalyzer.cli
# ~~~~~~~~~~~~~~~~

import os

import click

from foreanalyzer.console import CliConsole
from foreanalyzer.feeder import ZipFeeder01
from foreanalyzer.exceptions import NotConfigurated
import foreanalyzer.globals as glob
import foreanalyzer.utils as utils


# ~ * CONSTANTS * ~
INTERNAL_CONFIG_FILE = os.path.join(
    glob.OUTER_FOLDER_PATH, 'config.json')


# ~~~ * CLI COMMAND BUILDER * ~~~
@click.group()
@click.option('-v', '--verbose', default=0, show_default=True)
# TODO: add a limit to verbose level set to 3 [0,3]
@click.option('--algo')
def main(verbose, algo):
    """main controller"""
    CliConsole().verbose = verbose

@main.command()
def run():
    """run the analysis with config given
    load algo and works as earlier versions did"""
    # get configurations & settings
    config = utils.read_ext_config()
    if (config['USE_THIS'] == False and not
            os.path.isfile(INTERNAL_CONFIG_FILE)):
        raise NotConfigurated()
    elif config['USE_THIS'] == True:
        utils.write_int_config(config)
    config = utils.read_int_config()
    try:
        z = ZipFeeder01("EURUSD")
        z.process_dataframe()
    except KeyboardInterrupt:
        CliConsole().write("\nExiting...", "bold")
    finally:
        del z

def _check_instruments_parameter(value):
    str_instr = value.split(' ')
    for instr in str_instr:
        if instr not in glob.ACCEPTED_INSTRUMENTS:
            raise click.BadParameter("Instrument not accepted", param=instr)
    return str_instr


@main.command()
@click.option('--all', 'section', is_flag=True, flag_value="all",
              default="all", help="config all settings")
@click.option('-c', '--creds', 'section', is_flag=True, flag_value="creds",
              help="config only acount credentials")
@click.option('-a', '--account', 'section', is_flag=True, flag_value="acc",
              help="config only account settings")
@click.option('-g', '--algo', 'section', is_flag=True, flag_value="algo",
              help="config only algo setting")
def config(section):
    """set the internal configuration"""
    # get config file if present
    if os.path.isfile(INTERNAL_CONFIG_FILE):
        config = utils.read_int_config()
    else:
        config = {}
    # set credentials
    if section in ['all', 'creds']:
        CliConsole().write("# CREDENTIAL CONFIG #", "yellow", "bold")
        username = click.prompt("username")
        passwd = click.prompt("password", hide_input=True)
        CliConsole().debug(f"username: {username} - " +
                           f"password: {len(passwd)*'*'}")
        config['credentials'] = {'username': username, 'password': passwd}
    # set account settings
    if section in ['all', 'acc']:
        CliConsole().write("# ACCOUNT CONFIG #", "yellow", "bold")
        initial_config = click.prompt(
            "initial balance", default=1000, show_default=True)
        CliConsole().debug(f"initial money set: {initial_config}")
        count_margin = click.confirm("want to count margin?", default=False)
        sim_profit = click.confirm("want to simulate profit?", default=True)
        config['account'] = {
            'initial_config': initial_config, 'count_margin': count_margin,
            'simulate_profit': sim_profit}
    # setting algo settings
    if section in ['all', 'algo']:
        CliConsole().write("# ALGORITHM CONFIG #", "yellow", "bold")
        # instruments
        instruments = click.prompt(
            "instruments (codes separated by space)", default="EURUSD",
            show_default=True, value_proc=_check_instruments_parameter)
        if not isinstance(instruments, list): # uniform default EURUSD
            instruments = [instruments]
        CliConsole().debug(
            f"instruments set: {', '.join(instruments)}")
        # timeframe
        timeframe = click.prompt(
            "timeframe (in seconds)", default=300, show_default=True, type=int)
        CliConsole().debug(f"timeframe set: {timeframe}")
        config['account'] = {
            'instruments': instruments, 'timeframe': timeframe}
    # dump config data on internal config file
    utils.write_int_config(config)
    CliConsole().info("config data saved on internal json config file")
