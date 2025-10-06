#!/usr/bin/env python3
import ctypes
import os
import select
import itertools

# we need to get something into the dmesg after singularity loads otherwise its
# hooks cause inf loops.
os.system('echo "userland" | sudo tee /dev/kmsg')

kmsg_lines = []
with open('/dev/kmsg', 'rb') as f:
    while select.select([f], [], [], 0.1)[0]:
        kmsg_lines += f.readline().decode('unicode_escape').strip().split('\n')

kmsg_lines = filter(lambda x: x[0] in '1234567890', kmsg_lines)

libc = ctypes.CDLL(None)
klogctl = libc.klogctl
klogctl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
klogctl.restype = ctypes.c_int

buf_size = klogctl(10, None, 0)

buffer = ctypes.create_string_buffer(buf_size)
klogctl(3, buffer, buf_size)

klogctl_lines = buffer.value.decode('ascii').split('\n')


# trashfire of a script to normalize these lines
lines_a = []
lines_b = []
for a, b in itertools.zip_longest(klogctl_lines, kmsg_lines):
    if a is not None:
        try:
            line_a = a.split(']', 1)[1].strip()
            # print('a> ', a)
            lines_a.append(line_a)
        except:
            pass

    if b is not None:
        line_b = b.split(';', 1)[1].strip()
        # print('b> ', line_b)
        lines_b.append(line_b)


# lazy lol
with open('/tmp/a.txt', 'w') as f:
    f.write('\n'.join(lines_a))

with open('/tmp/b.txt', 'w') as f:
    f.write('\n'.join(lines_b))


os.system("diff --color=always /tmp/a.txt /tmp/b.txt")
os.system("rm /tmp/a.txt /tmp/b.txt")
