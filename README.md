# detect-unsigned-modules

A tool to detect when there is an unsigned kernel module loaded.

This POC uses the [singularity rootkit by MatheuZSecurity](https://github.com/MatheuZSecurity/Singularity/tree/main)
as a testcase as it is the best modern / public one that goes through the effort
to tamper with dmesg output.

## Usage

### Setup

Build the LKMs with?
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

## License

MIT for detections, GPL for the goat kernel module (if that is even
copyrightable)
