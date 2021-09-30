// compile with arm-linux-gnueabi-gcc
// avoid base address collision with target. use -Ttext=0xa000 gcc option to change ELF base.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>

void fuzz_entry(unsigned int addr, char* seed){
	__asm volatile("mov r0, %0"::"r"(seed));
	__asm volatile("mov r1, %0"::"r"(seed));
	__asm volatile("mov r2, %0"::"r"(seed));
	__asm volatile("mov r3, %0"::"r"(seed));

	// no need to distinguish arm/thumb. pass address as is.
	__asm volatile(
		"mov r6, %0\n\tbx r6\n\t"::"r"(addr)
	);
}

// PUT target's ELF base address here.
#define BASE ((void*)0x10000)

// use file interface with AFL++ (@@)
int main(int argc, char* argv[]){
	FILE* fp;
	size_t fsize;
	struct stat st;

	// load target binary
	size_t len_file;
	struct stat st;
	int fd = open("/target.bin", O_RDONLY);
	if( fstat(fd,&st) < 0){
		printf("cannot open /target.bin\n");
		return;
	}

	len_file = st.st_size;
	if (mmap(BASE, len_file, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE, fd, 0) != BASE){
		printf("mmap error!\n");
		return;
	}
	fclose(fd);

	// get AFL seed input
	fd = fopen(argv[1], "rb");
	stat(fd, &st);
	fsize = st.st_size;

	char* seed = (char*)malloc(fsize);
	read(fd, seed, fsize);

	// todo.
	// get target function address (including lsb)
	void* fptr = BASE;
	unsigned int offset = 0x500;	// put function's file offset here!
	fptr += offset;

	// start fuzzing.
	fuzz_entry(fptr, seed);
	return 0;
}

