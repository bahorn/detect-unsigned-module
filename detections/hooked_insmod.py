"""
Singularity hooks init_module() and always returns ENOEXEC, even for unprived
users.

so if we try to load a module as an unprived user but get that instead of EPERM
thats a hook.
"""
import ctypes

# Load libc
libc = ctypes.CDLL(None, use_errno=True)

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
if ctypes.get_errno() != 8 and res != 0:
    print('no init_module() hook detected')
else:
    print('init_module() is hooked!')
