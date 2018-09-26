#!/usr/bin/env python
import rospy
import time
import json
import speech_recognition as sr
from std_msgs.msg import String
from audio_common_msgs.msg import AudioData



class SpeechRecognizer(object):
    def __init__(self):
        self.file_path = __file__.replace("speech_recognition_node.py","")
        self.wav_file_path = self.file_path + "/log/speech/"
        self.microsoft_keys = "def4789dde804b599cd8976b96838a84"
        rospy.init_node("speech_recognition_node")
        rospy.Subscriber('audio_data',AudioData, self.recognize)
        self.sr_pub = rospy.Publisher('sr_result',String,queue_size = 1)
        self.r = sr.Recognizer()
        self.r.energy_threshold = 1500
        self.r.dynamic_energy_threshold = False
        self.r.sampling_rate  = 16000
        self.r.chunk_size = 1024
        self.r.pause_threshold = 0.8

    def recognize(self,ad_msg):
        result = ""
        now = time.localtime()

        time_save_buff = str(now.tm_year) + "_" + str(now.tm_mon) + "_" + str(now.tm_mday) + "_" + str(now.tm_hour) + "_" + str(now.tm_min) + "_" + str(now.tm_sec)
        save_path = self.wav_file_path + time_save_buff + ".wav"
        #print("Received wav file!")
        with open(save_path,"wb") as f:
            f.write(ad_msg.data)
        with sr.AudioFile(save_path) as source:
            audio = self.r.record(source)
        #os.system("aplay " + self.wav_file)
        #print("Start recognization!")
        try:
            result = self.r.recognize_bing(audio_data = audio, key = self.microsoft_keys , language = "en-US")
        except:
            try:
                result = self.r.recognize_google(audio_data = audio,language = "en-US")
            except:
                print("You said nothing!")

        if result:
            #print(result)
            result = result.lower()
            print(result)
            self.sr_pub.publish(result)


def speech_recognition_offline():
    speechrecognizer = SpeechRecognizer()
    rospy.spin()

if __name__ == '__main__':
    speech_recognition_offline()
