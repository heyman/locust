import runners
from runners import DistributedLocustRunner
import events
from time import time

response_times = []
cached_chart_data = {"time": 0, "response_times": []}

# Cache the result this many seconds as well as gather response times during this period
CACHE_UPDATE_TIME = 4.0

def get_chart_data():
    if isinstance(runners.locust_runner, DistributedLocustRunner):
        return {"time": cached_chart_data["time"], "response_times": [item for sublist in cached_chart_data["response_times"] for item in sublist]}
    return cached_chart_data

def on_request_success_chart(_, _1, response_time, _2):
    global response_times, cached_chart_data
    response_times.append(response_time)

    if not isinstance(runners.locust_runner, DistributedLocustRunner):
        if time() > CACHE_UPDATE_TIME + cached_chart_data["time"]:
            cached_chart_data = {"time": time(), "response_times": response_times}
            response_times = []

def on_report_to_master_chart(_, data):
    global response_times
    data["current_responses"] = response_times
    response_times = []

def on_slave_report_chart(_, data):
    global response_times, cached_chart_data
    if "current_responses" in data:
        response_times.append(data["current_responses"])

    if time() > CACHE_UPDATE_TIME + cached_chart_data["time"]:
        cached_chart_data = {"time": time(), "response_times": response_times}
        response_times = []

def register_listeners():
    events.report_to_master += on_report_to_master_chart
    events.slave_report += on_slave_report_chart
    events.request_success += on_request_success_chart
    
def remove_listeners():
    events.report_to_master.__idec__(on_report_to_master_chart)
    events.slave_report.__idec__(on_slave_report_chart)
    events.request_success.__idec__(on_request_success_chart)
    
register_listeners()