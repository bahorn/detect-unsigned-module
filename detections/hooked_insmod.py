"""
Singularity hooks init_module() and always returns zero, even for unprived
users.

so attempt loading an invalid module and see if we get that return code.
"""
import ctypes

# Load libc
libc = ctypes.CDLL(None)

# init_module syscall number (x86_64)
SYS_init_module = 175

# Create buffer of 'A's
buffer = b'A' * 1024

# Call init_module
res = libc.syscall(
    SYS_init_module,
    ctypes.c_char_p(buffer),
    ctypes.c_ulong(len(buffer)),
    ctypes.c_char_p(b"")
)
if res != 0:
    print('no init_module() hook detected')
else:
    print('init_module() is hooked!')
