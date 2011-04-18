import yaml, sys, os, fnmatch
import numpy as np
import cPickle as pickle
import time
from matplotlib import pylab
from datetime import datetime, timedelta
from dateutil import parser
from optparse import OptionParser
from .utils import find_files, datetime2timestamp, percentile, seconds2days

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
    
def busyplot(logdir, output, max_age=timedelta(30)):
    # Load everything
    snapshots = read_snapshot_dir(logdir)
    
    # Compute the stats (np array)
    stats = compute_stats(snapshots, max_age=max_age)
    
    # Plot
    if not os.path.exists(output):
        os.makedirs(output)
    plot_stats(output, stats)

def disk_cache(func):
    # Processes a file or directory, caching results 
    # Assumes that the wrapped function has only one arg (for simplicity).
    def wrapper(filename):
        if os.path.isdir(filename):
            cache = os.path.join(filename, '%s.pickle' % func.__name__)
        else:
            cache = os.path.splitext(filename)[0] + '.%s.pickle' % func.__name__
        if (os.path.exists(cache) and
            (os.path.getmtime(cache) > os.path.getmtime(filename))):
            # print('Using cache %r' % cache)
            return pickle.load(open(cache,'rb'))
        else:
            # print('Creating cache %r' % cache)
            result = func(filename)
            with open(cache, 'wb') as f:
                pickle.dump(result, f)
            return result
    return wrapper

@disk_cache    
def read_snapshot_dir(logdir):
        # Read all yaml files inside logdir
    snapshots = [ read_snapshot(f) for f in find_files(logdir, '*.yaml')]

    # print('Loaded %d snapshots' % len(snapshots))

    # Sort by Date
    snapshots.sort(key=lambda x: x['Date'])

    return snapshots

@disk_cache
def read_snapshot(filename):
    return yaml.load(open(filename))
    

def compute_stats(snapshots, max_age):
    stats = np.zeros((len(snapshots)),
                                [('timestamp','double'),
                                ('median_age','double'),
                                ('mean_age','double'),
                                ('count','int')])
    for i, snapshot in enumerate(snapshots):            
        snapshot_date = snapshot['Date']
        messages = snapshot['Messages']
        
        
        # parse the "Date" field from string -> datetime object
        for m in messages:
            m['Date'] = parser.parse(m['Date']).replace(tzinfo=None)
        
        valid_messages = [m for m in messages if snapshot_date-m['Date']<max_age]

        # print('Snapshot %s: %d messages, %d valid' % 
                # (snapshot_date, len(messages), len(valid_messages)))

        snapshot_timestamp = datetime2timestamp(snapshot_date)
        messages_timestamps = np.array([datetime2timestamp(m['Date']) 
                                        for m in valid_messages ])
        messages_ages = snapshot_timestamp - messages_timestamps 
        
        stats[i]['timestamp'] = datetime2timestamp(snapshot_date)
        stats[i]['count'] = len(valid_messages)
        stats[i]['median_age'] = percentile(messages_ages, 0.5)
        stats[i]['mean_age'] = np.mean(messages_ages)

    return stats
    
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
    
    z = 0.7;
    figsize=(4*z,3*z)
    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = stats['count']
    pylab.plot(x, y,'-')
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.ylabel('flagged messages')
    pylab.title('Stress')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'count.png'))

    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['median_age'])
    pylab.plot(x, y,'-')
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.title('Procrastination')
    pylab.ylabel('median age (days)')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'age.png'))
    
    
    pylab.figure(figsize=figsize)
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['mean_age'])
    pylab.plot(x, y,'-')
    y_avg = percentile(y, 0.5)
    pylab.plot(x, y_avg * np.ones(y.shape),'k--')
    pylab.title('Procrastination')
    pylab.ylabel('mean age (days)')
    set_axis_lastweek()
    pylab.savefig(os.path.join(output, 'meanage.png'))

    options = locals()
    plots = [stress_complete, procrastination_complete, meanage_complete]
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
    pylab.plot(x, y,'-')
    pylab.ylabel('flagged messages')
    pylab.title('Stress')
    set_axis_0()

def procrastination_complete(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['median_age'])
    pylab.plot(x, y,'-')
    pylab.title('Procrastination')
    pylab.ylabel('median age (days)')
    set_axis_0()


def meanage_complete(stats, options):
    ratio = 10; height=2.5
    pylab.figure(figsize=(ratio*height,height))
    right_now = time.time()
    x = seconds2days(stats['timestamp']-right_now)
    y = seconds2days(stats['mean_age'])
    pylab.plot(x, y,'-')
    pylab.title('Procrastination')
    pylab.ylabel('mean age (days)')
    set_axis_0()


if __name__ == '__main__':
    main()
    
    