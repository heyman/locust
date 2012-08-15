from stats import percentile, RequestStats
from collections import deque
from runners import SLAVE_REPORT_INTERVAL
from runners import locust_runner, DistributedLocustRunner
import math
import events


response_times = deque([])

# Are we running in distributed mode or not?
is_distributed = isinstance(locust_runner, DistributedLocustRunner)

# The time window in seconds that current_percentile use data from
PERCENTILE_TIME_WINDOW = 15.0

def pop_response_times():
    if is_distributed:
        resp = [r for sublist in response_times for r in sublist]
    else:
        resp = list(response_times)
    response_times.clear()
    return resp

def on_request_success_chart(_, _1, response_time, _2):
    if is_distributed:
        response_times.append(response_time)
    else:
        response_times.append(response_time)

        # remove from the queue
        rps = RequestStats.sum_stats().current_rps
        if len(response_times) > rps*PERCENTILE_TIME_WINDOW:
            for i in xrange(len(response_times) - int(math.ceil(rps*PERCENTILE_TIME_WINDOW))):
                response_times.popleft()

def on_report_to_master_chart(_, data):
    global response_times
    data["current_responses"] = response_times
    response_times = []

def on_slave_report_chart(_, data):
    if "current_responses" in data:
        response_times.append(data["current_responses"])

    # remove from the queue
    slaves = locust_runner.slave_count
    response_times_per_slave_count = PERCENTILE_TIME_WINDOW/SLAVE_REPORT_INTERVAL
    if len(response_times) > slaves * response_times_per_slave_count:
        response_times.popleft()

def register_listeners():
    events.report_to_master += on_report_to_master_chart
    events.slave_report += on_slave_report_chart
    events.request_success += on_request_success_chart
    
def remove_listeners():
    events.report_to_master.__idec__(on_report_to_master_chart)
    events.slave_report.__idec__(on_slave_report_chart)
    events.request_success.__idec__(on_request_success_chart)
    
register_listeners()