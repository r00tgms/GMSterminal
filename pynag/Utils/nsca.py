"""Module for dealing with NSCA."""
import platform
import subprocess


def send_nsca(code, message, nscahost, hostname=None, service=None, nscabin="send_nsca", nscaconf=None):
    """ Send data via send_nsca for passive service checks

    Args:

        code (int): Return code of plugin.

        message (str): Message to pass back.

        nscahost (str): Hostname or IP address of NSCA server.

        hostname (str): Hostname the check results apply to.

        service (str): Service the check results apply to.

        nscabin (str): Location of send_nsca binary. If none specified whatever
        is in the path will be used.

        nscaconf (str): Location of the NSCA configuration to use if any.

    Returns:

        [result,stdout,stderr] of the command being run
    """

    if not hostname:
        hostname = platform.node()

    # Build command
    command = [nscabin, '-H', nscahost]
    if nscaconf:
        command += ['-c', nscaconf]

    # Just in case, status code was sent in as an integer:
    code = str(code)

    # Build the input string
    if service:
        input_string = '\t'.join([hostname, service, code, message]) + '\n'
    else:
        input_string = '\t'.join([hostname, code, message]) + '\n'

    # Execute command

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=input_string)
    result = proc.returncode, stdout, stderr

    return result
