BusyMail
========


These are a couple of scripts that compute statistics ("stress" and "procrastination") from the data in the email inbox.

For example, here are my stats as they appear on [my webpage][web]:

<div class='figure' id='stats'> 
 
        <p class='graphics'> 
            <img id='stats_count' src="http://www.cds.caltech.edu/~andrea/busyplot/count.png"  alt='Count'/> 
            <img id='stats_age' src="http://www.cds.caltech.edu/~andrea/busyplot/age.png"    alt='Age'/> 
        </p> 
                 
	<p class='caption' style='font-style: italic'> 
	    Fig. 2. Stress and procrastination levels in the last 7 days.
	    Stress is measured by the number of flagged messages in the email inbox;
	    procrastination is measured by the median age of those messages.
	    <img id='updated' src="http://www.cds.caltech.edu/~andrea/busyplot/updated.gif" alt='Update'/> 
	</p> 
</div> 
	

## Usage

The first script ``busymail_log`` downloads the headers of email messages in a given mailbox, and stores them as a [YAML] file in a given directory.

Example usage:

    busymail_log --host imap.gmail.com --username <user> --password <pwd> \
                 --folder "[Gmail]/Starred" --storage logs/
        
The second script loads all the YAML files from the given directory, computes some statistics, and plots them to file.

    busymail_plot --storage logs/ --output figures/
    
Note that if you only have a few datapoints, the plot will not be clearly 
visible with the default axis properties (showing 1 week of data).
    
If you create a cron job with these two commands (and perhaps a rsync to your website), you can create an automatically updating summary of your activity.


## Installation

Install using:

    python setup.py develop
    
The prerequisites are:

* pyyaml
* numpy
* matplotlib
* imapclient

Install them before attempting the above command, as most of the times setup.py is not smart enough to install them correctly.

    
    
[web]: http://www.cds.caltech.edu/~andrea/
[YAML]: http://www.yaml.org/
    
    