import optparse
import subprocess
import sys
from collections import defaultdict
import json

"""
The first (optional) argument is the number of trials to run; the default is 5. The rest of
the arguments just get passed right through to Popen. Sample usage:

iperf_trials iperf (run 5 trials of iperf using all defaults)
iperf_trials 10 iperf -t 60 -u -b 100M (run 10 trials of iperf using UDP, aiming to achieve 100Mbps bandwidth)
"""

def process_stats(results, metric_positions):
    stats = defaultdict(lambda: {'max': 0.0, 'min': float("inf"), 'mean': 0.0 })
    counter = 0
    for r in results:
        for key, position in metric_positions.items():
            stats[key]['max'] = max(float(r[position]), stats[key]['max'])
            stats[key]['min'] = min(float(r[position]), stats[key]['min'])
            stats[key]['mean'] = (stats[key]['mean'] * counter + float(r[position])) / (counter + 1)
        counter += 1

    return stats

def process_tcp_stats(results):
    metric_positions = {
      'transfer': 7,
      'bandwidth': 8,
    }
    return process_stats(results, metric_positions)

def process_udp_stats(results):
    metric_positions = {
        'sent': 7,
        'bandwidth': 8,
        'jitter': 9,
        'loss': 12,
        'wrong_order': 13,
    }
    return process_stats(results, metric_positions)

argv = sys.argv[1:]

print __doc__

if '-h' in argv:
    print __doc__
    exit(0);

stats_processor = (process_tcp_stats, process_udp_stats)['-u' in argv]

trials = 5
try:
    trials = int(argv[0])
    argv = argv[1:]
except:
    pass

argv += ['-y', 'c'] # make sure we output csv


results = []
for i in xrange(0, trials):
    (stdout, stderr) = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if stderr:
        sys.stderr.write(stderr)
    if stdout:
        results.append(stdout.strip().split('\n')[-1].split(','))

print json.dumps(stats_processor(results), indent=2)
