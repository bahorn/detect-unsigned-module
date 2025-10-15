# to work out what we should ignore
sudo rm -r a b
sudo python3 system_snapshot.py a.baseline
sleep 5
sudo python3 system_snap/shot.py b.baseline
diff -r a.baseline b.baseline | grep "diff -r" | python3 get_ignore_list.py /dev/stdin
