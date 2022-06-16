#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


def calc(cardno):
    """
    计算t5577卡号
    params: cardno: str: 10位十六进制
    """
    if len(cardno) != 10:
        print("卡号不合法，请重新输入")
        return
    bin_cardno = "{:0>40b}".format(int(cardno, 16))
    # ABA码由ID代码转换为10进制所得
    aba = "{:0>10}".format(int(cardno[2:], 16))
    # wiegand26码由ID代码倒数5、6位和后4位分别换算成10进制组成
    wiegand26 = "{:0>3}, {:0>5}".format(int(cardno[-6:-4], 16), int(cardno[-4:], 16))

    # EM4100卡与RFID读卡器的交互过程中，连续9个1表示一次传输的开始
    bin_data = ["{:1>9}".format(1)]
    odd_paritys = ["0"] * 5
    # 将卡号转为二进制，10位卡号共10组数据
    for i in range(0, len(bin_cardno), 4):
        data = [bin_cardno[i : i + 4]]
        data.append(str(data[0].count("1") % 2))
        bin_data.append("".join(data))
        for j in range(4):
            odd_paritys[j] += data[0][j]
    for j in range(4):
        odd_paritys[j] = str(odd_paritys[j].count("1") % 2)
    bin_data.append("".join(odd_paritys))

    # 将所有传输数据转为十六进制就得到t5577卡数据
    block_data = "00148040{:X}".format(int("".join(bin_data), 2))
    block_datas = [block_data[x * 8 : (x + 1) * 8] for x in range(3)]

    # 组织打印结果
    bit_str = "9 header bits:  {0}\n8 customer ID:  {1} {2} \n32 Data Bits:   {3} {4} {5} {6} {7} {8} {9} {10}\nParity bits:    {11}"
    out_strs = []
    out_strs.append("EM410x ID: {}\nABA:       {}\nwiegand:   {}\n".format(cardno.upper(), aba, wiegand26))
    out_strs.append(bit_str.format(*bin_data))
    out_strs.append("Block0: {0}\nBlock1: {1}\nBlock2: {2}\n".format(*block_datas))
    out_strs.append("Proxmark3 run command:")
    for idx, value in enumerate(block_datas):
        out_strs.append("lf t55xx write -b {} -d {}".format(idx, value))
    out_strs.append("lf t55xx detect")
    print("\n".join(out_strs))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        calc(sys.argv[1])
    else:
        print("Usage: python {} 06008148dd".format(os.path.basename(sys.argv[0])))
        sys.exit(0)
