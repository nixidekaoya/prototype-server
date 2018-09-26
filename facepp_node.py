#!/usr/bin/python
import threading
import json
import rospy
import cv2
import time
import sys
import numpy as np
from cv_bridge import CvBridge
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from facepp import API, File



class FacePlusPlusThread(threading.Thread):
    def __init__(self,fpprecognizer):
        super(FacePlusPlusThread,self).__init__()
        self.recognizer = fpprecognizer

    def run(self):
        while True:
            if self.recognizer.start_flag == True:
                self.recognizer.start_flag = False
                print("start face++")
                clock1 = time.clock()
                ret = self.recognizer.facepp_api.search(outer_id = 'Ishiguro lab', image_file = File(self.recognizer.face_file_path))
                clock2 = time.clock()
                print(str(clock2 - clock1))
                try:
                    results = ret["results"][0]
                    if int(results["confidence"]) > 74:
                        print("The person is: " + results["user_id"])
                        self.recognizer.person_name = results["user_id"]
                        self.recognizer.person_find_clock = time.clock()
                        self.recognizer.speak_out_pub.publish("Hello! " + results["user_id"])
                        #print(self.recognizer.person_name)
                    else:
                        self.recognizer.speak_out_pub.publish("Hello! Who are you?" )
                except:
                    self.recognizer.speak_out_pub.publish("Hello!")




class FaceRecognizer(object):
    def __init__(self):
        self.file_path = __file__.replace("facepp_node.py","")
        self.face_file_path = self.file_path + "face.jpg"
        setting_file = open(self.file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.width = int(self.settings["width"])
        self.height = int(self.settings["height"])
        self.bias_pixels = int(self.settings["bias pixels"])
        self.cvbr = CvBridge()
        self.servo_move_pub = rospy.Publisher('servo_calibration',String, queue_size = 2)
        self.speak_out_pub = rospy.Publisher('speaker_text',String, queue_size = 10)
        self.face_cascade = cv2.CascadeClassifier(self.file_path + 'haarcascades/'+'haarcascade_profileface.xml')
        self.start_flag = False
        rospy.init_node('facepp_node')
        rospy.Subscriber("image_stream",CompressedImage,self.recognize_image)
        self.api_server_international = 'https://api-us.faceplusplus.com/facepp/v3/'
        self.key = '62b_10gNSQvOSNTTAihyzmNaG5zRY6iP'
        self.secret = 'kjyavIWFO5QfWPpUezbV-SpxjkjFKDwG'
        self.facepp_api = API(self.key , self.secret , srv = self.api_server_international)
        self.person_name = ""
        self.person_find_clock = 0



    def recognize_image(self,received_image):
        #clock1 = time.clock()
        if received_image.format == "jpeg":
            print("image received!")
            im1 = self.cvbr.compressed_imgmsg_to_cv2(received_image)
            gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 3)
            for (x,y,w,h) in faces:
                print("Face find")
                send_dic = {}
                x_center = int(x + w/2)
                y_center = int(y + w/2)
                send_dic["x center"] = x_center
                send_dic["y center"] = y_center
                #print(x_center)
                #print(y_center)
                send_buff = json.dumps(send_dic)
                self.servo_move_pub.publish(send_buff)
                if self.person_name == "":
                    cv2.imwrite(self.face_file_path , im1)
                    self.start_flag = True


                #if (x_center < (self.width/2 + self.bias_pixels)) and (x_center > (self.width/2 - self.bias_pixels)):
                #    if (y_center < (self.height/2 + self.bias_pixels)) and (y_center > (self.height/2 - self.bias_pixels)):
                #        self.speak_out_pub.publish("Hello")

            #if start_flag == True:
                #image_send_pub.publish("Ready")
            #clock2 = time.clock()
            #print(clock2 - clock1)





def facepp_run(recognizer):
    while not rospy.is_shutdown():
        clock = time.clock()
        if recognizer.person_name != "":
            if (clock - recognizer.person_find_clock) > 20:
                print("Clear person name")
                recognizer.person_name = ""



if __name__ == '__main__':
    fpprecognizer = FaceRecognizer()
    fppthread = FacePlusPlusThread(fpprecognizer)
    fppthread.start()
    print("facepp_node start!")

    try:
        facepp_run(fpprecognizer)
    except rospy.ROSInterruptException:
        pass
