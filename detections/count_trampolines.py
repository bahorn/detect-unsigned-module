"""
count the number of ftrace trampolines in vmallocinfo and kallsyms and see if it
matches the number in touched_functions.

might have false positives, unsure how it handles removing ftrace hooks
"""

def normalize_lines(text):
    """Merge lines starting with whitespace to the previous line."""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        if line and line[0].isspace() and result:
            # Merge with previous line
            result[-1] += ' ' + line.lstrip()
        else:
            if line != '':
                result.append(line)
    return result

def has_flag(line, flag):
    parts = line.strip().split()
    if len(parts) < 3:
        return False
    return flag in parts[2:]

with open('/sys/kernel/debug/tracing/touched_functions') as f:
    enabled_functions = normalize_lines(f.read())

tramp_count_in_ftrace = 0
for func in enabled_functions:
    if not has_flag(func, 'D'):
        tramp_count_in_ftrace += 1

tramp_count_in_vmalloc = 0

with open('/proc/vmallocinfo', 'r') as f:
    for line in f:
        if 'create_trampoline' in line:
            tramp_count_in_vmalloc += 1

tramp_count_in_kallsyms = 0

with open('/proc/kallsyms', 'r') as f:
    for line in f:
        if '[__builtin__ftrace]' in line:
            tramp_count_in_kallsyms += 1

print(tramp_count_in_ftrace, tramp_count_in_vmalloc, tramp_count_in_kallsyms)
if tramp_count_in_ftrace != tramp_count_in_vmalloc or \
        tramp_count_in_ftrace != tramp_count_in_kallsyms:
    print('mismatched trampoline count!')
else:
    print('trampoline count matches')
