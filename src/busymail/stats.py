from dateutil import parser
import numpy as np
from .utils import find_files, datetime2timestamp, percentile, seconds2days
import datetime

def compute_stats(snapshot, max_age):
    snapshot_date = snapshot['Date']
    messages = snapshot['Messages']
     
    # parse the "Date" field from string -> datetime object
    for m in messages:
        try:
            if not isinstance(m['Date'], datetime.datetime):
                m['Date'] = parser.parse(m['Date'], fuzzy=True).replace(tzinfo=None)
        except:
            print('Cannot parse date: %r' % m['Date'])
            raise
    
    valid_messages = [m for m in messages if m['Date'] is not None and snapshot_date-m['Date']<max_age]

    # print('Snapshot %s: %d messages, %d valid' % 
    #   (snapshot_date, len(messages), len(valid_messages)))

    snapshot_timestamp = datetime2timestamp(snapshot_date)
    messages_timestamps = np.array([datetime2timestamp(m['Date']) 
                                    for m in valid_messages ])
    messages_ages = snapshot_timestamp - messages_timestamps 
    
    dtype = [('timestamp','double'),
            ('median_age','double'),
            ('mean_age','double'),
            ('count','int')]
    stats = np.zeros((), dtype=dtype)
    stats['timestamp'] = datetime2timestamp(snapshot_date)
    stats['count'] = len(valid_messages)
    stats['median_age'] = percentile(messages_ages, 0.5)
    stats['mean_age'] = np.mean(messages_ages)
    return stats