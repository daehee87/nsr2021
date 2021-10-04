#!/bin/bash
./afl-fuzz -Q -i /input -o /output -- /target.bin @@
