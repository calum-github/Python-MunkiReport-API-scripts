# Python-MunkiReport-API-scripts

A basic script I wrote that performs a couple of functions.

The first function is to check the date and see if it is currently within a school holiday period, if it is we can safely
assume that the school has turned off their caching server for the holidays, in this case we simply the exit the script here.

If we pass this check, we make a request to Munkireport PHP via the API using the requests module.
The request asks Munkireport to return a list of Apple Caching Servers that have not checked in for more than 4 hours.

We then loop through those results and send an email alert to the school to alert them that their caching server is offline.

The last step is to send a summary email with a list of all the servers that are offline to a central IT support email address
so that they can investigate or follow up should the server continue to report as offline

Example of the email sent to owner of the caching server (ie the school)

"Subject: [WARNING] 1234 Apple Caching Server is OFFLINE

ATTN: The School ICT Coordinator

Your school's Apple Caching Server (ACS) currently appears to be offline and not functioning.


    It has not reported into our central monitoring system since: 01-01-2018

    Your caching server was built by John Smith, on January 01, 2017


Please ensure it is plugged into power and a working ethernet port and powered on.

If there are problems bringing your ACS online, please log a service desk call with <Alert System> on <1800 000 000>

Regards,

Alert System"

Example of the email sent to a central IT support or similar

"Subject: [WARNING] OFFLINE Apple Caching Server(s)

 

The following Apple Caching Servers are flagged as OFFLINE The school has been notified via an email sent to the school email address.

 

1234,Pretend HS,11:10:48 on 18-08-2017,Imaged by: Smith, Jon, on: Mon Jan 23 01:46:31 AEDT 2017

 

5678,Example PS,14:33:34 on 13-09-2017,Imaged by: Doe, Jane, on: Wed Mar 22 13:18:34 AEDT 2017

 

9012,Acme PS,11:48:03 on 13-09-2017,Imaged by: Doe, Jane, on: Tue May 30 12:15:00 AEST 2017

 


Regards,"




