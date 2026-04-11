import math


def chu_vi_hinh_tron(ban_kinh):
    return 2 * math.pi * ban_kinh


def dien_tich_hinh_tron(ban_kinh):
    return math.pi * ban_kinh * ban_kinh


def chu_vi_hinh_chu_nhat(chieu_dai, chieu_rong):
    return 2 * (chieu_dai + chieu_rong)


def dien_tich_hinh_chu_nhat(chieu_dai, chieu_rong):
    return chieu_dai * chieu_rong
