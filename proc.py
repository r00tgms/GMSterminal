#!/usr/bin/python

# Copyright (C) 2017  Win-design

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



# Standard init

import pynag.Plugins
from tempfile import mkdtemp
from pynag.Plugins import WARNING, CRITICAL, OK, UNKNOWN, simple as Plugin
from subprocess import Popen, PIPE
import os
import time


def mktmpdir():
    """Returs path to newly create temporary directory"""

    return mkdtemp(prefix="check_tftp_")


def tftp_get(host, filename, dest=None, timeout=20):
    """Fetches a ftp file to dest or into tmpdir"""
    global np
    global tmpdir

    # Generate tmpdir if not stipulated
    if dest is None:
        dest = "%s/%s" % (tmpdir, os.path.basename(filename))

    # Execute tftp command
    tftp = Popen(['tftp', str(host), '-m', 'binary', '-c', 'get', str(filename), str(dest)],
                 stdout=PIPE,
                 stderr=PIPE)

    # How long to wait for exit of tftp command
    timeout = time.time() + timeout

    # Poll for exit of tftp process
    ret = None
    while timeout > time.time():
        ret = tftp.poll()
        if ret is not None: break
        time.sleep(1)

    # Get size and throw away file
    try:
        size = os.stat(dest).st_size
        os.unlink(dest)
    except Exception:
        pass

    # Timeout, cleanup and add message
    if ret is None:
        np.add_message(CRITICAL, "Timeout fetching tftp://%s/%s" % (host, filename))
        return False

    # Concat stdin and stderr in case of error
    output = tftp.stderr.readline().strip() + " " + tftp.stdout.readline().strip()

    # Bad tftp exit code, dest was not created or size is off
    if ret != 0 or not size:
        np.add_message(CRITICAL, "Unable to fetch tftp://%s/%s [rc=%i]: %s" % (host, filename, ret, output))
        return False

    return size


def main():
    global np
    global tmpdir

    # new pynag.Plugin
    np = Plugin(must_threshold=False)

    # Arguments
    np.add_arg('f', 'file', 'Remote file, space seperate multiple files', required=False)
    np.add_arg('w', 'warning', 'Warn if tftp downloads take longer', required=False)
    np.add_arg('c', 'critical', 'Critical if tftp downloads take longer', required=False)
    np.add_arg('l', 'longoutput', 'Each file broken up into a new line for readability', required=False,
               action="store_true")

    # Activate
    np.activate()

    if np['host'] == "":
        np.nagios_exit(UNKNOWN, "Hostname is required")

    tmpdir = mktmpdir()

    end_time = time.time() + int(np['timeout'] or 20)

# data.txt add manually contient list of file that we will check
  #  dirname = os.path.join('data', 'tftplist.txt')
    with open('/Users/R00T/PycharmProjects/untitled/data.txt', 'r') as myfile:
        files = myfile.read().replace('\n', '')
# creat list of ips #files = np['file'].split()


    with open('/Users/R00T/PycharmProjects/untitled/ips.txt', 'r') as myips:
        ips = myips.read().replace('\n', '')


    # Loop through the files
    for ip in ips:
        for file in files:
            file_start_time = time.time()
            try:
                size = tftp_get(ip, file, timeout=(end_time - time.time()))
                file_end_time = time.time()
                run_time = time.time() - file_start_time

                if size is not False:
                    if np['critical'] and run_time >= int(np['critical']):
                        stat = CRITICAL
                    elif np['warning'] and run_time >= int(np['warning']):
                        stat = WARNING
                    else:
                        stat = OK
                    np.add_message(stat, "tftp://%s/%s got %iB in %.2f secs" %
                                   (np['host'], file,
                                    size, (file_end_time - file_start_time)))

                    np.add_perfdata("%s_size" % (file), size)

                    np.add_perfdata("%s_fetch" % (file),
                                    (file_end_time - file_start_time))

            except Exception, e:
                np.nagios_exit(UNKNOWN, e)

    # Check and return
    (ret, output) = np.check_messages(joinallstr=(np['longoutput'] and "\n" or " "))
    os.rmdir(tmpdir)
    np.nagios_exit(ret, output)


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        np.nagios_exit(UNKNOWN, "Exception: %s" % (e))
