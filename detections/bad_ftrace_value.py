"""
singularity as of 2025-12-06 has a bug in how it attempts to stop you disabling
ftrace.

if you write a random value to any file on disk called `ftrace_enabled` all
other files with the same name will have the same content.
you can detect this behaviour by writing to /tmp/ftrace_enabled and then try to
read the sysctl() version.
"""

VALUE = b'-99999999999999999999'

try:
    with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
        f.write(VALUE)
except OSError:
    print('not tampering with ftrace_enabled')
    exit()

import time
time.sleep(1)

with open('/proc/sys/kernel/ftrace_enabled', 'rb') as f:
    curr = f.read()

print(curr)
if curr in VALUE:
    print('s1ngular1ty detected')
else:
    print('weird behaviour, able to write invalid value to ftrace_enabled but its not preserved')
