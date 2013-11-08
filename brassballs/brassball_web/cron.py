#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brassballs.settings")

    from django.core.management import execute_from_command_line

#from django.core.management import setup_environ
#from mysite import settings

#setup_environ(settings)

#sys.path.append('/path/to/your/project/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

import smtplib
html = 'html version'
text = 'TEST VERSION'
subject = "BACKUP REPORT"
message = "HEY HEY" 
server = smtplib.SMTP('localhost')
server.sendmail('sender@host.com', 'gerrithall@gmail.com', message)
server.quit()
