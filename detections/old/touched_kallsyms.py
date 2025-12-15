"""
`touched_functions` is an easy detection for the kprobe trick to get the address
of `kallsyms_lookup_name()` [1].

[1] https://github.com/xcellerator/linux_kernel_hacking/issues/3#issuecomment-757951117
"""
with open('/sys/kernel/debug/tracing/touched_functions', 'r') as f:
    for line in f.read().split('\n'):
        if 'kallsyms_lookup_name' in line:
            print('SUS', line)
