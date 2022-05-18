import logging
import sys
from typing import Dict, Optional, Set, Union

LoggingLevelType = Union[int, str]

# From https://refactoring.guru/design-patterns/singleton/python/example
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class GlobalConfig(metaclass=SingletonMeta):
    logging_levels: Dict[str, LoggingLevelType] = dict()
    default_level: LoggingLevelType = logging.DEBUG
    active_loggers: Set[logging.Logger] = set()
    logfilename: Optional[str] = None

    def get_logging_level(
            self, logger_name: str,
            default_value: Optional[LoggingLevelType] = None) -> LoggingLevelType:
        if(logger_name  in self.logging_levels):
            return self.logging_levels[logger_name]

        if(default_value is not None):
            return default_value

        return self.default_level

    def reset_loggers(self):
        for logger in self.active_loggers:
            self.default_logger_setup(logger)

    def log_to_file(self, file_name):
        self.logfilename = file_name
        self.reset_loggers()

    def default_logger_setup(self, logger: logging.Logger):
        self.active_loggers.add(logger)
        this_level = GlobalConfig().get_logging_level(logger.name)
        logger.setLevel(this_level)

        # create console handler and set level to debug
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(this_level)
        handler = ch

        if(self.logfilename is not None):
            fh = logging.FileHandler('logs/{}'.format(self.logfilename))
            fh.setLevel(this_level)
            handler = fh

        # create formatter
        # Production
        # formatter = logging.Formatter('%(message)s')

        # Debug timing
        formatter = logging.Formatter('[%(asctime)s]  %(message)s', "%m/%d %H:%M:%S")

        # Debug loggers
        # formatter = logging.Formatter('[%(asctime)s]:%(name)10s:%(levelname)6s  %(message)s',
        #                               "%m/%d %H:%M:%S")

        # Debug levels
        # formatter = logging.Formatter('[%(asctime)s]:%(levelname)6s  %(message)s',
        #                               "%m/%d %H:%M:%S")

        # add formatter to ch
        handler.setFormatter(formatter)

        # Clear any previous handlers
        while len(logger.handlers) > 0:
            logger.removeHandler(logger.handlers[0])

        # add ch to logger
        logger.addHandler(handler)
