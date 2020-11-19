#include<stdio.h>
int main()
{
    int a, n=1;
    scanf("%d", &a);
    for (int i = 1; i <= a;i++){
        n = n * a % 100;
    }
    printf("%d\n", n);
}