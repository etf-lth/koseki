import logging

from koseki.core import KosekiCore

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler('koseki.log', 'a', 'utf-8')])


def run_koseki(flask_server=True):
    core = KosekiCore()
    core.start(flask_server=flask_server)


__all__ = ["run_koseki"]
