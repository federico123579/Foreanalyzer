"""
foreanalyzer.cli
~~~~~~~~~~~~~~~~

cli module
"""
import os
import logging

import click
import rich

import foreanalyzer._internal_utils as internal
from foreanalyzer.exceptions import NotConfigurated


INTERNAL_CONFIG_FILE = os.path.join(
    internal.OUTER_FOLDER_PATH, 'config.json')
LOGGER = logging.getLogger("foreanalyzer")

class CliConsole(metaclass=internal.SingletonMeta):
    """console controller logger replacement
    this has four different levels of logging: debug, info, warn and error
    each of these has its own color and debug is printed only if verbose
    parameter is set to ON"""
    def __init__(self):
        self.console = rich.console.Console()
        self.verbose = False
        self.log = self.console.log

    def _color_markup(self, text, color):
        return f"[{color}]" + str(text) + f"[/{color}]"

    def write(self, text, *attrs):
        self.console.print(text, style=' '.join(attrs))

    def debug(self, text):
        LOGGER.debug(text)
        if self.verbose:
            self.log(self._color_markup(text, "41"))

    def info(self, text):
        LOGGER.info(text)
        self.log(self._color_markup(text, "62"))

    def warn(self, text):
        LOGGER.warn(text)
        self.log(self._color_markup(text, "228"))

    def error(self, text):
        LOGGER.error(text)
        self.log(self._color_markup(text, "196"))


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False, show_default=True)
@click.option('--algo')
def main(verbose, algo):
    """main controller"""
    if verbose:
        CliConsole().verbose = True

@main.command()
def run():
    """run the analysis with config given
    load algo and works as earlier versions did"""
    # get configurations & settings
    config = internal.read_ext_config()
    if (config['USE_THIS'] == False and not
            os.path.isfile(INTERNAL_CONFIG_FILE)):
        raise NotConfigurated()
    elif config['USE_THIS'] == True:
        pass # let config be configured with the external config file
        # TODO: maybe dump external config into internal
    else:
        config = internal.read_int_config()


def _check_currencies_parameter(value):
    str_curs = value.split(' ')
    for curr in str_curs:
        if curr not in internal.ACC_CURRENCIES:
            raise click.BadParameter("Currency not accepted", param=curr)
    return str_curs


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
        config = internal.read_int_config()
    else:
        config = {}
    # set credentials
    if section in ['all', 'creds']:
        CliConsole().write("# CREDENTIAL CONFIG #", "yellow", "bold")
        config['username'] = click.prompt("username")
        config['passwd'] = click.prompt("password", hide_input=True)
        CliConsole().debug(f"username: {config['username']} - " +
                           f"password: {len(config['passwd'])*'*'}")
    # set account settings
    if section in ['all', 'acc']:
        CliConsole().write("# ACCOUNT CONFIG #", "yellow", "bold")
        config['initial_config'] = click.prompt(
            "initial balance", default=1000, show_default=True)
        CliConsole().debug(f"initial money set: " +
                           f"{config['initial_config']}")
    # setting algo settings
    if section in ['all', 'algo']:
        CliConsole().write("# ALGORITHM CONFIG #", "yellow", "bold")
        # currencies
        config['currencies'] = click.prompt(
            "currencies (codes separated by space)", default="EURUSD",
            show_default=True, value_proc=_check_currencies_parameter)
        if not isinstance(config['currencies'], list): # uniform default EURUSD
            config['currencies'] = [config['currencies']]
        CliConsole().debug(
            f"currencies set: {', '.join(config['currencies'])}")
        # timeframe
        config['timeframe'] = click.prompt(
            "timeframe (in seconds)", default=300, show_default=True, type=int)
        CliConsole().debug(f"timeframe set: {config['timeframe']}")
    # dump config data on internal config file
    internal.write_int_config(config)
    CliConsole().info("config data saved on internal json config file")

# TESTING
'''import click
from progress.bar import ChargingBar
from progress.spinner import Spinner
from rich.text import Text
from rich.console import Console

import time

import os
from tqdm import tqdm, trange
from time import sleep

def dosomething(buf):
    """Do something with the content of a file"""
    time.sleep(1)
    pass

def walkdir(folder):
    """Walk through each files in a directory"""
    for dirpath, dirs, files in os.walk(folder):
        for filename in files:
            yield os.path.abspath(os.path.join(dirpath, filename))


def process_content_with_progress3(inputpath, blocksize=1024):
    # Preprocess the total files sizes
    sizecounter = 0
    for filepath in tqdm(walkdir(inputpath), unit="files"):
        sizecounter += os.stat(filepath).st_size

    # Load tqdm with size counter instead of file counter
    with tqdm(total=sizecounter, leave=None,
              unit='B', unit_scale=True, unit_divisor=1024) as pbar:
        console = Console()
        for filepath in walkdir(inputpath):
            with open(filepath, 'rb') as fh:
                buf = 1
                while (buf):
                    buf = fh.read(blocksize)
                    dosomething(buf)
                    if buf:
                        pbar.set_postfix(file=filepath[-10:], refresh=False)
                        pbar.update(len(buf))
                        text = Text("Test Test")
                        text.stylize(0, 4, "bold magenta")
                        console.print(text)
                        #tqdm.write(text)


def test():
    click.echo("testing...")
    with ChargingBar('Processing', max=20) as bar:
        for i in range(20):
            # Do some work
            time.sleep(0.01)
            bar.next()
    spinner = Spinner('Loading ')
    for i in range(20):
        # Do some work
        spinner.next()
        time.sleep(0.01)
    process_content_with_progress3(".")
'''
