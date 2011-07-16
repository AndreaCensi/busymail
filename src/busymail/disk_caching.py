import os, cPickle as pickle

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