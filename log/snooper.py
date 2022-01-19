import pysnooper
with pysnooper.snoop(depth=2, output='log\py_variable.log'):
    # coding=utf-8
    while True:
        a,b=input().split()
        k=1
        if len(a)!=len(b):
            print("No")
            k=0
        elif len(a)==len(b)==0:
            print("Yes")
            k=0
        if k==1:
            List=[]
            List.append(a)
            for i in range(1,len(a)-1):
                List.append(a[i]+a[i+1:]+a[:i])
            List.append(a[-1]+a[:len(a)-1])
            if b in List:
                print("Yes")
            else:
                print("No")
