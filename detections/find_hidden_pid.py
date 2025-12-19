import os
import ctypes
import os

# Load libc
libc = ctypes.CDLL(None)

# Syscall number for pidfd_open (varies by architecture)
# On x86_64 it's 434
SYS_pidfd_open = 434

# Flags for pidfd_open
PIDFD_NONBLOCK = 0o00004000  # O_NONBLOCK

def pidfd_open(pid, flags=0):
    result = libc.syscall(SYS_pidfd_open, pid, flags)
    
    if result == -1:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    
    return result


def main():
    pids = []
    for i in os.listdir('/proc'):
        if i.isdigit():
            pids.append(int(i))
    pids.sort()

    to_check = set([i for i in range(0, os.getpid())]) - set(pids)

    for i in to_check:
        try:
            # interchangable with any of the many syscalls that take a pid.
            a = pidfd_open(i)
            os.close(a)
            print(f'hidden pid: {i}')
        except:
            continue


if __name__ == "__main__":
    main()
