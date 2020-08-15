# ~~~~ cli.py ~~~~
# forenalyzer.cli
# ~~~~~~~~~~~~~~~~

import os

import click

import foreanalyzer.cache_optimization as cache
from foreanalyzer.console import CliConsole
from foreanalyzer.exceptions import NotConfigurated
import foreanalyzer.globals as glob
from foreanalyzer.plot_hanlder import PlotterFactory
import foreanalyzer.utils as utils


# ~ * CONSTANTS * ~
INTERNAL_CONFIG_FILE = os.path.join(
    glob.OUTER_FOLDER_PATH, 'config.json')


# ~~~ * CLI COMMAND BUILDER * ~~~
@click.group()
@click.option('-v', '--verbose', count=True, default=0, show_default=True)
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
        for plt in config['plotters']:
            plotter = PlotterFactory[plt](
                instruments=config['algo']['instruments'],
                feeders=config['feeders'][plt],
                timeframe=config['algo']['timeframe'])
            plotter.feed()
            cache.save_cache(
                cache.cache_path(['results'],['feed01']), plotter.data)
    except KeyboardInterrupt:
        CliConsole().write("\nExiting...", "bold")


def _check_instruments_parameter(value):
    str_instr = value.split(' ')
    for instr in str_instr:
        if instr not in glob.ACCEPTED_INSTRUMENTS:
            raise click.BadParameter(f"{instr} not accepted", param=instr)
    return str_instr


def _check_timeframe_parameter(timeframe):
    if timeframe not in glob.ACCEPTED_TIMEFRAMES:
        raise click.BadParameter(f"{timeframe}S not accepted", param=timeframe)
    return timeframe


def _check_plotters_parameter(value):
    str_plotters = value.split(' ')
    for plot in str_plotters:
        if plot not in glob.ACCEPTED_PLOT:
            raise click.BadParameter(f"{plot} not accepted", param=plot)
    return str_plotters


def _check_feeders_parameter(value):
    str_feeders = value.split(' ')
    for feeder in str_feeders:
        if feeder not in glob.SUPPORTED_FEEDERS[utils.PARAMETER().cli_TEMP_PLT]:
            raise click.BadParameter(
                "%s not supported for %s" % (feeder, utils.PARAMETER().cli_TEMP_PLT), param=feeder)
    return str_feeders


@main.command()
@click.option('--all', 'section', is_flag=True, flag_value="all",
              default="all", help="config all settings")
@click.option('-c', '--creds', 'section', is_flag=True, flag_value="creds",
              help="config only acount credentials")
@click.option('-a', '--account', 'section', is_flag=True, flag_value="acc",
              help="config only account settings")
@click.option('-g', '--algo', 'section', is_flag=True, flag_value="algo",
              help="config only algo setting")
@click.option('-p', '--plot', 'section', is_flag=True, flag_value="plot",
              help="config only plot setting")
def config(section):
    """set the internal configuration"""
    # get config file if present
    if os.path.isfile(INTERNAL_CONFIG_FILE):
        config = utils.read_int_config()
    else:
        config = {}
    # set credentials
    if section == 'all':
        ctn_creds = click.confirm(
            "continue to credential config?", default=True)
    if (section == 'all' and ctn_creds is True) or section == 'creds':
        CliConsole().write("~~~ * CREDENTIAL CONFIG * ~~~", "yellow", "bold")
        username = click.prompt("username")
        passwd = click.prompt("password", hide_input=True)
        CliConsole().debug(f"username: {username} - " +
                           f"password: {len(passwd)*'*'}")
        config['credentials'] = {'username': username, 'password': passwd}
    # set account settings
    if section == 'all':
        ctn_acc = click.confirm(
            "continue to account config?", default=True)
    if (section == 'all' and ctn_acc is True) or section == 'acc':
        CliConsole().write("~~~ * ACCOUNT CONFIG * ~~~", "yellow", "bold")
        initial_config = click.prompt(
            "initial balance", default=1000, show_default=True)
        CliConsole().debug(f"initial money set: {initial_config}")
        count_margin = click.confirm("want to count margin?", default=False)
        sim_profit = click.confirm("want to simulate profit?", default=True)
        config['account'] = {
            'initial_config': initial_config, 'count_margin': count_margin,
            'simulate_profit': sim_profit}
    # setting algo settings
    if section == 'all':
        ctn_algo = click.confirm(
            "continue to algo config?", default=True)
    if (section == 'all' and ctn_algo is True) or section == 'algo':
        CliConsole().write("~~~ * ALGORITHM CONFIG * ~~~", "yellow", "bold")
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
            "timeframe (in seconds)", default=300, show_default=True, type=int,
            value_proc=_check_timeframe_parameter)
        CliConsole().debug(f"timeframe set: {timeframe}")
        config['algo'] = {
            'instruments': instruments, 'timeframe': timeframe}
    # plotters settings
    if section == 'all':
        ctn_plot = click.confirm(
            "continue to plot config?", default=True)
    if (section == 'all' and ctn_plot is True) or section == 'plot':
        CliConsole().write("~~~ * PLOT CONFIG * ~~~", "yellow", "bold")
        # plotters
        CliConsole().write(f"Plot handlers available:")
        CliConsole().write(f"{'   '.join(glob.ACCEPTED_PLOT)}", "bold")
        config['plotters'] = click.prompt(
            "plot handlers (codes separated by space)", default="CDSPLT",
            show_default=True, value_proc=_check_plotters_parameter)
        if not isinstance(config['plotters'], list): # uniform
            config['plotters'] = [config['plotters']]
        # feeders
        ctn_feed = click.confirm(
            "continue to feed config?", default=True)
        if ctn_feed:
            config['feeders'] = {}
            for plt in config['plotters']:
                CliConsole().write(f"Feeders available for {plt}:")
                CliConsole().write(f"{'   '.join(glob.SUPPORTED_FEEDERS[plt])}", "bold")
                utils.PARAMETER().cli_TEMP_PLT = plt
                config['feeders'][plt] = click.prompt(
                    "feeders (codes separated by space)", default="ZIPF01",
                    show_default=True, value_proc=_check_feeders_parameter)
                if not isinstance(config['feeders'][plt], list): # uniform
                    config['feeders'][plt] = [config['feeders'][plt]]
        # TODO
    # TODO: add plotter/grapher selection and configuration
    # TODO: add option to run at the end
    # TODO: add option to collect results
    # dump config data on internal config file
    utils.write_int_config(config)
    CliConsole().info("config data saved on internal json config file")
