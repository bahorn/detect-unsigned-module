build-singularity:
    cd lkm/rk-s1ngularity/ && make clean && make

load-singularity:
    cp lkm/rk-s1ngularity/singularity.ko /tmp/s1ngularity.ko
    sudo insmod /tmp/s1ngularity.ko

build-goat:
    cd lkm/goat && make clean && make

build-nitra2:
    cd lkm/nitra2 && make clean && make
