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

build-nitra2:
    cd lkm/nitra2 && make clean && make
