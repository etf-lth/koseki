import importlib
import logging
import types

from flask import Flask
from flask.blueprints import Blueprint

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.util import KosekiUtil


class KosekiPlugin:
    def __init__(self, app: Flask, storage: Storage, auth: KosekiAuth, util: KosekiUtil):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util

    def config(self) -> dict:
        return {}

    def plugin_enable(self) -> None:
        pass

    def plugin_disable(self) -> None:
        pass

    def create_blueprint(self) -> Blueprint:
        pass


class KosekiPluginManager:
    def __init__(
        self, app: Flask, storage: Storage, auth: KosekiAuth, util: KosekiUtil
    ):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util
        self.plugins: dict[str, KosekiPlugin] = {}

    def register_plugins(self) -> None:
        plugin: KosekiPlugin
        for plugin_name in self.app.config["PLUGINS"]:
            logging.info("Registering plugin: %s" % (plugin_name))

            plugin_module: types.ModuleType = importlib.import_module(
                "koseki.plugins." + plugin_name.lower()
            )
            plugin_type: type = getattr(plugin_module, plugin_name + "Plugin")

            # Instantiate plugin
            plugin = plugin_type(self.app, self.storage, self.auth, self.util)
            # Register config variables
            for k, v in plugin.config().items():
                self.app.config.setdefault(k, v)
            # Enable plugin
            plugin.plugin_enable()
            # Register URL handlers
            self.app.register_blueprint(plugin.create_blueprint())
            self.plugins[plugin_name] = plugin

    def isenabled(self, plugin: str) -> bool:
        return plugin in (p.lower() for p in self.plugins.keys())
