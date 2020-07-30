# -*- coding:utf-8 -*-
import os
import time
from datetime import datetime
import re
import pyaudio
import wave
#from Audio_Accuracy.conver_encod import convertUTF8ToANSI
from conver_encod import convertUTF8ToANSI
#from Audio_Accuracy.operate_excel import creat_excel, write_excel
from operate_excel import creat_excel,write_excel
#from Audio_Accuracy.conver_encod import rb_to_utf
from conver_encod import rb_to_utf
#from Audio_Accuracy.send_email import my_send
from send_email import my_send
# adb拉取日志到指定路径下
# os.system('adb devices')
# os.system('adb pull /tmp/uai_log.txt D:\download')
# print("拉去文件结束")
#from Audio_Accuracy.file import get_txt_line
from file import get_txt_line

import logging
import logging.config

CON_LOG = 'config\\log.conf'
logging.config.fileConfig(CON_LOG)
logging = logging.getLogger()


def load_log(device_id=None, filepath=None, filter_log_path=None):
    dt = datetime.now()
    now_time = dt.strftime('%Y_%m_%d_%H_%M_%S')  # 得用下划线，用： 号无法截图保存
    # father_path = os.path.abspath(os.path.dirname(os.getcwd()))
    my_path = os.path.abspath(os.getcwd())
    if filepath == None:
        filepath = my_path + '/Logs/original_log/uai_log_%s' % (now_time)
    if filter_log_path == None:
        filter_log_path = my_path + '/Logs/result_log/filter_uai_log_%s.txt' % (now_time)

    # device_id=get_txt_line()
    if device_id == '':
        adbshell = 'adb pull /tmp/uai_log.txt ' + filepath
    else:
        adbshell = 'adb -s ' + str(device_id) + ' pull /tmp/uai_log.txt ' + filepath
    # print(adbshell)
    logging.info("adb shell 命令：" + adbshell)
    result = os.path.exists(filepath)
    if result:  # 如果该文件夹存在
        # adbshell='adb shell /tmp/uai_log.txt '+filepath
        os.system(adbshell)
    else:  # 如果不存在，先新建
        os.mkdir(filepath)
        os.system(adbshell)
    file_path_1 = filepath + '\\uai_log.txt'
    file_path_2 = filepath + '\\uai_log_convert.txt'
    # res=convertUTF8ToANSI(file_path_1,file_path_2)
    # if res==False:
    #     print("txt文件转码错误，不进行转码了")
    #     file_path_2=file_path_1
    time.sleep(3)
    return file_path_1, filter_log_path


def filter_time(line):
    # print("检查是否是时间")
    # print(line)
    # print("type(line):", type(line))
    line = str(line)
    # print(line)
    # print("这里检查是否是时间行，是的话就返回True，否则返回False")
    # print("type(line):",type(line))
    '''
    使用正则，查看是否是时间行
    :param line: 读取的字符串行
    :return: False or True
    '''
    # 正式使用时，该正则要放到外面，是个全局的，这样就只初始化一次了就
    # pattern = re.compile(r'\d{4}(\-\|\/|.)(\s)\d{1,2}\1\d{1,2}')  # 时间的正则,\s表示空格
    pattern = re.compile(r'b\'\d{4}(\-\|\/|.)(\s)\d{1,2}\1\d{1,2}')  # 时间的正则,\s表示空格
    line = line.strip('\n')  # 去掉换行符
    # line=line.strip('\n')
    time_result = pattern.match(line)
    # pattern.search:可以在字符串任何位置匹问配
    # pattern.match:是从字符百串开头进行度匹配
    if time_result is None:
        # print("时间行没有匹配上")
        return False
    else:
        # print("时间行匹配上了")
        return True


def transform_log_time(line):
    # 转换中的时间，转换为毫秒级时间戳
    # 输入参数是日志中的时间字符串
    # print("输入要检测的时间行： ",line)
    # print("输入的时间行：",line)
    line = str(line)
    # 这几行是因为读入是以二进制读入的，需要特殊处理一下
    line = line.replace('\'', '')
    line = line.replace('b', '')
    line = line.strip('\n')
    line = line.replace('\\', '')
    line = line.replace('n', '')

    # print("处理后的时间行")
    # print("转换日志时间戳: ",line)
    try:
        datetime_obj = datetime.strptime(line, "%Y- %m-%d %H:%M:%S.%f")
        obj_stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    except:
        # print("日志中输入的时间不对，请检查")
        logging.error("日志中输入的时间不对，请检查")
        return None
    else:
        # print("转换成功")
        return obj_stamp


def get_now_time_millisecond():
    # 获取当前时间的毫秒级时间戳
    t = time.time()
    my_time = int(round(t * 1000))  # 毫秒级时间戳
    return my_time


def save_txt(line, pathfile=None):
    # print("保存txt: ",line,filter_log_path)
    if pathfile == None:
        try:
            father_path = os.path.abspath(os.path.dirname(os.getcwd()))
            filepath = father_path + '/Logs/result_log/filter_uai_log.txt'
            # print('保存的文件路径：',filepath)
            logging.info('保存的文件路径：' + filepath)
        except:
            # print("获取保存txt文件的路径失败")
            logging.info("获取保存txt文件的路径失败")
            return None
    try:
        # print("保存路径...",pathfile)
        with open(pathfile, 'a', encoding='utf-8') as f:
            f.write(line)
            f.write('\n')
    except:
        # print("文件写入错误")
        logging.error("文件写入错误")
        return None
    else:
        # print("写入文件成功")
        # print(pathfile)
        return pathfile


def get_log_time_after(filepath, filter_log_path, mytime=None):
    '''
    提取在某个时间戳之后的日志
    :param filepath: 日志文件路径
    :param mytime: 毫米级时间戳，该时间之后的日志会被提取,在播放音频之前就要计算出时间戳
    :return:
    '''
    upline = ''
    log = []
    lineNumbers = 0
    if mytime == None:
        # print("没有输入日志截取的时间戳")
        logging.error("没有输入日志截取的时间戳")
        return None
    is_time_up = False
    number_kongge = 0
    with open(filepath, 'rb') as f:
        # is_time_up=False
        while True:
            try:
                line = f.readline()
                if not line:
                    # print(upline)
                    # print(line)
                    logging.info(line)
                    # print("结束了")
                    logging.info("日志读取结束了")
                    break
            except UnicodeDecodeError:
                # print("这里出现了编码错误，出现编码错误的行是： ", lineNumbers)
                # print("上一行是：",upline)
                # print("这一行是：",line)
                logging.error("这里出现了编码错误，出现编码错误的行是： " + str(lineNumbers))
                logging.error("上一行是： " + str(upline))
                continue
            else:
                # print(line)
                upline = line
                lineNumbers = lineNumbers + 1
                # print('lineNumbers:', lineNumbers)
                # if 'recogniationText' in str(line):
                #     print("找到了 ===================")
                if is_time_up == True:  # 如果找到了时间节点，就直接保存
                    if 'recogniationText' in str(line):
                        # print("找到了 recogniationText===================")
                        logging.info("找到了 recogniationText===================")
                    log.append(line)
                    # line=str(line)
                    # 达到时间节点之后，转换一下格式进行保存
                    line = line.decode('utf-8', 'ignore')
                    save_txt(line, filter_log_path)

                if is_time_up == False:  # 如果还没有找到时间节点，才继续查找，找到了就不要在执行了
                    is_time_line = filter_time(line)
                    if is_time_line:
                        # 如果该行是时间行，转换成毫秒级的时间戳
                        log_tmp_time = transform_log_time(line)
                        # print('log_tmp_time:', log_tmp_time)
                        # print("mytime: ", mytime)
                        if log_tmp_time >= mytime:
                            is_time_up = True
                            # print("找到了时间隔离点")
                            # print(line)
                            # print(lineNumbers)
                            # print("==================")
                        else:
                            continue
    # print('lineNumbers: ', lineNumbers)
    logging.info("总行数 lineNumbers: " + str(lineNumbers))
    time.sleep(10)
    return log


'''
    with open(filepath,encoding='gbk') as f:  #使用gbk，使用utf-8会概率性报错，看下还会出错吗
        # try:
        #     lines=f.readlines()  #会读取到换行符
        #     #lines.decode("utf8","ignore")
        # except:
        #     print('字符串解析错误')
        #     print("字符串解析错误字符串解析错误字符串解析错误字符串解析错误字符串解析错误")
        #     lines=f.readlines()
        #     #raise ('字符串解析错误')

        lines=f.readlines()
        for line in lines:
            lineNumbers=lineNumbers+1
            print('lineNumbers:',lineNumbers)
            #print("xxxxxxxxxxx")
            is_time_line=filter_time(line)
            if is_time_line:
                #如果该行是时间行，转换成毫米级时间戳
                log_tmp_time=transform_log_time(line)
                print('log_tmp_time:',log_tmp_time)
                print("mytime: ",mytime)
                if log_tmp_time >= mytime:  #该行日志的时间大于给定的时间，是本次需要的日志，截取
                    print(lineNumbers)
                    print("==================")
                    break
            else:
                continue
    '''

'''
    is_time_up = False
    number_kongge=0
    with open(filepath,'r') as f:
        #is_time_up=False
        while True:
            try:
                line=f.readline()
                #number_kongge=number_kongge+1
                #if number_kongge ==10:
                    #print('number_kongge:',number_kongge)
                    #break
                if not line:
                    #print(upline)
                    print("结束了")
                    break

            except UnicodeDecodeError:
                print("这里出现了编码错误，出现编码错误的行是： ",lineNumbers)
                #print("上一行是：",upline)
                continue
            else:
                #print(line)
                upline=line
                lineNumbers = lineNumbers + 1
                #print('lineNumbers:', lineNumbers)
                if 'recogniationText' in str(line):
                    print("找到了 ===================")
                if is_time_up==True:   #如果找到了时间节点，就直接保存
                    log.append(line)
                    save_txt(line, filter_log_path)

                if is_time_up==False:  #如果还没有找到时间节点，才继续查找，找到了就不要在执行了

                    is_time_line = filter_time(line)
                    if is_time_line:
                        #如果该行是时间行，转换成毫秒级的时间戳
                        log_tmp_time = transform_log_time(line)
                        # print('log_tmp_time:', log_tmp_time)
                        # print("mytime: ", mytime)
                        if log_tmp_time>mytime:
                            is_time_up=True
                            #print("找到了时间隔离点")
                            #print(line)
                            #print(lineNumbers)
                            #print("==================")
                        else:
                            continue

    print('lineNumbers: ',lineNumbers)
    time.sleep(10)
    return log
'''

''' 
    #把时间挫之后的数据进行保存
    with open(filepath,encoding='gbk') as f:
        lines=f.readlines()
        number=0
        for line in lines:
            number=number+1
            if number>lineNumbers:
                log.append(line)
                save_txt(line,filter_log_path)
            else:
                continue
    return log
'''

'''
def get_log_time_after_1(filepath,filter_log_path,mytime=None):

    #提取在某个时间戳之后的日志
    #:param filepath: 日志文件路径
    #:param mytime: 毫米级时间戳，该时间之后的日志会被提取,在播放音频之前就要计算出时间戳
    #:return:

    is_time_up = False
    log=[]
    lineNumbers=0
    if mytime==None:
        print("没有输入日志截取的时间戳")
        return None
    with open(filepath,'rb') as f:  #使用gbk，使用utf-8会概率性报错，看下还会出错吗
        try:
            lines=f.readlines()  #会读取到换行符
            #lines.decode("utf8","ignore")
        except:
            print('字符串解析错误')
            print("字符串解析错误字符串解析错误字符串解析错误字符串解析错误字符串解析错误")
            #lines=f.readlines()
            #raise ('字符串解析错误')
        else:
            for line in lines:
                lineNumbers=lineNumbers+1
                #print(lineNumbers)
                #print("xxxxxxxxxxx")
                is_time_line=filter_time(line)
                if is_time_up==False:
                    is_time_line = filter_time(line)
                    if is_time_line:
                        #如果该行是时间行，转换成毫米级时间戳
                        log_tmp_time=transform_log_time(line)
                        print('log_tmp_time:',log_tmp_time)
                        print("mytime: ",mytime)
                        if log_tmp_time >= mytime:  #该行日志的时间大于给定的时间，是本次需要的日志，截取
                            print(lineNumbers)
                            is_time_up=True
                            print("=======找到大于给定的时间了===========")
                            #break
                    else:
                        continue
                else:
                    line = line.decode('utf-8', 'ignore')
                    with open(filter_log_path, 'a', encoding='utf-8') as newfile:
                        newfile.write(line)
                        print("开始写入filter_log_path:",filter_log_path)

    # #把时间挫之后的数据进行保存
    # with open(filepath,'r') as f:
    #     lines=f.readlines()
    #     number=0
    #     for line in lines:
    #         number=number+1
    #         if number>lineNumbers:
    #             log.append(line)
    #             save_txt(line,filter_log_path)
    #         else:
    #             continue
    # return log
'''


def play_wav(filepath):
    # 播放wav文件
    chunk = 1024
    # 从目录中读取语音
    wf = wave.open(filepath, 'rb')
    data = wf.readframes(chunk)
    # 创建播放器
    p = pyaudio.PyAudio()

    # 获得语音文件的各个参数
    FORMAT = p.get_format_from_width(wf.getsampwidth())
    CHANELS = wf.getnchannels()
    RATE = wf.getframerate()
    # print('FORMAF:{} \nCHANELS: {}\nRATE: {}'.format(FORMAT,CHANELS,RATE))
    str_tmp = 'FORMAF:{} \nCHANELS:{}\nRATE:{}'.format(FORMAT, CHANELS, RATE)
    logging.info("播放的系统参数\n" + str_tmp)
    # 打开音频流，output=True表示音频输出
    stream = p.open(format=FORMAT,
                    channels=CHANELS,
                    rate=RATE,
                    frames_per_buffer=chunk,
                    output=True)
    # while data !='':
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
    # print("播放结束")
    logging.info("播放结束")


def get_file_all(xiaoyou_path=None, jiaohu_path=None):
    # 返回的是唤醒词、交互词、交互词的txt全路径的列表
    xiaoyou_path_wav = []
    jiaohu_path_wav = []
    jiaohu_path_txt = []
    if xiaoyou_path == None:
        my_path = os.path.abspath(os.getcwd())
        xiaoyou_path = my_path + '/yuyin/xiaoyou/'
        logging.info("xiaoyou_path:" + xiaoyou_path)
        for i, j, k in os.walk(xiaoyou_path):
            # print('k:',k)
            for i in k:
                # print('iiiii',i)
                all_path = xiaoyou_path + i
                xiaoyou_path_wav.append(all_path)
                # print('all_path:',all_path)
    else:  # 为了GUI页面，使用GUI页面传入路径地址
        logging.info("xiaoyou_path:" + xiaoyou_path)
        for i, j, k in os.walk(xiaoyou_path):
            # print('k:',k)
            for i in k:
                # print('iiiii',i)
                all_path = xiaoyou_path + i
                xiaoyou_path_wav.append(all_path)
                # print('all_path:',all_path)

    if jiaohu_path == None:
        my_path = os.path.abspath(os.getcwd())
        jiaohu_path = my_path + '/yuyin/jiaohu/'
        for a, b, c in os.walk(jiaohu_path):
            # print('c:',c)
            for j in c:
                # print("xxxxxxxx")
                file = os.path.splitext(j)
                filename, type = file
                if type == '.txt':
                    jiaohu_path_txt_allpath = jiaohu_path + j
                    jiaohu_path_txt.append(jiaohu_path_txt_allpath)
                elif type == '.wav':
                    jiaohu_path_wav_allpath = jiaohu_path + j
                    jiaohu_path_wav.append(jiaohu_path_wav_allpath)
                else:
                    # print("有其他类型（非txt和wav格式）文件，请检查，暂且忽略")
                    logging.warning("有其他类型（非txt和wav格式）文件，请检查，暂且忽略")
                    continue
    else:  # GUI页面有传入的交互音频的路径
        for a, b, c in os.walk(jiaohu_path):
            # print('c:',c)
            for j in c:
                # print("xxxxxxxx")
                file = os.path.splitext(j)
                filename, type = file
                if type == '.txt':
                    jiaohu_path_txt_allpath = jiaohu_path + j
                    jiaohu_path_txt.append(jiaohu_path_txt_allpath)
                elif type == '.wav':
                    jiaohu_path_wav_allpath = jiaohu_path + j
                    jiaohu_path_wav.append(jiaohu_path_wav_allpath)
                else:
                    # print("有其他类型（非txt和wav格式）文件，请检查，暂且忽略")
                    logging.warning("有其他类型（非txt和wav格式）文件，请检查，暂且忽略")
                    continue

    if len(jiaohu_path_wav) != len(jiaohu_path_txt):
        # print("交互文件中语音和txt数量不一致，请检查")
        logging.error("交互文件中语音和txt数量不一致，请检查")
        return None

    # 处理一下啊唤醒词与交互词数量不一致的问题
    if len(xiaoyou_path_wav) > len(jiaohu_path_wav):
        logging.info("交互词数量少于唤醒词数量，处理一下")
        length = len(jiaohu_path_wav)
        # print("length:",length)
        xiaoyou_path_wav_new = xiaoyou_path_wav[:length]

    elif len(xiaoyou_path_wav) < len(jiaohu_path_wav):
        # 唤醒词少
        logging.info("唤醒词数量少于交互词数量，处理一下")
        xiaoyou_path_wav_new = []
        lenth1 = len(xiaoyou_path_wav)
        lenth2 = len(jiaohu_path_wav)
        lenth = lenth2 - lenth1
        logging.info("读入的唤醒词数量: " + str(lenth1))
        # print("lenth1",lenth1)
        # print("length2",lenth2)
        logging.info("读入的交互词数量: " + str(lenth2))

        zhengshu = lenth // lenth1
        # print("zhengshu: ",zhengshu)
        yushu = lenth % lenth1
        # print("yushu: ",yushu)
        if zhengshu >= 1:  # 欢迎词很少
            num = zhengshu + 1
            xiaoyou_path_wav_1 = xiaoyou_path_wav * num
            if yushu == 0:
                xiaoyou_path_wav_new = xiaoyou_path_wav_1
            else:
                xiaoyou_path_wav_new = xiaoyou_path_wav_1 + xiaoyou_path_wav[:yushu]
        else:
            xiaoyou_path_wav_new = xiaoyou_path_wav + xiaoyou_path_wav[:yushu]
        # print("=======xiaoyou_path_wav_new:=====",xiaoyou_path_wav_new)
    else:
        xiaoyou_path_wav_new = xiaoyou_path_wav

    # print("len(xiaoyou_path_wav_new)=",len(xiaoyou_path_wav_new))
    len_wake_new_num = len(xiaoyou_path_wav_new)
    logging.info("处理后的唤醒词数量:" + str(len_wake_new_num))

    # print("len(jiaohu_path_wav)=",len(jiaohu_path_wav))
    len_jiaohu_new_num = len(jiaohu_path_wav)
    logging.info("处理后交互词的数量：" + str(len_jiaohu_new_num))

    # print("xiaoyou_path_wav_new:",xiaoyou_path_wav_new)
    logging.info("唤醒词列表:")
    logging.info(xiaoyou_path_wav_new)
    # print('jiaohu_path_wav',jiaohu_path_wav)
    logging.info("交互词列表：")
    logging.info(jiaohu_path_wav)
    # print('jiaohu_path_txt',jiaohu_path_txt)
    logging.info("交互文本列表：")
    logging.info(jiaohu_path_txt)
    return xiaoyou_path_wav_new, jiaohu_path_wav, jiaohu_path_txt


def log_check(filepath, txt_path):
    '''
    需要返回的是：唤醒词是否识别到 True/False          is_wake
                唤醒词所在的行内容,没有唤醒返回''    wake_line
                识别是否成功   True/False           is_indenty
                识别成的字符串                       identy_str
                配置文件中读取的与语音词               real_str
    '''
    is_wake = False
    wake_line = ''
    is_indenty = False
    identy_str = ''
    real_str = ''
    nlp_str = ''
    # print("txt_path: ",txt_path)
    logging.info("txt_path: " + str(txt_path))

    # mytxt=get_txt_line(txt_path)
    with open(txt_path, encoding='utf-8') as f:
        mytxt = f.readline()
        mytxt = mytxt.strip()  # 去掉空格
        # mytxt = mytxt.strip('\n')
    # print('读取的配置文件的字符:',mytxt)
    # logging.info("读取的配置文件的字符："+str(mytxt))
    if mytxt[0] == '﻿':
        # print('第一个位置是空')
        logging.info("第一个位置是空,去掉前面的空格在比较")
        mytxt = mytxt[1:]
    real_str = mytxt
    logging.info("读取的配置文件的字符：" + str(mytxt))

    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = str(line)
            line = line.strip('\n')
            # 提取唤醒关键词
            pattern_wakeup = re.compile(r'.*?uaibot(.*?)\[app\]\[onWakeup\]\sapp\s\-\swakeup\:\sxiaoyouxiaoyou')
            matchObj_wakeup = re.match(pattern_wakeup, line)
            if matchObj_wakeup:
                # print("matchObj_wakeup.group: ",matchObj_wakeup.group())
                # print("matchObj_wakeup.group(1): ", matchObj_wakeup.group(1))
                # print("----------------------")
                # print(line)
                logging.info("正则匹配到了")
                logging.info("matchObj_wakeup.group:" + str(matchObj_wakeup.group()))
                logging.info("matchObj_wakeup.group(1): " + str(matchObj_wakeup.group(1)))
                logging.info("输出该行： " + str(line))
                is_wake = True
                wake_line = line

            # 提取识别文字和反馈文字的正则
            pattern = re.compile(
                r'.*uaibot.*?\[app\]\[onResult\]\sapp\s\-\sasr\s\-\sonResult.*?msg.*?tts\"\:\"(.*?)\"\,\"data\"\:\{\"asrResult\"\:\[\{\"recogniationText\"\:\"(.*?)\"\,\"confidence')
            matchObj = re.match(pattern, line)
            if matchObj:
                # print("matchObj.group() : ", matchObj.group())
                # print("matchObj.group(1) : ", matchObj.group(1))
                # print("matchObj.group(2) : ", matchObj.group(2))
                nlp_str = matchObj.group(1)
                identy_str = matchObj.group(2)
                # is_indenty=True
    # print("识别到的字符:",identy_str)
    logging.info("识别到的字符串: " + str(identy_str))
    if identy_str == mytxt:
        # print("识别成功")
        logging.info("识别成功")
        is_indenty = True
    # print("nlp返回结果： ",nlp_str)
    logging.info("nlp返回结果： " + str(nlp_str))
    return is_wake, wake_line, is_indenty, identy_str, real_str, nlp_str
    # 返回的参数分别是：唤醒词是否识别到、唤醒词所在的行、交互是否识别成功、交互识别成的字符、配置文件中读取到的字符


def main():
    # 创建excel文件
    excel_file = creat_excel()
    logging.info("创建excel文件，保存测试结果：" + str(excel_file))
    xiaoyou_path_wav_new, jiaohu_path_wav, jiaohu_path_txt = get_file_all()
    # print(jiaohu_path_wav)
    logging.info("文件预处理完毕,打印下处理后返回的结果")
    logging.info("xiaoyou_path_wav_new:")
    logging.info(xiaoyou_path_wav_new)
    logging.info("jiaohu_path_wav:")
    logging.info(jiaohu_path_wav)
    logging.info("jiaohu_path_txt:")
    logging.info(jiaohu_path_txt)
    # 获取当前时间的毫秒级时间戳，为了后续截取日志
    # now_millisecond_time = get_now_time_millisecond()
    # time.sleep(5)
    for i in range(len(jiaohu_path_wav)):
        # print(jiaohu_path_wav[i])
        now_millisecond_time = get_now_time_millisecond()
        time.sleep(5)

        # 播放唤醒语音
        logging.info("播放唤醒词： " + str(xiaoyou_path_wav_new[i]))
        play_wav(xiaoyou_path_wav_new[i])
        # 等待时间，需要根据经验设置等待时间
        time.sleep(3)
        # 播放交互语音
        logging.info("播放交互词： " + str(jiaohu_path_wav[i]))
        play_wav(jiaohu_path_wav[i])
        # 等待一会
        time.sleep(20)
        # 拉取日志
        logging.info("开始拉取日志....")
        file_path, filter_log_path = load_log()
        # print("=======log地址======")
        logging.info("====log地址====")
        # print('file_path',file_path)
        logging.info("file_path: " + str(file_path))
        # print('filter_log_path',filter_log_path)
        logging.info("filter_log_path: " + str(filter_log_path))
        time.sleep(20)
        get_log_time_after(file_path, filter_log_path, now_millisecond_time)

        time.sleep(3)

        is_wake, wake_line, is_indenty, identy_str, real_str, nlp_test = log_check(filter_log_path, jiaohu_path_txt[i])
        logging.info("结果写入excel中: " + str(excel_file))
        write_excel(excel_file, xiaoyou_path_wav_new[i], jiaohu_path_wav[i], jiaohu_path_txt[i],
                    file_path, filter_log_path, is_wake, wake_line, is_indenty, identy_str, real_str, nlp_test)
        time.sleep(20)
    # print("测试结束，发送邮件")
    logging.info("测试结束，发送邮件")
    msg_to = ['1508691067@qq.com']
    my_send(excel_file, msg_to)


def do_main(deviceid, email, wake_path, jiaohu_path, excel_path):
    excel_file = creat_excel(excel_path)
    logging.info("创建excel文件，保存测试结果：" + str(excel_file))
    xiaoyou_path_wav_new, jiaohu_path_wav, jiaohu_path_txt = get_file_all(wake_path, jiaohu_path)
    # print(jiaohu_path_wav)
    logging.info("文件预处理完毕,打印下处理后返回的结果")
    logging.info("xiaoyou_path_wav_new:")
    logging.info(xiaoyou_path_wav_new)
    logging.info("jiaohu_path_wav:")
    logging.info(jiaohu_path_wav)
    logging.info("jiaohu_path_txt:")
    logging.info(jiaohu_path_txt)

    for i in range(len(jiaohu_path_wav)):
        # print(jiaohu_path_wav[i])
        now_millisecond_time = get_now_time_millisecond()
        time.sleep(5)

        # 播放唤醒语音
        logging.info("播放唤醒词： " + str(xiaoyou_path_wav_new[i]))
        play_wav(xiaoyou_path_wav_new[i])
        # 等待时间，需要根据经验设置等待时间
        time.sleep(3)
        # 播放交互语音
        logging.info("播放交互词： " + str(jiaohu_path_wav[i]))
        play_wav(jiaohu_path_wav[i])
        # 等待一会
        time.sleep(20)
        # 拉取日志
        logging.info("开始拉取日志....")
        file_path, filter_log_path = load_log()
        # print("=======log地址======")
        logging.info("====log地址====")
        # print('file_path',file_path)
        logging.info("file_path: " + str(file_path))
        # print('filter_log_path',filter_log_path)
        logging.info("filter_log_path: " + str(filter_log_path))
        time.sleep(20)
        get_log_time_after(file_path, filter_log_path, now_millisecond_time)

        time.sleep(3)

        is_wake, wake_line, is_indenty, identy_str, real_str, nlp_test = log_check(filter_log_path, jiaohu_path_txt[i])
        logging.info("结果写入excel中: " + str(excel_file))
        write_excel(excel_file, xiaoyou_path_wav_new[i], jiaohu_path_wav[i], jiaohu_path_txt[i],
                    file_path, filter_log_path, is_wake, wake_line, is_indenty, identy_str, real_str, nlp_test)
        time.sleep(20)
    # print("测试结束，发送邮件")
    logging.info("测试结束，发送邮件")
    # msg_to = ['1508691067@qq.com']
    # my_send(excel_file,msg_to)
    my_send(excel_file, email)


if __name__ == "__main__":
    # excel_path='D:\\download'
    deviceid = ''
    email = '1508691067@qq.com'
    wake_path = 'C:\\Users\\weiwei\\PycharmProjects\\test_appium\\Audio_Accuracy\\yuyin\\xiaoyou\\'
    jiaohu_path = 'C:\\Users\\weiwei\\PycharmProjects\\test_appium\\Audio_Accuracy\\yuyin\\jiaohu\\'
    excel_path = 'D:\\download'
    do_main(deviceid, email, wake_path, jiaohu_path, excel_path)

    # main()





