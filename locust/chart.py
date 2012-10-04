import runners
from runners import DistributedLocustRunner
import events
from time import time
import math

response_times = []

cached_response_times = []
cache_timestamp = 0

# Cache the result this many seconds as well as gather response times during this period
CACHE_UPDATE_TIME = 4.0

def get_chart_data():
    if isinstance(runners.locust_runner, DistributedLocustRunner):
        resp_times = [item for sublist in cached_response_times for item in sublist]
    else:
        resp_times = sorted(cached_response_times)

    return {"timestamp": cache_timestamp, 
            "data": {"mean": average(resp_times),
                     "10%": percentile(resp_times, 0.10),
                     "25%": percentile(resp_times, 0.25),
                     "50%": percentile(resp_times, 0.50),
                     "75%": percentile(resp_times, 0.75),
                     "90%": percentile(resp_times, 0.90)
                    }
            }

def average(resp_times):
    return sum(resp_times) / max(len(resp_times), 1)

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return 0
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def on_request_success_chart(_, _1, response_time, _2):
    global response_times, cached_response_times, cache_timestamp
    response_times.append(response_time)

    if not isinstance(runners.locust_runner, DistributedLocustRunner):
        if time() > CACHE_UPDATE_TIME + cache_timestamp:
            cache_timestamp = time()
            cached_response_times = response_times
            response_times = []

def on_report_to_master_chart(_, data):
    global response_times
    data["current_responses"] = response_times
    response_times = []

def on_slave_report_chart(_, data):
    global response_times, cached_response_times, cache_timestamp
    if "current_responses" in data:
        response_times.append(data["current_responses"])

    if time() > CACHE_UPDATE_TIME + cache_timestamp:
        cache_timestamp = time()
        cached_response_times = response_times
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