import time
import select
from collections import Counter


COMMONLY_HOOKED = {
        '__x64_sys_write': ['x64_sys_call'],
        '__x64_sys_kill': ['x64_sys_call']
        # ('__x64_sys_read', ['x64_sys_call']) # not great to hook reading
}

seen_counter = Counter()
seen = set()

# setup ftrace
with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'w') as f:
    f.write('\n'.join(COMMONLY_HOOKED.keys()) + '\n')

with open('/sys/kernel/debug/tracing/current_tracer','w') as f:
    f.write('function')

done = False

with open('/sys/kernel/debug/tracing/trace', 'w') as f:
    f.write('\n')

with open('/sys/kernel/debug/tracing/trace_pipe', 'r') as f:
    while not done:
        select.select([f], [], [], 0.1)

        line = f.readline()
        if not line:
            print('no data')
            time.sleep(1)
        if line[0] == '#':
            continue

        c = line.strip().split(' ')
        caller = c[-1][2:]
        target = c[-2]

        if target in COMMONLY_HOOKED:
            if caller not in COMMONLY_HOOKED[target]:
                print(f'{target} called by unexpected caller {caller}')
                break
        
        if target not in seen:
            seen.add(target)
        
        seen_counter.update([target])

        if len(seen) == len(COMMONLY_HOOKED):
            done = True
            for name in seen:
                if seen_counter[name] < 2:
                    done = False

with open('/sys/kernel/debug/tracing/current_tracer', 'w') as f:
    f.write('nop')

with open('/sys/kernel/debug/tracing/set_ftrace_filter', 'w') as f:
    f.write('\n')
