
# ~~~~ console.py ~~~~
# forenalyzer.console
# ~~~~~~~~~~~~~~~~~~~~

import logging
import logging.config
import os.path

import rich

import foreanalyzer.utils as utils


# ~ * LOGGER * ~
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'deafult': {
            'format':
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'deafult',
        },
        'rotating': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'deafult',
            'filename': os.path.join(
                os.path.dirname(__file__), 'logs', 'logfile.log'),
            'when': 'midnight',
            'backupCount': 3
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
            #'propagate': True
        },
        'foreanalyzer': {
            'handlers': ['rotating'],
            'level': 'DEBUG'
        }
    }
})
LOGGER = logging.getLogger("foreanalyzer")


# ~~~ * HIGH LEVEL CLASS * ~~~
class CliConsole(metaclass=utils.SingletonMeta):
    """console controller logger replacement
    this has four different levels of logging: debug, info, warn and error
    each of these has its own color and debug is printed only if verbose
    parameter is set to ON"""
    def __init__(self):
        self.console = rich.get_console()
        self.verbose = False
        self.prefix = None

    def _color_markup(self, text, color):
        return f"[{color}]" + str(text) + f"[/{color}]"

    def log(self, text, *args, **kwargs):
        if self.prefix != None:
            text = self.prefix + " - " + text
        return self.console.log(text, *args, **kwargs)

    def write(self, text, *attrs):
        self.console.print(text, style=' '.join(attrs))

    def debug(self, text, level=1):
        LOGGER.debug(text)
        if self.verbose >= level:
            #self.log(self._color_markup(text, "41"))
            self.log(self._color_markup(text, "green"))

    def info(self, text):
        LOGGER.info(text)
        #self.log(self._color_markup(text, "62"))
        self.log(self._color_markup(text, "blue"))

    def warn(self, text):
        LOGGER.warn(text)
        #self.log(self._color_markup(text, "228"))
        self.log(self._color_markup(text, "yellow"))

    def error(self, text):
        LOGGER.error(text)
        #self.log(self._color_markup(text, "196"))
        self.log(self._color_markup(text, "red"))