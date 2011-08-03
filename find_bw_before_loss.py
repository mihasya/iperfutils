import optparse
import subprocess
import re

parser = optparse.OptionParser()
parser.add_option('--host', action='store', dest='host')
parser.add_option('--port', action='store', dest='port', default=5001, type=long)
parser.add_option('--step', action='store', dest='step', default=5, type=int, help="decrease the bandwidth target by this much after every failed test (5)")
parser.add_option('--successes', action='store', dest='successes', default=2, type=int, help="require this many runs at or below the desired loss threshold to pass (2)")
parser.add_option('--start', action='store', dest='start')
parser.add_option('--maxloss', action='store', dest='maxloss', default='0.0', type=float)

(opts, args) = parser.parse_args()

assert opts.host
assert opts.start

try:
    target = re.match('^(?P<value>\d+)(?P<unit>[MK]{1})$', opts.start).groupdict()
except AttributeError:
    print "Invalid target bandwidth %s" % opts.target
    exit(1)

print opts

target['value'] = int(target['value'])
successes = 0
while target['value'] > 0 and successes < opts.successes:
    popen_opts = ['iperf', '-c', opts.host, '-u', '-y', 'c', '-b', "%(value)d%(unit)s" % target ]
    (stdout, stderr) = subprocess.Popen(popen_opts, stdout=subprocess.PIPE).communicate()
    client = stdout.strip().split("\n")[-1]
    client = client.split(',')
    if float(client[12]) > opts.maxloss:
        target['value'] -= opts.step
        print "new target: %(value)d%(unit)s; " % target + "loss was %f after %d successes" % (float(client[12]), successes)
        successes = 0
    else:
        successes += 1

if successes == opts.successes:
    print "%.2f%% loss achieved at " % opts.maxloss + "%(value)d%(unit)s" % target
