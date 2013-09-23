import yaml, sys, os, fnmatch
import numpy as np
import cPickle as pickle
import time
from matplotlib import pylab
from datetime import datetime, timedelta
from dateutil import parser
from optparse import OptionParser
from .utils import find_files, datetime2timestamp, percentile, seconds2days
from .disk_caching import disk_cache
from .stats import compute_stats

MESSAGE_ID = 'Message-Id'
SNAPSHOT_IDS = 'ids'

def main():
    parser = OptionParser()
    parser.add_option("--storage",
                      help="Local directory containing YAML snapshots.")
    parser.add_option("--output", help="Local directory to store produced plots.")
    (options, args) = parser.parse_args()  

    def check(x):
        if getattr(options, x) is None:
            print('Please provide "--%s" switch on the command line.' % x)
            sys.exit(1)
            
    check('output')
    check('storage')

    busyplot(options.storage, options.output)
    
def busyplot(logdir, output):
    # Load everything
    stats = []
    for f in find_files(logdir, '*.yaml'):
        f_stats = compute_stats_file(f)
        stats.append(f_stats)

    stats = np.hstack(stats) 
    
    # Plot
    if not os.path.exists(output):
        os.makedirs(output)
    plot_stats(output, stats)


@disk_cache    
def compute_stats_file(filename):
    snapshot = yaml.load(open(filename))
    max_age=timedelta(30)
    return compute_stats(snapshot, max_age)
    
    
    
def set_axis_lastweek():
    pylab.xlabel('time (days)')
    pylab.gcf().subplots_adjust(top=1.0-0.13, bottom=0.2, right=1-0.02,
                                left=0.2)
    a = list(pylab.axis())
    na = [-7, 0.5, 0, a[3]*1.05]
    pylab.axis(na)
    
def set_axis_0():
    pylab.xlabel('time (days)')
    pylab.gcf().subplots_adjust(top=1.0-0.13, bottom=0.2, right=1-0.02,
                                left=0.2)
    a = list(pylab.axis())
    na = [a[0], a[1], 0, a[3]*1.05]
    pylab.axis(na)
    
def plot_stats(output, stats):
    from matplotlib import rc
    rc('font', family='serif')

    right_now = time.time()
    
    how=dict(markersize=2)
    z = 0.7;
    figsize=(4*z,3*z)
    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = stats['count']
    pylab.plot(x, y,'k-', **how)
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.ylabel('flagged messages')
    pylab.title('Stress')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'count.png'))

    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['median_age'])
    pylab.plot(x, y,'k-', **how)
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.title('Procrastination')
    pylab.ylabel('median age (days)')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'age.png'))
    
    
    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['mean_age'])
    pylab.plot(x, y,'k-', **how)
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.title('Procrastination')
    pylab.ylabel('mean age (days)')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'meanage.png'))

    options = locals()
    plots = [stress_complete, procrastination_complete, meanage_complete,
            procrastination_complete_both ]
    for plot in plots:
        # print('Plotting %s' % plot.__name__)
        plot(stats, options)
        filename = os.path.join(output, '%s.png' % plot.__name__)
        # print('Writing to %r.' % filename)
        pylab.savefig(filename)

def stress_complete(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    y = stats['count']
    pylab.plot(x, y,'.')
    pylab.ylabel('flagged messages')
    pylab.title('Stress')
    set_axis_0()

def procrastination_complete(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['median_age'])
    pylab.plot(x, y,'.')
    pylab.title('Procrastination')
    pylab.ylabel('median age (days)')
    set_axis_0()


def meanage_complete(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['mean_age'])
    pylab.plot(x, y,'.')
    pylab.title('Procrastination')
    pylab.ylabel('mean age (days)')
    set_axis_0()


def procrastination_complete_both(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    median = seconds2days(stats['median_age'])
    mean = seconds2days(stats['mean_age'])
    pylab.plot(x, median,'k.', label='median')
    pylab.plot(x, mean,'b.', label='mean')
    pylab.title('Procrastination')
    pylab.ylabel('age (days)')
    pylab.legend(loc='upper left')
    set_axis_0()


if __name__ == '__main__':
    main()
    
    