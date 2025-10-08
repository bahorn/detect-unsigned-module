"""
try using write() to disable ftrace.

if it fails, something is probably hooking it.
"""

with open('/proc/sys/kernel/ftrace_enabled', 'rb') as f:
    orig = f.read()

if orig == b'0\n':
    print('already disabled')
    exit()

with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
    f.write(b'0\n')

with open('/proc/sys/kernel/ftrace_enabled', 'rb') as f:
    curr = f.read()

if curr == orig:
    print('unable to disable ftrace')
else:
    print('able to disable ftrace, restoring')
    with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
        f.write(b'1\n')

