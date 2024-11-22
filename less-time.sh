#! /usr/bin/env sh
#tail --lines=+1 time_out/time_*.txt | less
tail --lines=+1 $(find time_out/ -maxdepth 1 -name 'time_*.txt' -print | sort -r) | less -c
