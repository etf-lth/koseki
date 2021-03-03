import importlib
from koseki.schedule import KosekiScheduler
import logging
import os
import types

from flask import Flask
from flask.blueprints import Blueprint

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.util import KosekiUtil


class KosekiPlugin:
    def __init__(self, app: Flask, storage: Storage, auth: KosekiAuth, util: KosekiUtil, scheduler: KosekiScheduler):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util
        self.scheduler = scheduler

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
        self, app: Flask, storage: Storage, auth: KosekiAuth, util: KosekiUtil, scheduler: KosekiScheduler
    ):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util
        self.scheduler = scheduler
        self.plugins: dict[str, KosekiPlugin] = {}

    def register_plugins(self) -> None:
        plugin: KosekiPlugin

        #
        # Read config first before enabling
        #
        for plugin_name in self.app.config["PLUGINS"]:
            logging.info("Registering plugin: %s", plugin_name)

            # Instantiate plugin
            plugin_module: types.ModuleType = importlib.import_module(
                "koseki.plugins." + plugin_name.lower()
            )
            plugin_type: type = getattr(plugin_module, plugin_name + "Plugin")
            plugin = plugin_type(self.app, self.storage, self.auth, self.util, self.scheduler)
            self.plugins[plugin_name] = plugin

            # Register config variables
            for key, value in plugin.config().items():
                self.app.config[key] = value

        # Re-read user config to overwrite/prioritise over plugin config
        self.app.config.from_pyfile(os.path.join("..", "koseki.cfg"))

        # Enable plugins
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            # Enable plugin
            plugin.plugin_enable()
            # Register URL handlers
            self.app.register_blueprint(plugin.create_blueprint())

    def isenabled(self, plugin: str) -> bool:
        return plugin in (p.lower() for p in self.plugins.keys())
