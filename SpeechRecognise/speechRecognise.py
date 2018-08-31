"""
实现了语音识别功能，识别语音转换成文字
"""

# -*- coding: utf-8 -*-
import json
import logging

try:
    from io import BytesIO as StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
from .WaveOperate.WaveFilter import *
from .BaiduSpeech.SpeechRecognizer import *
import redis

r = redis.Redis(host="127.0.0.1")

def push_recognize_data(err_no, result):
    r.publish("voice", json.dumps({"type":"voice", "data": result[0]}, ensure_ascii=False))
    print("push data to redis")
    logging.info("recognize data: " + result[0])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # baidu_oauth_conf = 'BaiduSpeech./BaiduOAuth.ini'
    api_key, secret_key = 'm0lwCtK4VVMmhFQFCF4ZpnFD','ia7oc1UQkrmWofC0Qv05ftOjdqUGv1ao'
    access_token = get_baidu_token_url(api_key, secret_key)
    # save_baidu_token_config(baidu_oauth_conf, access_token)
    # access_token = get_baidu_token_config(baidu_oauth_conf)
    sonic_conf = {
        'channels':1,
        'sample_width':2,
        'sample_frequency':16000,
        'sample_length':2048
    }
    sonic_conf = Sonic(**sonic_conf)
    bandpass_filter = butter_bandpass(150, 2000, sonic_conf.sample_frequency)
    record_conf = {
        'gate_value':700,
        'series_min_count':30,
        'block_min_count':8,
        'speech_filter':bandpass_filter
    }
    record_conf = RecordConf(**record_conf)
    logging.warning("speech recognition record start.")
    speech_recognizer = BaiduSpeechRecognizer(access_token, sonic_conf, record_conf)

    # for err_no, result in speech_recognizer.speech_recognition():
    #     print(err_no, result)

    # speech_recognizer.wav_file_recognize_async('WaveOperate/RecordExample.wav', print, print)
    # speech_recognizer.wav_file_recognize_async('WaveOperate/RecordFilteredExample.wav', print, print)

    speech_recognizer.speech_recognize_async(push_recognize_data, print)
















