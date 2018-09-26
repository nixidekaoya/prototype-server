#!/usr/bin/env python
import threading
import json
import rospy
import darknet
import cv2
import time
import numpy as np
from ctypes import *
from cv_bridge import CvBridge
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage


class Recognizer(object):
    def __init__(self):
        self.file_path = __file__.replace("image_recognition_node_yolo.py","")
        self.object_like_path = self.file_path + "log/object/like/"
        self.object_dislike_path = self.file_path + "log/object/dislike/"
        self.object_neutral_path = self.file_path + "log/object/neutral/"
        self.object_person_path = self.file_path + "log/object/person/"
        self.template_path = self.file_path + "log/template/"
        setting_file = open(self.file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.width = int(self.settings["width"])
        self.height = int(self.settings["height"])
        self.bias_pixels = int(self.settings["bias pixels"])
        self.cvbr = CvBridge()
        #self.servo_move_pub = rospy.Publisher('servo_calibration',String, queue_size = 2)
        #self.speak_out_pub = rospy.Publisher('speak_text',String, queue_size = 10)
        self.recognize_result_pub = rospy.Publisher('recognize_result',String , queue_size = 5)
        self.recognize_start_pub = rospy.Publisher('image_send_save',String , queue_size = 1)
        self.template_pub = rospy.Publisher('template_image',CompressedImage,queue_size = 1)
        self.face_cascade = cv2.CascadeClassifier(self.file_path+'haarcascades/'+'haarcascade_profileface.xml')
        self.start_flag = False
        self.net = darknet.load_net(self.file_path+"yolov3.cfg" , self.file_path+"yolov3.weights" , 0)
        self.meta = darknet.load_meta(self.file_path + "coco.data")
        self.recognize_flag = True
        self.Negative = 1
        self.Positive = 2
        self.Neutral = 3
        self.Person = 4
        self.No_response = 0
        self.object_name = ""
        self.object_image = ""
        rospy.Subscriber('object_find',String,self.update_object)
        rospy.init_node('image_recognition_node')
        rospy.Subscriber("image_stream",CompressedImage,self.recognize_image)
        rospy.Subscriber("save_image_request",String,self.save_image)
        rospy.Subscriber("recognize_flag",String,self.toggle_recognize_flag)
        #rospy.Subscriber("recognize_start",String ,self.switch_flag)

    def update_object(self,recv_data):
        if recv_data.data == "clear":
            self.object_name = ""
        else:
            self.object_name = recv_data.data



    def toggle_recognize_flag(self,recv_data):
        if recv_data.data == "On":
            self.recognize_flag = True
        elif recv_data.data == "Off":
            self.recognize_flag = False
        else:
            dummy = 0

    def save_image(self,recv_data):
        now = time.localtime()
        time_save_buff = str(now.tm_year) + "_" + str(now.tm_mon) + "_" + str(now.tm_mday) + "_" + str(now.tm_hour) + "_" + str(now.tm_min) + "_" + str(now.tm_sec)
        dic_buff = json.loads(recv_data.data)
        #print(dic_buff)
        print(str(dic_buff))
        if dic_buff["Type"] == self.Negative:
            save_path = self.object_dislike_path + time_save_buff + "_dislike_" + dic_buff["Object"] + ".jpg"
            cv2.imwrite(save_path,self.object_image)
        elif dic_buff["Type"] == self.Positive:
            save_path = self.object_like_path + time_save_buff + "_like_" + dic_buff["Object"] + ".jpg"
            cv2.imwrite(save_path,self.object_image)
        elif dic_buff["Type"] == self.Neutral:
            save_path = self.object_neutral_path + time_save_buff + "_neutral_" + dic_buff["Object"] + ".jpg"
            cv2.imwrite(save_path,self.object_image)
        elif dic_buff["Type"] == self.Person:
            save_path = self.object_person_path + time_save_buff +"_" + dic_buff["Object"] + ".jpg"
            cv2.imwrite(save_path,self.object_image)
        else:
            dummy = 0

    def object_color(self,im,x_center,y_center):
        blue = im[y_center - 1,x_center - 1,0]
        green = im[y_center - 1,x_center - 1,1]
        red = im[y_center - 1,x_center - 1,2]
        blue = np.median(blue)
        green = np.median(green)
        red = np.median(red)
        color = np.uint8([[[blue,green,red]]])
        #print(color)
        hsv = cv2.cvtColor(color,cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)
        color = ""
        if v < 46:
            color = "black"
        elif v >= 221 and s <= 30:
            color = "white"
        elif v <= 220 and s < 43:
            color = "gray"
        else:
            if h <= 10:
                color = "red"
            elif h <= 25:
                color = "orange"
            elif h <= 34:
                color = "yellow"
            elif h <= 77:
                color = "green"
            elif h <= 99:
                color = "cyan"
            elif h <= 124:
                color = "blue"
            elif h <= 155:
                color = "purple"
            else:
                color = "black"
        return color








    def recognize_image(self,received_image):
        clock1 = time.time()
        if self.recognize_flag:
            #print("image received!")
            self.im1 = self.cvbr.compressed_imgmsg_to_cv2(received_image)
            #print(self.im1)
            #gray = cv2.cvtColor(self.im1, cv2.COLOR_BGR2GRAY)
            #faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            #for (x,y,w,h) in faces:
            #    dic_buff = {}
            #    dic_buff["name"] = "person"
            #    dic_buff["x center"] = int(x + w/2)
            #    dic_buff["y center"] = int(y + h/2)
            #    send_buff = json.dumps(dic_buff)
            #    print(send_buff)
            #    self.recognize_result_pub.publish(send_buff)
            #print(result)
            result = darknet.detect2(net = self.net , meta = self.meta, image = self.im1 , thresh =.7)
            for reco_result in result:
                dic_buff = {}
                name = reco_result[0]
                probs = reco_result[1]
                coords = reco_result[2]
                x_center = coords[0]
                y_center = coords[1]
                #print(x_center)
                #print(y_center)
                color = self.object_color(self.im1,x_center,y_center)

                dic_buff["name"] = name
                dic_buff["x center"] = x_center
                dic_buff["y center"] = y_center
                dic_buff["width"] = int(coords[2])
                dic_buff["height"] = int(coords[3])
                if int(dic_buff["width"]) > 312:
                    if int(dic_buff["height"]) > 312:
                        continue
                lu_x = x_center - dic_buff["width"]/2
                lu_y = y_center - dic_buff["height"]/2
                rd_x = x_center + dic_buff["width"]/2
                rd_y = y_center + dic_buff["height"]/2
                if lu_x < 0:
                    lu_x = 0
                if lu_y < 0:
                    lu_y = 0
                if rd_x > (self.width - 1):
                    rd_x = self.width - 1
                if rd_y > (self.height - 1):
                    rd_y = self.height - 1
                template = self.im1[lu_y:rd_y,lu_x:rd_x]
                save_path = self.template_path + name + ".jpg"
                cv2.imwrite(save_path,template)
                if self.object_name == name:
                    self.object_image = self.im1
                    cimg = self.cvbr.cv2_to_compressed_imgmsg(template,"jpeg")
                    self.template_pub.publish(cimg)

                print("object:" + name + ",color:" + color)
                dic_buff["prob"] = probs
                dic_buff["color"] = color
                send_buff = json.dumps(dic_buff)

                self.recognize_result_pub.publish(send_buff)
            clock2 = time.time()
            #print(clock2 - clock1)




def image_run():
    rospy.spin()



if __name__ == '__main__':
    recognize = Recognizer()

    try:
        image_run()
    except rospy.ROSInterruptException:
        pass
