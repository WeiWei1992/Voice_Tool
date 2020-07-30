#-*- coding:utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import chardet
import shutil
import pandas as pd
import codecs
import unicodedata

import logging
import logging.config
CON_LOG='config\\log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()

# oldfile:UTF8文件的路径
# newfile:要保存的ANSI文件的路径
def convertUTF8ToANSI(oldfile, newfile):
    print("开始转化日志编码格式，utf-8转换为anis")
    #打开UTF8文本文件
    try:
        f = codecs.open(oldfile, 'r', 'utf')
        utfstr = f.read()
        f.close()

        # 把UTF8字符串转码成ANSI字符串
        outansestr = utfstr.encode('mbcs')

        # 使用二进制格式保存转码后的文本
        f = open(newfile, 'wb')
        f.write(outansestr)
        f.close()
    except:
        return False
    else:
        return True

def get_txt_encod_model(filepath):
    f=open(filepath,'rb')
    data=f.read()
    res=chardet.detect(data)
    print(filepath+"：编码格式： ",res)
    print(res['encoding'])  # 取得文本格式
    geshi = res['encoding']
    f.close()
    print(geshi)
    return geshi

    #return res

def rb_to_utf(in_file_path,out_file_path):
    with open(in_file_path,'rb') as f:
        lines=f.readlines()
        for line in lines:
            line=line.decode('utf-8','ignore')
            with open(out_file_path,'a',encoding='utf-8') as newfile:
                newfile.write(line)

if __name__=="__main__":

    with open('result_1.txt',encoding="utf-8") as f:
        lines=f.readlines()
        for line in lines:
            print(line)

    # mydata_txt=pd.read_csv("uai_log_conver_error.txt",sep='\n')
    # print(mydata_txt)
