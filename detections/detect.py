#!/usr/bin/env python3
import os
import select

lines = []

os.system('insmod ./lkm/goat/goat.ko')
os.system('rmmod goat')

with open('/dev/kmsg', 'rb') as f:
    while select.select([f], [], [], 1)[0]:
        lines.append(f.readline())

first_find = b'Goat Loaded'
search_str = b"module verification failed: signature and/or required key missing"

found = False
for line in lines[:-5:-1]:
    print(line)
    if first_find in line:
        found = True
    elif found and search_str in line:
        break
    elif found and search_str not in line:
        found = False
        break
    else:
        found = False

if found:
    print('no unsigned module has been loaded before now')
else:
    print('unsigned module has previously been loaded!!')
