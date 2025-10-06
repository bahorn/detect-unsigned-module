# detect-unsigned-modules

A tool to detect when there is an unsigned kernel module loaded.

This POC uses the [singularity rootkit by MatheuZSecurity](https://github.com/MatheuZSecurity/Singularity/tree/main)
as a testcase as it is the best modern / public one that goes through the effort
to tamper with dmesg output.

## Usage

### Setup

Build the LKMs with:
```
just build-goat
just build-singularity
```

### `detect.py`

This loads an unsigned module, and tries to see if you get the message about
how loading one taints the kernel.
If you don't get this message, its a good indicator about how one is currrently
already loaded.
This idea was briefly mentioned in my articlen tmp.0ut #4.

```
sudo python3 detect.py
```

Should say if one is probably loaded or not.
Remember to reboot if you have already ran it.

`detect_with_loaded.sh` is a test case that should trigger a detection with
singularity.

### `diff_devkmsg_klogctl.py`

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

## License

MIT for detections, GPL for the goat kernel module (if that is even
copyrightable)
