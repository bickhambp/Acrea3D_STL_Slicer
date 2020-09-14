#include <stdio.h>
#include <stdlib.h>

char readFile(){
    FILE *stl_file;
    int * stl_file_content = (int*)malloc(4000000);
    int temp;

    stl_file = fopen("/temp/stlfiledata.txt", "r");

    fscanf(stl_file, "%d", stl_file_content);
    fclose(stl_file);
    return temp;
}

int main(){
    printf("%d\n\r", readFile());
}