import logging
import sys

from koseki.core import KosekiCore

logging_format = "%(asctime)s %(levelname)s %(message)s"
logging_handler_file = logging.FileHandler('koseki.log', 'a', 'utf-8')
logging_handler_console = logging.StreamHandler(sys.stdout)


def run_prod():
    logging.basicConfig(
        format=logging_format,
        level=logging.DEBUG,
        handlers=[logging_handler_file])
    core = KosekiCore()
    core.start(flask_server=False)
    return core.app


def run_dev():
    logging.basicConfig(
        format=logging_format,
        level=logging.DEBUG,
        handlers=[logging_handler_file, logging_handler_console])
    core = KosekiCore()
    core.start(flask_server=True)
    return core.app


__all__ = ["run_prod", "run_dev"]
