import json

import requests
import mock

from locust import stats, web
from .testcases import LocustTestCase

class TestWebUI(LocustTestCase):    
    def test_index(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/" % self.web_port).status_code)
    
    def test_stats_no_data(self):
        self.assertEqual(200, requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).status_code)
    
    def test_stats(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        self.assertEqual(2, len(data["stats"])) # one entry plus Total
        self.assertEqual("/test", data["stats"][0]["name"])
        self.assertEqual("GET", data["stats"][0]["method"])
        self.assertEqual(120, data["stats"][0]["avg_response_time"])
        
    def test_stats_cache(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(2, len(data["stats"])) # one entry plus Total
        
        # add another entry
        stats.global_stats.get("/test2", "GET").log(120, 5612)
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).content)
        self.assertEqual(2, len(data["stats"])) # old value should be cached now
        
        web.request_stats.clear_cache()
        
        data = json.loads(requests.get("http://127.0.0.1:%i/stats/requests" % self.web_port).content)
        self.assertEqual(3, len(data["stats"])) # this should no longer be cached
    
    def test_request_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/requests/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
    
    def test_distribution_stats_csv(self):
        stats.global_stats.get("/test", "GET").log(120, 5612)
        response = requests.get("http://127.0.0.1:%i/stats/distribution/csv" % self.web_port)
        self.assertEqual(200, response.status_code)
