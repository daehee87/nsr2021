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
#define BASE ((void*)0x5555e000)

// use file interface with AFL++ (@@)
int main(int argc, char* argv[]){

	// load target binary
	size_t len_file;
	struct stat st;
	int bin_fd = open("./toy", O_RDONLY);
	if( fstat(bin_fd,&st) < 0){
		printf("cannot open /target.bin\n");
		return;
	}

	len_file = st.st_size;
	printf("binary size: %d bytes\n", len_file);
	if (mmap(BASE, len_file, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE, bin_fd, 0) != BASE){
		printf("mmap error!\n");
		return;
	}
	printf("mmap ok: %p\n", BASE);

	// get AFL seed input
	FILE* fp = fopen(argv[1], "rb");
	fseek(fp, 0, SEEK_END);
	int seed_size = ftell(fp);
	fseek(fp, 0, SEEK_SET);

	char* seed = (char*)malloc(seed_size);
	unsigned int r = fread(seed, 1, seed_size, fp);
	printf("read %d input bytes from AFL\n", r);

	// todo.
	// get target function address (including lsb)
	void* fptr = BASE;
	unsigned int offset = 0x2dc;	// put function's file offset from symtab
	fptr += offset;

	// start fuzzing.
	fuzz_entry(fptr, seed);
	_exit(0);	// noreturn
	return 0;
}


