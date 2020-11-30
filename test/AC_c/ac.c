#include<stdio.h>
int main()
{
    int b, m=1;
    scanf("%d", &b);
    for (int i = 1; i <= b;i++){
        m = m * b % 100;
    }
    printf("%d\n", m);
}