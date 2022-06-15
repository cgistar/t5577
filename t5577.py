#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def calc(cardno):
    """
    计算t5577卡号
    params: cardno: str: 10位十六进制
    """
    if len(cardno) != 10:
        print("卡号不合法，请重新输入")
        return
    cardno_bin = "{:0>40b}".format(int(cardno, 16))
    # ABA码由ID代码转换为10进制所得
    aba = "{:0>10}".format(int(cardno[2:], 16))
    # wiegand26码由ID代码倒数5、6位和后4位分别换算成10进制组成
    wiegand26 = "{:0>3}, {:0>5}".format(int(cardno[-6:-4], 16), int(cardno[-4:], 16))

    # 将卡号转为二进制，10位卡号共10组数据
    bin_group = [cardno_bin[j:j + 4] for j in range(0, len(cardno_bin), 4)]
    # 每组数据中增加一位偶校验（每组二进制中1的个数为偶数个）
    bin_group = [f"{x}{x.count('1') % 2}" for x in bin_group]
    # 在进行数据校验的同时，确保了不会出现连续9个1与传输开始标志冲突。PC0~PC3位为列校验位，S0位停止位。
    odd_parity = [str("".join([k[i] for k in bin_group]).count("1") % 2) for i in range(4)]
    odd_parity.append("0")
    # EM4100卡与RFID读卡器的交互过程中，连续9个1表示一次传输的开始
    bin_data = "{:1>9}{}{}".format(1, "".join(bin_group), "".join(odd_parity))
    # 将所有传输数据转为十六进制就得到t5577卡数据
    block_data = "{:X}".format(int(bin_data, 2))

    # 组织打印结果
    out_strs = []
    out_strs.append("计算数据结果:\n行校验:    {} 列校验: {}".format(", ".join(bin_group), "".join(odd_parity)))
    out_strs.append(f"交互数据:  {bin_data}")
    out_strs.append(f"EM410x ID: {cardno.upper()}\nABA:       {aba}\nwiegand:   {wiegand26}\n")
    out_strs.append(f"Block0: 00148040\nBlock1: {block_data[:8]}\nBlock2: {block_data[8:]}")
    out_strs.append(f"Proxmark3写卡指令: \nlf t55xx write b 0 d 00148040\nlf t55xx write b 1 d {block_data[:8]}\nlf t55xx write b 2 d {block_data[8:]}\nlf t55xx detect")
    print("\n".join(out_strs))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        calc(sys.argv[1])
    else:
        print(f"用法：{sys.argv[0]} 06008148dd")
        sys.exit(0)
