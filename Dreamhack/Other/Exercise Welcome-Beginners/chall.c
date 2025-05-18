// Name: chall.c
// Compile Option: gcc chall.c -o chall -fno-stack-protector

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define FLAG_SIZE 0x45

void init() {
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stdout, 0, 2, 0);
}

int main(void) {
    int fd;
    char *flag;

    init();

    // read flag
    flag = (char *)malloc(FLAG_SIZE);
    fd = open("./flag", O_RDONLY);
    read(fd, flag, FLAG_SIZE);

    char cmp_str[10] = "Dreamhack";
    char inp_str[10];   
    printf("Enter \"Dreamhack\" : ");
    scanf("%9s", inp_str);

    if(strcmp(cmp_str, inp_str) == 0){
        puts("Welcome Beginners!");
        // print flag
        puts(flag);
    }
    
    return 0;
}