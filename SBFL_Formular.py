# -*- coding: utf-8 -*-
import math

debug = False

'''
Ncf = 失败测试样例中执行该行的数量
Nuf = 失败测试样例中未执行该行的数量
Ncf + Nuf为总失败样例数
Ncp = 成功测试样例中执行该行的数量
Nup = 成功测试样例中未执行该行的数量
Ncp + Nup为总成功样例数
'''

def cal_jaccard(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("jaccard:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncf + Nuf + Ncp
    if a == 0:
        return 0
    b = Ncf / a
    return b

def cal_naish(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("naish:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncp + Nup + 1
    b = Ncf - Ncp / a
    return b

def cal_GP08(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP08:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncf * Ncf
    b = 2 * Ncp + 2 * Ncf + 3 * Nup
    c = a * b
    return c

def cal_GP10(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP10:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    if Nup == 0:
        return 0
    a = Ncf - 1 / Nup
    print(a)
    b = math.sqrt(a)
    return b

def cal_GP11(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP11:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncf * Ncf
    b = math.sqrt(Nup)
    c = a * (a + b)
    return c

def cal_GP13(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP13:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = 2 * Ncp + Ncf
    if a == 0:
        return 0
    b = Ncf * (1 + 1 / a)
    return b

def cal_GP20(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP20:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncp + Nup
    if a == 0:
        return 0
    b = 2 * (Ncf + Nup / a)
    return b

def cal_GP26(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("GP26:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncf * Ncf
    b = math.sqrt(Nup)
    c = 2 * a + b
    return c

def cal_turantula(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("turantula:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    if Ncf + Nuf == 0:
        a = 0
    else:
        a = Ncf / (Ncf + Nuf)
    if Ncp + Nup == 0:
        b = 0
    else:
        b = Ncp / (Ncp + Nup)
    if a + b == 0:
        return 0
    c = a / (a + b)
    return c

def cal_dstar(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("Dstar:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncp + Nuf
    if a == 0:
        return 0
    b = math.pow(Ncf, 3) #3次方是作者推荐的
    c = b / a
    return c


def cal_ochiai(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("Ochiai:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    if Ncf + Nuf == 0:
        return 0
    a = Ncf + Ncp
    b = math.sqrt((Ncf + Nuf) * a)
    if b == 0:
        return 0
    c = Ncf / b
    return c


def cal_ochiai_new(Ncf, Nuf, Ncp, Nup):
    if debug:
        print("Ochiai_new:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    if Ncf + Nuf == 0:
        return 0
    a = Ncf + Ncp
    b = math.sqrt((Ncf + Nuf) * a)
    if b == 0:
        return 0
    c = math.pow(Ncf, 3) / b #3次方是作者推荐的
    return c


def cal_op2(Ncf, Nuf, Ncp, Nup):
    if debug:
     print("op2:%d %d %d %d" %(Ncf, Nuf, Ncp, Nup))
    a = Ncp / (Ncp + Nup + 1)
    b = Ncf - a
    return b