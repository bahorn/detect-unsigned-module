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

def try_write(value, write_extra=False):
    try:
        with open('/proc/sys/kernel/ftrace_enabled', 'wb', buffering=0) as f:
            f.write(bytearray(value))
            # this is a bit dumb, but i had problems getting my python code to
            # trigger something i could easily do from bash.
            # i eventually ftraced and saw a second write of two null bytes
            # which is where this comes from
            if write_extra:
                f.write(b'\x00\x001\x00\x00')
    except OSError:
        return False

    return True

if try_write(b'9999999999999999999') or \
        (not try_write(b'0xa')) or \
        try_write(b'0' * 32) or \
        (not try_write(b'1\x0a\x00', True)):
    print('singularity detected')
else:
    print('no tampering detected')
