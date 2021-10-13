#!/bin/bash
echo 'building toy example...'
arm-linux-gnueabi-gcc -o toy /src/toy.c -static
echo 'check LOAD virtual base'
readelf -l toy
echo 'check target function virtual address'
nm -a toy | grep LLVM
echo 'building wrapper binary...'
arm-linux-gnueabi-gcc -o /target.bin /src/wrapper.c -static

ls -al /input
echo 'put genesis test case'
echo aaaaaaaa > /input/dummy
./afl-fuzz -Q -i /input -o /output -- /target.bin @@

echo 'spawning shell...'
/bin/bash
