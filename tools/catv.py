"""
cat but with readv instead of read()

not my own work, written with claude 4.5
"""
import os
import sys
import ctypes

# Define iovec structure for readv/writev
class iovec(ctypes.Structure):
    _fields_ = [
        ("iov_base", ctypes.c_void_p),
        ("iov_len", ctypes.c_size_t)
    ]

libc = ctypes.CDLL(None, use_errno=True)

def cat_readv(filename):
    # Open file for reading (or use stdin if filename is "-")
    if filename == "-":
        fd = sys.stdin.fileno()
    else:
        fd = os.open(filename, os.O_RDONLY)
    
    try:
        # Create multiple buffers for vectorized I/O
        num_buffers = 4
        buffer_size = 4096
        
        # Allocate buffers
        buffers = [(ctypes.c_char * buffer_size)() for _ in range(num_buffers)]
        
        # Create iovec array
        iovecs = (iovec * num_buffers)()
        for i in range(num_buffers):
            iovecs[i].iov_base = ctypes.cast(buffers[i], ctypes.c_void_p)
            iovecs[i].iov_len = buffer_size
        
        stdout_fd = sys.stdout.fileno()
        
        while True:
            # readv syscall - reads into multiple buffers in one call
            bytes_read = libc.readv(fd, iovecs, num_buffers)
            
            if bytes_read <= 0:
                break
            
            # Write out the data we read
            remaining = bytes_read
            for i in range(num_buffers):
                if remaining <= 0:
                    break
                    
                chunk_size = min(remaining, buffer_size)
                os.write(stdout_fd, buffers[i][:chunk_size])
                remaining -= chunk_size
                
    finally:
        if filename != "-":
            os.close(fd)

# Usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        cat_readv("-")
    else:
        for filename in sys.argv[1:]:
            cat_readv(filename)
