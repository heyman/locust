from collections import OrderedDict
    

class Plugin(object):
    runner = None
    """Locust runner instance"""
    
    web_app = None
    """Flask app instance for locust web UI"""
    
    
    def __init__(self, runner, web_app):
        self.runner = runner
        self.web_app = web_app
    
    def load(self):
        pass
    
    def unload(self):
        pass
    

class PluginRegistry(object):
    plugins = None
    
    def __init__(self):
        self.plugins = OrderedDict()
    
    def add_plugin(self, plugin):
        if isinstance(plugin, basestring):
            parts = plugin.split(".")
            module_part = ".".join(parts[:-1])
            module = __import__(module_part, fromlist=[""])
            plugin = getattr(module, parts[-1])
        if not issubclass(plugin, Plugin):
            raise TypeError("Plugins need to be of the type Plugin. Got: %r" % (plugin,))
        self.plugins[plugin] = None
    
    def load_plugins(self, runner, web_app):
        for plugin_class in self.plugins:
            plugin = plugin_class(runner, web_app)
            self.plugins[plugin_class] = plugin
            plugin.load()
    
    def unload_plugins(self):
        for plugin_class, plugin in self.plugins.items():
            if plugin is not None:
                plugin.unload()
                del self.plugins[plugin_class]

registry = PluginRegistry()

LOCUST_PLUGINS = [
    "locust.plugins.percentile.ResponseTimePercentile",
]
