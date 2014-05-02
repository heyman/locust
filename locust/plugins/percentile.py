import json
from itertools import chain

from flask import Blueprint
from . import Plugin


def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.iterkeys())]


class ResponseTimePercentile(Plugin):
    def load(self):
        blueprint = Blueprint("response_time_percentile", __name__)

        @blueprint.route("/percentiles")
        def percentiles():
            rows = []
            rows.append(["Name", "50%", "75%", "85%", "90%", "95%", "98%", "100%"])
            
            for s in chain(_sort_stats(self.runner.request_stats), [self.runner.stats.aggregated_stats("Total", full_request_history=True)]):
                row = [s.name]
                for p in [0.5, 0.75, 0.85, 0.90, 0.95, 0.98]:
                    row.append(s.get_response_time_percentile(p))
                row.append(s.max_response_time)
                rows.append(row)
            
            return json.dumps(rows)
        
        self.web_app.register_blueprint(blueprint)
