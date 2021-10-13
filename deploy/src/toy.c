#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void LLVMFuzzerTestOneInput(u_int8_t* bytes, size_t len){
    if(bytes[0] == 'F')
    if(bytes[1] == 'U')
    if(bytes[2] == 'Z')
    if(bytes[3] == 'Z'){
	// artificial bug with sufficient code coverage
        *((int*)0xdeadbeef) = 0xcafebabe;
    }
}

void main(){
	printf("this is a toy example for select-fuzz\n");
	LLVMFuzzerTestOneInput("hey", 3);
}
