import logging

from koseki.core import KosekiCore

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.FileHandler('koseki.log', 'a', 'utf-8')])

def run_prod():
    core = KosekiCore()
    core.start(flask_server=False)
    return core.app

def run_dev():
    core = KosekiCore()
    core.start(flask_server=True)
    return core.app


__all__ = ["run_prod", "run_dev"]
