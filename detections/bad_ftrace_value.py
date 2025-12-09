"""
singularity as of 2025-12-06 has a bug in how it attempts to stop you disabling
ftrace.

if you write a random value to any file on disk called `ftrace_enabled` all
other files with the same name will have the same content.
you can detect this behaviour by writing to /tmp/ftrace_enabled and then try to
read the sysctl() version.
"""

VALUE = b'abcd'

with open('/tmp/ftrace_enabled', 'wb') as f:
    f.write(VALUE)

import time
time.sleep(1)

with open('/proc/sys/kernel/ftrace_enabled', 'rb') as f:
    curr = f.read()

print(curr)
if VALUE in curr:
    print('s1ngular1ty detected')
else:
    print('not hooking all reads of files called `ftrace_enabled`')

import os
os.remove('/tmp/ftrace_enabled')
