#!/usr/bin/python

import requests
import csv
import json
import sys
import datetime
import time
import subprocess
import smtplib

# Munki report PHP variables
base_url = 'https://<munki-report>/index.php?'
login = '<username>'
password = '<password>'
# data columns to get back from munki report
columns = [
    "machine.hostname",
    "reportdata.remote_ip",
    "reportdata.timestamp",
    "site_info.site_code",
    "site_info.site_name",
    "ard.text3"
]

# Set up some site codes to ignore for whatever reason
site_codes_to_ignore = ['1234','5678'] # 

# Date and holiday period variables
get_today = datetime.date.today()
today = (str(get_today))

## Set the holiday start/end periods here - school term dates.
t1_start = '2018-04-14'
t1_end = '2018-04-30'

t2_start = '2017-07-01'
t2_end = '2017-07-17'

t3_start = '2017-09-23'
t3_end = '2017-10-08'

t4_start = '2017-12-16'
t4_end = '2018-02-05'

def check_holiday_period(today):
    # Test if today is in a holiday period.
    # If we are, then we should return true
    if t1_start <= today <= t1_end:
        return True
    else:
        if t2_start <= today <= t2_end:
            return True
        else:
            if t3_start <= today <= t3_end:
                return True
            else:
                if t4_start <= today <= t4_end:
                    return True
                else:
                    return False    

# Use smtplib to send email
def send_email_summary(offline_servers):
    smtp_server_address = 'mail.server.com'
    smtp_server_port = '25'
    from_email_address = 'alerts@server.com'

    recip = 'recip1@server.com'
    bcc_recip1 = 'bcc1@server.com'

    subject = "[WARNING] OFFLINE Apple Caching Server(s)"
    message_body = """From: Alert System <%s>
To: <%s>
Subject: %s
reply-to: <%s>

The following Apple Caching Servers are flagged as OFFLINE
The school has been notified via an email sent to the school email address.


%s


Regards,

<Alert System>

    """ % (from_email_address,recip,subject,from_email_address,offline_servers)
    
    email_server = smtplib.SMTP(smtp_server_address, smtp_server_port)
    try:
        email_server.sendmail(from_email_address, [recip, bcc_recip1], message_body)
        print ' - Sent summary email to: %s ...' % recip
        #print '         - Sent bcc to: %s ...' % bcc_recip
    except Exception as Error: 
        print Error
    email_server.quit()


# Use smtplib to send email
def send_email_alert(recipient, site_code, site_name, last_seen, built_by):
    smtp_server_address = 'mail.server.com'
    smtp_server_port = '25'
    from_email_address = 'alerts@server.com'
    
    subject = "[WARNING] %s Apple Caching Server is OFFLINE" % site_name
    message_body = """From: Alert System <%s>
To: <%s>
Subject: %s
reply-to: <%s>

ATTN: The School ICT Coordinator

Your school's Apple Caching Server (ACS) currently appears to be offline and not functioning.


    It has not reported into our central monitoring system since: %s

    Your caching server was %s


Please ensure it is plugged into power and a working ethernet port and powered on.

If there are problems bringing your ACS online, please log a service desk call with <Alert System> on <1800 000 000>

Regards,

Alert System

    """ % (from_email_address,recipient,subject,from_email_address,last_seen,built_by)
    
    email_server = smtplib.SMTP(smtp_server_address, smtp_server_port)
    try:
        email_server.sendmail(from_email_address, [recipient], message_body)
        print '         - Sent email to: %s ...' % recipient
        print '         - Sent bcc to: %s ...' % bcc_recip
    except Exception as Error: 
        print Error
    email_server.quit()


# Generate the munki report query
def generate_query():
    q = {'columns[{0}][name]'.format(i): c for i, c in enumerate(columns)}
    q['search[value]'] = 'ACS' 
    return q

# create an empty list in which to store our offline servers
offline_servers_list = []

# Start the script here, if we are in a holiday period lets just exit!
print 'Today is: %s' % today
if check_holiday_period(today):
    print "[ERROR] We are in a holiday period! Exiting!"
    raise SystemExit
else:
    print "We are _not_ in a holiday period, lets continue..."
# Ok not in a holiday period, lets continue

print ""
print "Checking for servers that have not been online for more than 4 hours ..."
print ''

# Authenticate to Munki Report and get a session cookie
auth_url ='{0}/auth/login'.format(base_url)
query_url='{0}/datatables/data'.format(base_url)
session = requests.Session()
auth_request = session.post(auth_url, data={'login': login, 'password': password})

# Trap here if we can't access munki report for whatever reason
if auth_request.status_code != 200:
    print '[ERROR] Invalid url!'
    raise SystemExit

query_data = session.post(query_url, data=generate_query())
query_data_json = query_data.json()['data']
output = csv.writer(sys.stdout)
# Get the current time in epoch
current_time = int(time.time())
#output.writerow([0])

for row in query_data_json:
    ip_address = row[0]
    built_by = row[1]
    checkin_epoch = row[2]
    hostname = row[3]
    site_name = row[4]
    site_code = row[5]
    last_seen_time = time.strftime('%H:%M:%S on %d-%m-%Y', time.localtime(float(int(checkin_epoch))))
    time_since_last_seen = (float(int(current_time))) - (float(int(checkin_epoch)))
    if time_since_last_seen > 14400:
        if site_code not in site_codes_to_ignore:
            # Perform an ldap lookup to get the school email address from the site code
            school_email = subprocess.check_output(
               "/usr/local/bin/site_py_email %s" % site_code, shell=True)
            time.sleep(1)
            if not school_email.strip():
                school_email = "<other.email@server.com>"
            school_email = school_email.strip()
            print '     Hostname:     %s' % hostname
            print '     IP Address:   %s' % ip_address
            print '     Site code:    %s' % site_code
            print '     Site name:    %s' % site_name
            print '     Last seen:    %s' % last_seen_time
            print '     School Email: %s' % school_email
            print '     Built by:     %s' % built_by
            send_email_alert(school_email,site_code,site_name,last_seen_time,built_by)
            print ''
            # add our servers to our list in a CSV fashion - yes i know this is horribly ugly
            offline_servers_list.append(site_code+','+site_name+','+last_seen_time+','+built_by)
# join our list off line servers and append a carriage return
offline_servers = "\n\n".join(offline_servers_list)
# now send off our summary!
send_email_summary(offline_servers)



