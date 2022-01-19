#include<stdio.h>
int main() {
    int a, b, n = 1;
    scanf("%d %d", &a, &b);
    if(b % 2 == 0) {
        a = a + b;
        n = a + n % 100;
    } else {
        a = a - b;
        n = n + a / 100;
    }
    printf("%d\n", n);
}