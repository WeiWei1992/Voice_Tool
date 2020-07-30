#播放语音文件
import pyaudio
import wave
import time
import os
from datetime import datetime
import re

import logging
import logging.config
CON_LOG='config\\log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

def get_txt_line_tmp(filepath=None):
    with open(filepath,encoding='utf-8') as f:
        mytxt=f.readline()
        mytxt=mytxt.strip()  #去掉空格
    if mytxt[0] == '﻿':
        #print('第一个位置是空')
        logging.info("第一个位置是空,去掉前面的空格在比较")
        mytxt = mytxt[1:]
    real_str=mytxt
    logging.info("读取到的数据是:"+str(real_str))
    return real_str


def get_txt_line(filepath=None):
    #默认是读取设备id号，因为如果传递参数，就读取设备id
    real_str=''
    print(os.getcwd())
    if filepath==None:
        filepath=os.getcwd()+'/config/device.txt'
        res=os.path.exists(filepath)
        if res==True:
            logging.info("发现了文件:"+filepath)
            try:
                with open(filepath,encoding='utf-8') as f:
                    real_str = f.readline()
            except:
                logging.error("读取设备id出现错误")
        else:
            real_str=''
    else:
        real_str=get_txt_line_tmp(filepath)
        logging.info("读取到的数据是:"+str(real_str))
    return real_str


if __name__=="__main__":
    mytxt=get_txt_line()
    if mytxt=='':
        print("mytxt is 空")

