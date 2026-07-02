import importlib
import logging
import os
import types

from markupsafe import Markup
from typing import Callable

from flask import Flask
from flask.blueprints import Blueprint

from koseki.auth import KosekiAuth
from koseki.db.storage import Storage
from koseki.schedule import KosekiScheduler
from koseki.util import KosekiUtil


class KosekiPlugin:
    def __init__(self, app: Flask, storage: Storage, auth: KosekiAuth,
                 util: KosekiUtil, scheduler: KosekiScheduler):
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
        return Blueprint("kosekiplugin", __name__)
    
    def register_hooks(self, plugin_manager: KosekiPluginManager) -> None:
        pass # plugins add hooks here (tabs and extra html stuff)

    def register_models(self) -> None:
        pass  # plugins add models here


class KosekiPluginManager:
    def __init__(
        self, app: Flask, storage: Storage, auth: KosekiAuth,
        util: KosekiUtil, scheduler: KosekiScheduler
    ):
        self.app = app
        self.storage = storage
        self.auth = auth
        self.util = util
        self.scheduler = scheduler
        self.plugins: dict[str, KosekiPlugin] = {}
        self._hooks: dict[str, list[Callable]] = {}
        self._tabs: dict[str, tuple[tuple[str, str], ...]] = {}

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
            plugin = plugin_type(self.app, self.storage,
                                 self.auth, self.util, self.scheduler)
            self.plugins[plugin_name] = plugin

            # Register config variables
            for key, value in plugin.config().items():
                self.app.config[key] = value

        # Re-read user config to overwrite/prioritise over plugin config
        self.app.config.from_pyfile(os.path.join("..", "koseki.cfg"))

        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.register_models()
        self.storage.create_tables()


        # Enable plugins
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            # Enable plugin
            plugin.plugin_enable()
            # Register URL handlers
            self.app.register_blueprint(plugin.create_blueprint())
            # Register hooks
            plugin.register_hooks(self)

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        self._hooks.setdefault(hook_name, []).append(callback)

    def render_hooks(self, hook_name: str, **kwargs) -> Markup:
        return Markup("".join(
            cb(**kwargs) for cb in self._hooks.get(hook_name, [])
        ))
    
    def register_tab(self, group: str, uri: str, name: str) -> None:
        self._tabs[group] = self._tabs.get(group, ()) + ((uri, name),)

    def get_tabs(self, group: str) -> tuple[tuple[str, str], ...]:
        return self._tabs.get(group, ())

    def isenabled(self, plugin: str) -> bool:
        return plugin in (p.lower() for p in self.plugins.keys())
