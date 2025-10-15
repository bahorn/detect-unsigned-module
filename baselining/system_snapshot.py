#!/usr/bin/env python3
"""
Simple tool to snapshot /sys and /proc.
Handles files that block on read or don't support reading.

written by claude 4.5 and with patches by me bah
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Files/directories known to block on read or cause issues
SKIP_ITEMS = {
    # Tracing files that block
    'trace_pipe',
    'trace_pipe_raw',
    'snapshot_pipe',
    'snapshot_raw',
    'revision',
    
    # Other blocking/problematic files
    'kmsg',
    'kcore',
    'kpageflags',
    'kpagecount',
    
    # Virtual/dynamic directories
    'self',
    'thread-self',

    'max_bytes',
    'wakeup_sources',
    'zone_info',
    'timer_list',
    'slabinfo',
    'buddyinfo',
    'diskstats',
    'interupts',
    'meminfo',
    'loadavg',
    'pagetypeinfo',
    'schedstat',
    'softirqs',
    'uptime',
    'vmstat',
    'zoneinfo',
    'interrupts'
}

# Patterns for files to skip
SKIP_PATTERNS = {
    '_trigger',
    'free_buffer',
    'lru_gen'
}

# Directories to skip entirely
SKIP_DIRS = {
    '/proc/bus/pci',  # Binary PCI config space
    '/sys/kernel/debug/dri',  # Can hang on some GPU debugfs files
    '/sys/kernel/slab',
    '/sys/kernel/irq',
    '/sys/fs',
    '/sys/devices',
    '/proc/fs',
    '/proc/presure',
    '/sys/kernel/debug/bdi',
    '/sys/kernel/debug/block',
    '/sys/kernel/debug/tracing/per_cpu',
    '/sys/kernel/debug/extfrag',
    '/sys/kernel/tracing/per_cpu',
    '/proc/pressure',
    '/proc/stat',
    '/proc/driver/rtc',
    '/sys/kernel/debug/sched/debug'
}

def is_pid_dir(name):
    """Check if directory name is a PID (all digits)."""
    return name.isdigit()

def should_skip(filepath, is_dir=False):
    """Check if file/directory should be skipped."""
    name = os.path.basename(filepath)
    
    # Skip PIDs in /proc
    if is_dir and '/proc/' in filepath and is_pid_dir(name):
        return True
    
    # Skip known items
    if name in SKIP_ITEMS:
        return True
    
    # Skip entire directory paths
    for skip_dir in SKIP_DIRS:
        if filepath.startswith(skip_dir):
            return True
    
    # Skip files matching patterns
    if not is_dir:
        for pattern in SKIP_PATTERNS:
            if pattern in name:
                return True
    
    return False

def copy_file_safe(src, dst, max_size=10*1024*1024):
    """Safely copy a file, handling errors and size limits."""
    try:
        # Check file size first (some sysfs/proc files report 0 but aren't)
        stat_info = os.stat(src)
        
        # Skip if it looks like a directory or special file
        if not os.path.isfile(src):
            return 'skip'
        
        with open(src, 'rb') as f:
            # Read with size limit to avoid huge files
            content = f.read(max_size + 1)
            if len(content) > max_size:
                content = content[:max_size] + b'\n[TRUNCATED - file too large]\n'
        
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(content)
        return 'ok'
    except (PermissionError, OSError, IOError) as e:
        # Write error info instead of the file content
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w') as f:
            f.write(f"[ERROR: {type(e).__name__}: {e}]\n")
        return 'error'

def snapshot_tree(source_dir, output_base, label):
    """Create a snapshot of a directory tree."""
    source = Path(source_dir)
    output = output_base / label
    
    if not source.exists():
        print(f"Warning: Source directory {source_dir} does not exist, skipping")
        return
    
    copied = 0
    skipped = 0
    errors = 0
    
    print(f"\nSnapshotting {source_dir} -> {output}")
    
    for root, dirs, files in os.walk(source, followlinks=False):
        # Calculate relative path
        rel_root = os.path.relpath(root, source)
        
        # Filter out directories to skip
        original_dirs = dirs[:]
        dirs[:] = []
        for d in original_dirs:
            full_path = os.path.join(root, d)
            if not should_skip(full_path, is_dir=True):
                dirs.append(d)
            else:
                skipped += 1
        
        for filename in files:
            src_path = os.path.join(root, filename)
            
            if should_skip(src_path, is_dir=False):
                skipped += 1
                continue
            
            # Build destination path
            if rel_root == '.':
                dst_path = output / filename
            else:
                dst_path = output / rel_root / filename
            
            result = copy_file_safe(src_path, dst_path)
            if result == 'ok':
                copied += 1
            elif result == 'error':
                errors += 1
            else:
                skipped += 1
    
    print(f"  Copied: {copied}, Skipped: {skipped}, Errors: {errors}")

def main():
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"system_snapshot_{timestamp}"
    
    output_base = Path(output_dir)
    
    if output_base.exists():
        print(f"Error: Output directory {output_dir} already exists")
        sys.exit(1)
    
    output_base.mkdir(parents=True)
    
    print(f"Creating system snapshot in: {output_dir}")
    # Snapshot each major tree
    snapshot_tree("/sys", output_base, "sys")
    snapshot_tree("/proc", output_base, "proc")
    
if __name__ == "__main__":
    main()
