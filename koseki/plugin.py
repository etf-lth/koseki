import importlib
import logging
from typing import DefaultDict
from koseki.core import KosekiCore
from flask.blueprints import Blueprint


class KosekiPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def config(self) -> dict:
        return {}

    def plugin_enable(self) -> None:
        pass

    def plugin_disable(self) -> None:
        pass

    def create_blueprint(self) -> Blueprint:
        pass

class KosekiPluginManager:
    def __init__(self, core: KosekiCore):
        self.core = core
        self.plugins = DefaultDict[str, KosekiPlugin]()

    def register_plugins(self):
        plugin: KosekiPlugin
        for plugin_name in self.core.app.config["PLUGINS"]:
            plugin_module: any = importlib.import_module("koseki.plugins." + plugin_name.lower())
            plugin_type: type = getattr(plugin_module, plugin_name + "Plugin")

            logging.info("Registering plugin: %s" % (plugin_name))

            # Instantiate plugin
            plugin = plugin_type(self.core.app, self.core, self.core.storage) # TODO: sort this out
            # Register config variables
            self.core.app.config.from_object(plugin.config())
            # Register URL handlers
            self.core.app.register_blueprint(plugin.create_blueprint())
            self.plugins[plugin_name] = plugin

    def isenabled(self, plugin: str) -> bool:
        return plugin in self.plugins