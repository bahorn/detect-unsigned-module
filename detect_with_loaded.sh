#!/bin/sh
just build-singularity
just load-singularity
just build-goat
sudo python3 detect.py
