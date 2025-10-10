with open('/sys/kernel/debug/tracing/touched_functions', 'r') as f:
    for line in f.read().split('\n'):
        if 'kallsyms_lookup_name' in line:
            print('SUS', line)
