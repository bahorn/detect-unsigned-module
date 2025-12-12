"""
singularity as of 2025-12-06 has a bug in how it attempts to stop you disabling
ftrace.

if you write a random value to any file on disk called `ftrace_enabled` all
other files with the same name will have the same content.
you can detect this behaviour by writing to /tmp/ftrace_enabled and then try to
read the sysctl() version.

singularity atm doesn't support hex constants, so we can exploit that for
detection.
"""
import time

def try_write(value):
    try:
        with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
            f.write(value) 
    except OSError:
        return False

    return True

if try_write(b'9999999999999999999') or \
        (not try_write(b'0xa')) or \
        (try_write(b'0' * 32)):
    print('singularity detected')
else:
    print('no tampering detected')
