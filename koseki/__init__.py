import logging

from koseki.core import KosekiCore

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler('koseki.log', 'a', 'utf-8')])


def run_koseki():
    core = KosekiCore()
    core.start()


__all__ = ["run_koseki"]
