# detect-unsigned-modules

A tool to detect when there is an unsigned kernel module loaded.
The idea is that afrer loading an unsigned module the message warning you about
it won't show up anymore.
So if you load a module that does nothing you can see if you get the message
printed or not.
This idea was briefly mentioned my article in tmp.0ut #4.

This POC uses the [singularity rootkit by MatheuZSecurity](https://github.com/MatheuZSecurity/Singularity/tree/main)
as a testcase as it is the best modern / public one that goes through the effort
to tamper with dmesg output.

## Usage

Remember you need to reboot between uses!

## License

MIT
