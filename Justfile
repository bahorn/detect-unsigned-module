load-none:


update-submodules:
    cd lkm/rk-s1ngularity/ && git pull
    cd lkm/kovid/ && git pull
    cd lkm/nitara2 && git pull
    cd lkm/beautifullies && git pull


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

# testing our detections

batch-tests rootkit="none":
    just load-{{ rootkit }}
    # is something blocking use from turning ftrace off
    sudo python3 detections/can_disable_ftrace.py
    # a detection for singularity trying to break the previous detection
    sudo python3 detections/bad_ftrace_value.py
    # try using ftrace and look for symbols we use being filtered
    # temp disabled as it doesn't play nice with other detections
    # sudo python3 detections/try_ftrace.py
    # look for singularity's init_module() hook
    # MUST be done as an unprived user
    python3 detections/hooked_insmod.py
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
    # check if we have a matching number of create_trampolines created
    # allocations in /proc/vmallocinfo for the number of ftrace
    # touched_functions.
    # Experimental, might have false positives.
    sudo python3 detections/count_trampolines.py
    # Looks at who calls commonly hooked functions.
    # Ftrace provides caller information via trace_pipe, so we setup ftrace
    # normally and see if we spot an unexpected caller.
    # This can interfere with the current counting trampolines implementation.
    sudo python3 detections/function_trace_parents.py

batch-tests-lkm rootkit="none":
    just batch-tests {{ rootkit }}
    sudo python3 detections/unsigned_loaded.py
    sudo ./detections/nitara2.sh

baseline rootkit:
    -sudo rm -r a.baseline b.baseline
    sudo python3 baselining/system_snapshot.py a.baseline
    just load-{{ rootkit }}
    sudo python3 baselining/system_snapshot.py b.baseline
    -diff -r a.baseline b.baseline
