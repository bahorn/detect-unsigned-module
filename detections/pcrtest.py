"""
PCRtest.py - bah / November 2024
A quick / dirty test for recent versions of the Kovid LKM rootkit.
If you write to /proc/sys/kernel/tainted, kovid unset a few bits.
You can use resetting behaviour to detect it.
Run this script as root.

originally shared at:
https://gist.github.com/bahorn/b2ed75066c118bd36419ad4e3b4862a0
"""
import time


with open('/proc/sys/kernel/tainted', 'r') as f:
    first = f.read()


with open('/proc/sys/kernel/tainted', 'wb') as f:
    f.write(b'64')

time.sleep(6)

with open('/proc/sys/kernel/tainted', 'r') as f:
    second = f.read()

if first == second:
    print('you have kovid')
else:
    print('clean')
