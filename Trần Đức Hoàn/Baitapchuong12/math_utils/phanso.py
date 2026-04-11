import math


def rut_gon(tu_so, mau_so):
    if mau_so == 0:
        raise ValueError("Mau so khong duoc bang 0")
    ucln = math.gcd(tu_so, mau_so)
    tu = tu_so // ucln
    mau = mau_so // ucln
    if mau < 0:
        tu = -tu
        mau = -mau
    return tu, mau


def cong(ps1, ps2):
    a, b = ps1
    c, d = ps2
    return rut_gon(a * d + b * c, b * d)


def tru(ps1, ps2):
    a, b = ps1
    c, d = ps2
    return rut_gon(a * d - b * c, b * d)


def nhan(ps1, ps2):
    a, b = ps1
    c, d = ps2
    return rut_gon(a * c, b * d)


def chia(ps1, ps2):
    a, b = ps1
    c, d = ps2
    if c == 0:
        raise ZeroDivisionError("Khong the chia cho phan so co tu so bang 0")
    return rut_gon(a * d, b * c)
