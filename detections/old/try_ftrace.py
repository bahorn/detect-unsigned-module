"""
try using ftrace and check stuff we are doing isn't being hidden from us
"""
to_check = ['__x64_sys_write', '__x64_sys_read']

with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'wb') as f:
    for s in to_check:
        f.write(bytes(s + '\n', 'ascii'))

# singularity fakes this value in recent versions, so we just try and setup a
# function
with open('/sys/kernel/debug/tracing/current_tracer', 'wb') as f:
    f.write(b'function\n')
import time

time.sleep(1)
with open('/dev/null', 'wb') as f:
    f.write(b'aaaa')

found = set()
c = 0
with open('/sys/kernel/debug/tracing/touched_functions', 'r') as f:
    for line in f:
        sym = line.split(' ')[0]
        print(sym)
        if sym in to_check:
            found = found.union([sym])
        c += 1


with open('/sys/kernel/debug/tracing/current_tracer', 'wb') as f:
    f.write(b'nop\n')

with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'wb') as f:
    f.write(b'\n')

if c == 0:
    print('no symbols have been touched, unexpected for modern distros')

print(found)
if len(found) != len(to_check):
    print('symbols are being filtered!')
else:
    print('didnt find symbol filtering')
