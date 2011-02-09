import sys, os, yaml
from imapclient import IMAPClient
from datetime import datetime
from optparse import OptionParser

def get_messages(hostname, username, password, folder, ssl=True):
    ''' Retrieve the headers of the email messages '''
    server = IMAPClient(hostname, use_uid=True, ssl=ssl)
    server.login(username, password)
    select_info = server.select_folder(folder)
    messages = server.search(['NOT DELETED'])
    what = 'RFC822.SIZE ENVELOPE'.split()
    response = server.fetch(messages, what)
    summaries = []
    for msgid, data in response.iteritems():
        env = envelope_fields(data)
        env['Size'] = data['RFC822.SIZE']
        summaries.append(env)
    summaries.sort(key=lambda d: d['Date'])
    return summaries
    
    
def envelope_fields(data):
    ''' Extracts/normalizes the header fields from an IMAP response packet. '''
    fields = "Date Subject From Sender Reply-To To Cc Bcc In-Reply-To Message-Id"
    fields = fields.split()
    env = data['ENVELOPE']
    assert len(env) == len(fields)
    result= dict(zip(fields, env))
    tuple_fields = 'From Sender Reply-To To Cc Bcc'.split()
    for t in tuple_fields:
        if result[t] is not None:
            def normalize(name, route, user, domain):
                email = '%s@%s' % (user, domain)
                if email == name: name = None
                return [name, email]
            result[t] = [ normalize(*x) for x in result[t]]
            # if len(result[t]) == 1:
            #     result[t] = result[t][0]
    return result

def main():
    parser = OptionParser()
    parser.add_option("--hostname", help="IMAP server")
    parser.add_option("--username", help="IMAP user")
    parser.add_option("--password", help="IMAP password")
    parser.add_option("--folder",   help="IMAP folder")
    parser.add_option("--storage",  help="Local directory to save messages to")
    (options, args) = parser.parse_args()  

    def check(x):
        if getattr(options, x) is None:
            print('Please provide %r on the command line.' % x)
            
    check('hostname')
    check('username')
    check('password')
    check('folder')
    check('storage')
    
    storage = options.storage
    
    messages = get_messages(options.hostname, options.username, 
                            options.password, options.folder)
    now = datetime.now()

    snapshot = {'BusyVersion': 1, 'Date': now, 'Messages': messages}

    if not os.path.exists(storage):
        os.makedirs(storage)

    basename = '%s.yaml' % now.isoformat('-')
    filename = os.path.join(storage, basename)
    with open(filename,'w') as f:
        yaml.dump(snapshot, f)
    
    
if __name__ == '__main__':
    main()
