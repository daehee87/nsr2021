FROM ubuntu:18.04

RUN apt update && apt-get install -y git wget unzip libglib2.0-dev libeina-dev qemu-user qemu-user-static build-essential qemu-system-arm libtool-bin python automake bison gcc-arm-linux-gnueabi g++-arm-linux-gnueabi

# setup AFL++
RUN git clone https://github.com/AFLplusplus/AFLplusplus.git
WORKDIR /AFLplusplus
RUN AFL_NO_X86=1 make -j2
WORKDIR /AFLplusplus/qemu_mode
RUN CPU_TARGET=arm ./build_qemu_support.sh
WORKDIR /AFLplusplus
RUN AFL_NO_X86=1 make -j2

ENV QEMU_LD_PREFIX=/usr/arm-linux-gnueabihf

WORKDIR /
RUN mkdir input
RUN mkdir output
ADD target.bin .
ADD fuzz.sh /AFLplusplus/
#RUN ln -s `which r2` ./r2
RUN chmod +x /AFLplusplus/fuzz.sh

# (selectively) fuzz target.bin
WORKDIR /AFLplusplus
CMD ["./fuzz.sh"]


