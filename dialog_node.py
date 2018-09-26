#!/usr/bin/env python
import json
import rospy
import time
from std_msgs.msg import String


class Dialog_class(object):
    def __init__(self):
        self.file_path = __file__.replace("dialog_node.py","")
        setting_file = open(self.file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.objects = []
        object_file = open(self.file_path + "coco.names")
        for line in object_file.readlines():
            line = line.replace('\n','')
            #print(line)
            self.objects.append(line)
        object_file.close()
        #print(self.objects)
        self.width = int(self.settings["width"])
        self.height = int(self.settings["height"])
        self.bias_pixels = int(self.settings["bias pixels"])
        rospy.init_node('dialog_node')
        self.servo_move_pub = rospy.Publisher('servo_calibration',String, queue_size = 1)
        self.speak_out_pub = rospy.Publisher('speaker_json',String, queue_size = 1)
        self.save_image_pub = rospy.Publisher('save_image_request',String, queue_size = 1)
        self.recognize_flag_pub = rospy.Publisher('recognize_flag',String, queue_size = 1)
        self.servo_command_pub = rospy.Publisher('command_topic',String, queue_size = 1)
        self.camera_pub = rospy.Publisher('command_topic',String,queue_size = 1)
        self.template_clear_pub = rospy.Publisher('clear_template',String,queue_size = 1)
        self.object_find_pub = rospy.Publisher('object_find',String,queue_size = 1)
        self.camera_command = {"command":"send"}
        rospy.Subscriber('recognize_result',String,self.recognize_result)
        rospy.Subscriber('sr_result', String, self.sr_receive)
        self.person_find = False
        self.save_image_msg = {"Type":0,"Object":"None"}
        self.color = "black"
        self.res = {}
        self.speak_dic = {}
        self.clear_timer = 0
        self.person_timer = 0
        self.sr_recvive_flag = False
        self.question_flag = False
        self.response_counter = 0
        self.complete_list = []
        self.track_name = ""
        self.sr_res = []
        self.object_list = []
        self.x_center = 0
        self.y_center = 0
        self.response = 0
        self.question_list = ["which","one","color"]
        self.negative_list = ["no","don","dislike"]
        self.positive_list = ["yes","yea","i like","good","yeah"]
        self.Negative = 1
        self.Positive = 2
        self.Neutral = 3
        self.Person = 4
        self.No_response = 0
        self.find_counter = 0

    def ros_pub(self,publisher,json_buff):
        send_buff = json.dumps(json_buff)
        publisher.publish(send_buff)
        print(send_buff)

    def check_clear_list(self):
        if self.person_timer != 0:
            temp_time = time.time()
            if (temp_time - self.person_timer) >= 60:
                self.person_timer = 0
                if "person" in self.complete_list:
                    self.complete_list.remove("person")


        if self.clear_timer != 0:
            temp_time = time.time()
            if (temp_time - self.clear_timer) >= 300:
                self.clear_timer = 0
                self.complete_list = []



    def recognize_result(self,recv_data):
        dic = json.loads(recv_data.data)
        name = dic["name"]
        pos = {}
        pos["x center"] = dic["x center"]
        pos["y center"] = dic["y center"]
        pos["width"] = dic["width"]
        pos["height"] = dic["height"]
        pos["prob"] = dic["prob"]
        pos["color"] = dic["color"]
        self.res[name] = pos
        if name not in self.object_list:
            self.object_list.append(name)

    def sr_receive(self,recv_data):
        if self.sr_recvive_flag == True:
            sr_res = recv_data.data
            sr_res = sr_res.lower()
            print(sr_res)
            if self.response == self.No_response:
                for word in self.negative_list:
                    if word in sr_res:
                        self.response = self.Negative
                        self.speak_dic["speak"] = "dislike response"
                        self.ros_pub(self.speak_out_pub, self.speak_dic)
                        #self.speak_out_pub.publish("Oh, you don't like it")
                        break
            if self.response == self.No_response:
                for word in self.positive_list:
                    if word in sr_res:
                        self.response = self.Positive
                        self.speak_dic["speak"] = "like response"
                        self.ros_pub(self.speak_out_pub, self.speak_dic)
                        #self.speak_out_pub.publish("I see, you like it")
                        break
            if self.response == self.No_response:
                for word in self.question_list:
                    if word in sr_res:
                        self.speak_dic["speak"] = "color"
                        self.speak_dic["color"] = self.color
                        self.ros_pub(self.speak_out_pub, self.speak_dic)
                        self.question_flag = True
                        self.speak_dic = {}
                        break
                if self.question_flag == False:
                    self.response = self.Neutral
                    self.speak_dic["speak"] = "blind response"
                    self.ros_pub(self.speak_out_pub, self.speak_dic)
                self.question_flag = False


    def delay(self,sec):
        clock1 = time.time()
        clock2 = time.time()
        while ((clock2 - clock1) < sec):
            clock2 = time.time()


    def track_object(self):
        if self.track_name == "":
            if not self.complete_list:
                self.clear_timer = time.time()
        #if False:
            if self.object_list:
                for object in self.object_list:
                    if object not in self.complete_list:
                        self.track_name = object
                        self.object_find_pub.publish(self.track_name)
                        self.track_clock1=time.time()
                        print("now tracking " + object)
                        if self.track_name != "person":
                            self.person_find = False
                        break
        else:
            position = self.res[self.track_name]
            self.res[self.track_name] = ""

            #print(position)
            if position:
                self.x_center = int(position["x center"])
                self.y_center = int(position["y center"])
                self.width = position["width"]
                self.height = position["height"]
                self.prob = position["prob"]
                self.color = position["color"]
                #servo_send_json = {}
                #servo_send_json["x center"] = position["x center"]
                #servo_send_json["y center"] = position["y center"]
                #self.ros_pub(self.servo_move_pub,servo_send_json)
                #servo_send_buff = json.dumps(position)
                #self.servo_move_pub.publish(servo_send_buff)

                print("tracking:" + self.track_name + ", x center:" + str(self.x_center) + ", y center:" + str(self.y_center) + " ,color:" + self.color)
                if (self.x_center < 288)  and (self.x_center > 128):
                    if (self.y_center < 288) and (self.y_center > 128):

                        #self.camera_command["command"] = "stop"
                        self.ros_pub(self.camera_pub, self.camera_command)

                        if self.track_name == "person":
                            if self.person_find == False:

                                #self.recognize_flag_pub.publish("Off")
                                #self.speak_out_pub.publish("Hello!")
                                self.speak_dic["speak"] = "greeting"
                                self.ros_pub(self.speak_out_pub,self.speak_dic)
                                self.save_image_msg["Type"] = self.Person
                                self.save_image_msg["Object"] = self.track_name
                                #save_image_send_buff = json.dumps(self.save_image_msg)
                                #self.save_image_pub.publish(save_image_send_buff)
                                self.ros_pub(self.save_image_pub,self.save_image_msg)
                                self.person_find = True
                                if self.track_name not in self.complete_list:
                                    self.complete_list.append(self.track_name)
                                    self.person_timer = time.time()
                                self.delay(3)
                            self.template_clear_pub.publish("clear")
                            self.object_find_pub.publish("clear")
                            servo_command_dic = {"command":"default"}
                            self.ros_pub(self.servo_command_pub, servo_command_dic)
                        else:
                            #self.recognize_flag_pub.publish("Off")
                            #self.speak_out_pub.publish("There is a " + self.track_name + " ,do you like it?")
                            self.speak_dic["speak"] = "ask"
                            self.speak_dic["object"] = self.track_name
                            self.ros_pub(self.speak_out_pub,self.speak_dic)
                            self.speak_dic = {}
                            self.sr_recvive_flag = True
                            while self.response == self.No_response:
                                self.delay(0.5)
                            self.sr_recvive_flag = False
                            self.save_image_msg["Type"] = self.response
                            self.save_image_msg["Object"] = self.track_name
                            #save_image_send_buff = json.dumps(self.save_image_msg)
                            #self.save_image_pub.publish(save_image_send_buff)
                            self.ros_pub(self.save_image_pub,self.save_image_msg)
                            self.delay(3)
                            self.template_clear_pub.publish("clear")
                            self.object_find_pub.publish("clear")
                            #self.recognize_flag_pub.publish("On")
                            servo_command_dic = {"command":"default"}
                            self.ros_pub(self.servo_command_pub,servo_command_dic)
                            self.response = self.No_response
                            if self.track_name not in self.complete_list:
                                self.complete_list.append(self.track_name)
                        #self.camera_command["command"] = "send"
                        self.ros_pub(self.camera_pub,self.camera_command)
                        self.delay(1)
                        self.track_name = ""
                        self.res = {}
                        self.object_list = []

            else:
                self.track_clock2=time.time()
                #print(str((self.track_clock2 - self.track_clock1)*500))
                if (self.track_clock2 - self.track_clock1) > 3:
                    #print("I cannot find " + self.track_name)
                    self.object_list.remove(self.track_name)
                    if self.track_name in self.complete_list:
                        self.complete_list.remove(self.track_name)
                    #if self.track_name != "person":
                        #self.speak_out_pub.publish("I thought there is a " + self.track_name)
                    self.track_name = ""
                    #self.delay(1)



def dialog_run(dialog):
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        dialog.track_object()
        dialog.check_clear_list()
        #dialog.speak_sth()
        rate.sleep()



if __name__ == '__main__':
    dialog = Dialog_class()
    dialog_run(dialog)
