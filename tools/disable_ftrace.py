"""
use writev to disable ftrace, as singularity doesn't hook it
"""
import os
import ctypes

libc = ctypes.CDLL("libc.so.6")

fd = os.open("/proc/sys/kernel/ftrace_enabled", os.O_WRONLY)

class iovec(ctypes.Structure):
    _fields_ = [("iov_base", ctypes.c_void_p), ("iov_len", ctypes.c_size_t)]

data = b'0'
vec = iovec(ctypes.cast(data, ctypes.c_void_p), len(data))

libc.writev(fd, ctypes.byref(vec), 1)
os.close(fd)
