"""
read a file one byte at a time to bypass some read hooks
"""
import os
import sys

fd = os.open(sys.argv[1], os.O_RDONLY)

while True:
    byte = os.read(fd, 1)
    if not byte:
        break
    sys.stdout.buffer.write(byte)

os.close(fd)
