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
    exit()

with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'wb') as f:
    f.write(b'run_init_process\n')
    f.write(b'__x64_sys_write\n')

# singularity fakes this value in recent versions, so we just try and setup a
# function
with open('/sys/kernel/debug/tracing/current_tracer', 'wb') as f:
    f.write(b'function\n')

with open('/dev/null', 'wb') as f:
    f.write(b'aaaa')

faking = False
with open('/sys/kernel/debug/tracing/trace', 'r') as f:
    for line in f:
        if '#' not in line:
            faking = True

with open('/sys/kernel/debug/tracing/enabled_functions', 'r') as f:
    if 'run_init_process' in f.read():
        faking = True

with open('/sys/kernel/debug/tracing/current_tracer', 'wb') as f:
    f.write(b'nop\n')

with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'wb') as f:
    f.write(b'\n')

if not faking:
    print('able to disable ftrace, restoring')
else:
    print('faking ftrace being disabled. probably singularity')

with open('/proc/sys/kernel/ftrace_enabled', 'wb') as f:
    f.write(b'1\n')

