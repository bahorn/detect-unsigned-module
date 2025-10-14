build-singularity:
    cd lkm/rk-s1ngularity/ && make clean && make

load-singularity:
    cp lkm/rk-s1ngularity/singularity.ko /tmp/s1ngularity.ko
    sudo insmod /tmp/s1ngularity.ko

build-kovid:
    cd lkm/kovid && make clean && DEPLOY=1 PROCNAME=kv make

load-kovid:
    cd lkm/kovid && sudo ./run.sh

build-goat:
    cd lkm/goat && make clean && make

load-goat:
    sudo insmod ./lkm/goat/goat.ko
    # does nothing so just rmmod it
    sudo rmmod goat

build-beautifullies:
    cd lkm/beautifullies && just extract-kernel && just build

load-beautifullies:
    cd lkm/beautifullies && just load

build-nitara2:
    cd lkm/nitara2 && make clean && make

batch-tests:
    # is something blocking use from turning ftrace off
    sudo python3 detections/can_disable_ftrace.py
    # look for singularity's init_module() hook
    sudo python3 detections/hooked_insmod.py
    # check if injecting seeks between reads causes a mismatch between the read
    # amount
    sudo python3 detections/seek_stutter.py /sys/kernel/debug/tracing/touched_functions
    # look at if the kernels taint resets every 5 seconds
    # if you have previously ran the tests this will return positive
    sudo python3 detections/pcrtest.py
    # check if kallsyms_lookup_name has been used
    sudo python3 detections/touched_kallsyms.py
    # compare the output of two different ways of reading the kernel message
    # buffer
    sudo python3 detections/diff_devkmsg_klogctl.py

batch-tests-lkm: batch-tests
    sudo python3 detections/unsigned_loaded.py
    sudo ./detections/nitara2.sh
