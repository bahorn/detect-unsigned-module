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

# first we try too large of a value, that detects older versions
def to_large():
    VALUE = b'9999999999999999999'

    try:
        with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
            f.write(VALUE)
    except OSError:
        return False

    time.sleep(1)

    with open('/proc/sys/kernel/ftrace_enabled', 'rb') as f:
        curr = f.read()

    print(curr)
    return True

# otherwise write a hex value, which singularity does't support
# til you patch it :) hi!
def with_hex():
    try:
        with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
            f.write(b'0xa')
    except OSError:
        return True

    return False

if to_large() or with_hex():
    print('singularity detected')
else:
    print('no tampering detected')
