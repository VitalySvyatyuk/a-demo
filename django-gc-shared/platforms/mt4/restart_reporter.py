#!/usr/bin/env python
"""This is a windows script that restarts reporter after checking imap mailbox,
and finding a report
"""

import subprocess
import traceback
from wsgiref.simple_server import make_server

import os
import os.path

# noinspection PyPackageRequirements
import MySQLdb
import logging

# Set this if debugging

DEBUG_MODE = False

# Configure logging
MODULE_PATH = os.path.dirname(__file__)
LOG_DIR = MODULE_PATH
LOG_FILENAME = os.path.join(LOG_DIR, 'restart_report.log')
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, filename=LOG_FILENAME)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

log = logging.getLogger('reporter_restarter')
log.addHandler(stream_handler)


REPORTER_BINARY = r'C:\report\mtreportsrv.exe'

# The IPs from which it is allowed to fetch the restart URL
ALLOWED_IPS = ['127.0.0.1', '188.40.109.81', '188.40.109.120']

# The port, on which WSGI will listen
LISTEN_PORT = 8135

MT4_MYSQL_ACCESS = {
    'host': '95.215.1.135',
    'db': 'gcmtsrv',
    'user': 'webuser',
    'passwd': 't@^tuinoahoa',
}


def restart_reporter():
    log.debug('Restarting MT4 report server')

    # Assert that we can see the mysql database
    # This will raise an exception if it cannot connect
    connection = MySQLdb.connect(**MT4_MYSQL_ACCESS)
    cursor = connection.cursor()

    # Kill existing reporter
    binary_name = os.path.basename(REPORTER_BINARY)
    process = 'taskkill /im "%s" /f' % binary_name
    log.debug('Executing %s' % process)
    if not DEBUG_MODE:
        os.system(process)

    # Flush mysql tables
    if not DEBUG_MODE:
        try:
            cursor.execute('DROP TABLE mt4_config')
        except MySQLdb.Error:
            # This can happen if there is no such table
            pass
        else:
            connection.commit()

    # Start new reporter
    log.debug('Executing %s' % REPORTER_BINARY)
    if not DEBUG_MODE:
        subprocess.Popen(REPORTER_BINARY)


class RestartReporterWSGI(object):

    def __call__(self, environ, start_response):
        # Initial headers
        headers = {
            'Content-Type': 'text/plain'
        }
        transform_headers = lambda headers: headers.items()
        if not self.has_access(environ):
            start_response('403 Forbidden', transform_headers(headers))
            return 'Access denied'
        try:
            restart_reporter()
        except MySQLdb.Error:
            start_response('500 Internal Error', transform_headers(headers))
            return traceback.format_exc()
        else:
            start_response('200 OK', transform_headers(headers))
        return ''

    @staticmethod
    def has_access(environ):
        if environ['REMOTE_ADDR'] not in ALLOWED_IPS:
            return False
        return True


if __name__ == '__main__':

    # Start reporter for the first time. After that, it will be restarted
    # by the WSGI server
    restart_reporter()
    server = make_server('', LISTEN_PORT, RestartReporterWSGI())
    log.info('Starting serving on port %s' % LISTEN_PORT)
    server.serve_forever()