# detect-unsigned-modules

Various scripts implementing detections for linux LKM rookits.

The scripts are tested against:
* [singularity rootkit by MatheuZSecurity](https://github.com/MatheuZSecurity/Singularity/tree/main),
  only public one that goes through the effort to tamper with dmesg output.
* [kovid by carloslack](https://github.com/carloslack/KoviD/tree/master)

## Usage

### Setup

Build the LKMs with:
```
just build-goat
just build-nitara2
just build-singularity
just build-kovid
just build-beautifullies # custom module to test detection bypass approaches
```

### Detections

These are found in `detections/` and can be ran with `just batch-tests` or `just
batch-tests-lkm` (to include ones that load an LKM)

#### `unsigned_loaded.py`

This loads an unsigned module, and tries to see if you get the message about
how loading one taints the kernel.
If you don't get this message, its a good indicator about how one is currrently
already loaded.
This idea was briefly mentioned in my articlen tmp.0ut #4.

```
sudo python3 unsigned_loaded.py
```

Should say if one is probably loaded or not.
Remember to reboot if you have already ran it.

#### `diff_devkmsg_klogctl.py`

This tool diffs the output between two ways of reading the kernel message
buffer, as both aren't hooked in some rootkits.
This one doesn't need the setup to be ran.

```
sudo python3 diff_devkmsg_klogctl.py
```

You shouldn't get many differences shown on clean systems (though its possible
because of my poor attempt at line normalization and maybe log levels).

If you get lines like:
* missing systemd-journal entries, as singularity removes lines containing
  "journal".
* lines about loading modules.
* the whole buffer being in only one, as kovid's run.sh clears the buffer.

those are pretty good detection signals.

For example, if you load singularity after already running `detect.py`, you'll
get output like:

```
$ sudo python3 diff_devkmsg_klogctl.py
539,540d538
< systemd[1]: Listening on systemd-journald-dev-log.socket - Journal Socket (/dev/log).
< systemd[1]: Listening on systemd-journald.socket - Journal Socket.
549d546
< systemd[1]: Starting systemd-journald.service - Journal Service...
552d548
< systemd-journald[277]: Collecting audit messages is disabled.
567d562
< systemd[1]: Started systemd-journald.service - Journal Service.
569,570d563
< systemd-journald[277]: Received client request to flush runtime journal.
< systemd-journald[277]: File /var/log/journal/5b8d8f5c116e4bb68ecb9d786884a225/system.journal corrupted or uncleanly shut down, renaming and replacing.
598d590
< systemd-journald[277]: File /var/log/journal/5b8d8f5c116e4bb68ecb9d786884a225/user-1000.journal corrupted or uncleanly shut down, renaming and replacing.
600d591
< CPU: 0 PID: 997 Comm: sshd Not tainted 6.8.0-85-generic #85-Ubuntu
664d654
< [    277]     0   277    10543     1090      288      800         2    94208        0          -250 systemd-journal
697d686
< goat: module verification failed: signature and/or required key missing - tainting kernel
700d688
< singularity: loading out-of-tree module taints kernel.
```

#### `hooked_insmod.py`

Singularity hooks `init_module()` to always
return 0, even for unpriv'd users.
So you can attempt to load an invalid module from any user and see if the return
code is 0, and if so you got a detection.

```
python3 hooked_insmod.py
```

#### `can_disable_ftrace.py`

Checks if it is possible to disable ftrace.
Singularity hooks `write()` to try and stop it being disables, but this
behaviour is detectable.

```
sudo python3 can_disable_ftrace.py
```

#### `nitara2.sh`

Uses nitara2 to see if it detects anything.
Singularity currently bypasses upstream nitara2, but the submodule include a
patch to work around it.
Kovid also does, no fix yet.

```
sudo nitara2.sh
```

#### `pcrtest.py`

Detects kovid by looking at if the kernels taint value is reset every 5 seconds.

```
sudo python3 pcrtest.py
```

#### `touched_kallsyms.py`

The [classic kprobe trick to get the address of `kallsyms_lookup_name()`](https://github.com/xcellerator/linux_kernel_hacking/issues/3#issuecomment-75795111) leaves
an artifact in `/sys/kernel/debug/tracing/touched_functions`.
If you grep that file for `kallsyms_lookup_name` and find it, someone used the
trick.

```
sudo python3 touched_kallsyms.py
```

### Tools

These are found in `tools/` and might be handy in some cases.


#### `disable_ftrace.py`

Uses `writev()` as a work around to disable basic attempts at stoping ftrace
from being disabled.

Run this if you can't load a module, or want to use the systems with the hooks
all gone for deploying further forensics tools.

```
sudo python3 disable_ftrace.py
```

(the current version of singularity patched this specific syscall, but other
disable'ing techniques exist. @ me if you need one)

#### `1bt.py`

Read a file one byte at a time to bypass some hooks.

```
sudo python3 1bt.py /path/to/file
```

#### `catv.py`

`cat` but with `readv()` instead. just to bypass incomplete hooks.

```
sudo python3 catv.py /path/to/file
```

(written using claude 4.5, as the models can currently generate sample syscall
usage code pretty well. if this breaks, regen with another read like syscall)

## License

MIT for detections, GPL for the goat kernel module (if that is even
copyrightable)
