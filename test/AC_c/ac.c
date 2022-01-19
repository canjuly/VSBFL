#include<stdio.h>
int main() {
    int x, y, m = 1;
    scanf("%d %d", &x, &y);
    if(y % 2 == 0) {
        x = x + y;
        m = m + x % 100;
    }
    else {
        x = x - y;
        m = m + x / 100;
    }
    printf("%d\n", m);
}

