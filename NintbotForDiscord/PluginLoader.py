import os
import json
import importlib.util
import traceback
__author__ = 'Riley Flynn (nint8835)'


class PluginLoader:

    def __init__(self, bot):
        self.bot = bot
        self._plugins = []

    def load_plugins(self):
        self._plugins = []
        for folder in [os.path.join("plugins", i) for i in os.listdir(os.path.join("plugins")) if os.path.isdir(os.path.join("plugins", i))]:
            if os.path.isfile(os.path.join(folder, "plugin.json")):
                with open(os.path.join(folder, "plugin.json")) as f:
                    plugin_data = json.load(f)
                    print(plugin_data)
                    # noinspection PyBroadException
                    try:
                        spec = importlib.util.spec_from_file_location(plugin_data["module_name"], os.path.join(folder, plugin_data["main_file"]))
                        plugin = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(plugin)
                        plugin_instance = plugin.Plugin(self.bot)
                        self._plugins.append({"info": plugin_data, "status": "loaded", "module": plugin, "instance": plugin_instance})
                    except:
                        self._plugins.append({"info": plugin_data, "status": "error", "exception": traceback.format_exc(5), "module": plugin})
                    print(self._plugins)
