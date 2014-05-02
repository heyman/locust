import json
import requests

from locust.test.testcases import LocustTestCase
from locust.plugins import registry

from locust.plugins.percentile import ResponseTimePercentile

class ResponseTimePercentileTest(LocustTestCase):
    PLUGINS = LocustTestCase.PLUGINS + [ResponseTimePercentile]
    
    def test_percentile_endpoint(self):
        length = 13000
        for i in range(100):
            self.runner.stats.get("endpoint1", "GET").log(i*10, length)
        
        self.runner.stats.get("endpoint2", "GET").log(2000, length)
        
        
        response = requests.get("http://127.0.0.1:%i/percentiles" % self.web_port)
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        self.assertEqual(4, len(data))
        self.assertEqual("endpoint1", data[1][0])
        self.assertEqual("endpoint2", data[2][0])
        self.assertEqual("Total", data[3][0])
        
        for t in data[2][1:]:
            # all percentiles for endpoint2 should be 2000
            self.assertEqual(2000, t)
        
        # the 100% percentile of endpoint1 should be 990
        self.assertEqual(990, data[1][-1])
        self.assertEqual(980, data[1][-2])
