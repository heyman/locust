import requests

from locust.test.testcases import LocustTestCase
from locust.plugins import Plugin, registry

from flask import Blueprint

class TestPlugin(Plugin):
    pass

class TestPlugins(LocustTestCase):
    def test_load_plugin(self):
        state = {"loaded":False}
        class MyPlugin(Plugin):
            def load(self):
                state["loaded"] = True
        
        self.assertNotIn(MyPlugin, registry.plugins)
        registry.add_plugin(MyPlugin)
        self.assertIn(MyPlugin, registry.plugins)
        registry.load_plugins(self.runner, self.web_app)
        self.assertTrue(state["loaded"])
    
    def test_load_plugin_string(self):
        self.assertNotIn(TestPlugin, registry.plugins)
        registry.add_plugin("locust.test.plugins.test_plugins.TestPlugin")
        self.assertIn(TestPlugin, registry.plugins)
    
    def test_web_route_not_persisted_between_tests(self):
        response = requests.get("http://127.0.0.1:%i/test_entry" % self.web_port)
        self.assertEqual(404, response.status_code)
    
    def test_add_web_route(self):
        class MyPlugin(Plugin):
            def load(self):
                bp = Blueprint("test_blueprint", __name__)
                @bp.route("/test_entry")
                def test_route():
                    return "yeah"
                
                self.web_app.register_blueprint(bp)
        
        self.assertNotIn(MyPlugin, registry.plugins)
        
        registry.add_plugin(MyPlugin)
        self.assertIn(MyPlugin, registry.plugins)
        
        registry.load_plugins(self.runner, self.web_app)
        response = requests.get("http://127.0.0.1:%i/test_entry" % self.web_port)
        self.assertEqual(200, response.status_code)
        self.assertEqual("yeah", response.content)
        
