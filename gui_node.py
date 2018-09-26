#!/usr/bin/env python
import threading
import time
import sys
import Tkinter as tk
import json
import rospy
import io
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from sound_play.msg import SoundRequest
from PIL import Image
from PIL import ImageTk

file_path = __file__.replace("gui_node.py","")
setting_file = open(file_path + "settings.txt",'r')
js = setting_file.read()
settings = json.loads(js)
setting_file.close()

image_file_name = file_path + settings["image file"]
json_send = {"command":"none","send":False}
comm_pub = rospy.Publisher('command_topic', String, queue_size = 1)
speaker_pub = rospy.Publisher('speaker_text',String,queue_size = 10)
sound_play_pub = rospy.Publisher('robotsound',SoundRequest,queue_size = 10)
send_image_pub = rospy.Publisher('image_save_stream',CompressedImage, queue_size = 1)
sound_msg = SoundRequest()
rospy.init_node('gui_node')
send_flag = False
#image_stream = io.BytesIO()

class Guis(object):
    def __init__(self,master):
        global image_file_name
        self.master = master
        frame_1 = tk.Frame(master,width = 20, height = 5)
        frame_2 = tk.Frame(master,width = 200, height = 5)
        frame_3 = tk.Frame(master,width = 200, height = 50)
        frame_4 = tk.Frame(master,width = 200, height = 50)
        frame_5 = tk.Frame(master,width = 200, height = 50)
        frame_6 = tk.Frame(master,width = 200, height = 50)
        frame_7 = tk.Frame(master,width = 200, height = 50)
        self.frame_8 = tk.Frame(master,width = 200, height = 50)
        self.frame_9 = tk.Frame(master,width = 200, height = 50)
        frame_1.pack(side = tk.TOP)
        frame_2.pack()
        frame_3.pack()
        frame_4.pack()
        frame_5.pack()
        frame_6.pack()
        frame_7.pack()
        self.frame_8.pack()
        self.frame_9.pack()
        self.photo = Image.open(image_file_name)
        self.photo = ImageTk.PhotoImage(self.photo)
        self.canvas = tk.Canvas(master,height = 300,width = 400)
        self.canvas.create_image(20,20,image = self.photo,anchor = tk.NW)
        self.canvas.pack(side = tk.BOTTOM)
        #self.label = tk.Label(master, image = self.photo)
        #self.label.pack(side = tk.BOTTOM)

        self.button_up = tk.Button(frame_1, width = 10,height = 5,text = "Up" , command = self.command_w)
        self.button_up.pack(side = tk.TOP)

        self.button_left = tk.Button(frame_2, width = 10,height = 5,text = "Left" , command = self.command_a)
        self.button_left.pack(side = tk.LEFT,anchor = "w")

        self.button_down = tk.Button(frame_2, width = 10,height = 5,text = "Down" , command = self.command_s)
        self.button_down.pack(side = tk.LEFT,anchor = "w")

        self.button_up = tk.Button(frame_2, width = 10,height = 5,text = "Right" , command = self.command_d)
        self.button_up.pack(side = tk.LEFT,anchor = "w")

        self.button_quit = tk.Button(frame_3,width = 10,height =5,text = "Quit" , command = self.command_quit)
        self.button_quit.pack(side = tk.LEFT,anchor = "w")

        self.button_send = tk.Button(frame_3,width = 10,height =5,text = "Refresh" , command = self.command_send)
        self.button_send.pack(side = tk.LEFT,anchor = "w")

        self.button_stop = tk.Button(frame_3,width = 10,height =5,text = "Stop refreshing" , command = self.command_stop)
        self.button_stop.pack(side = tk.LEFT,anchor = 'w')

        self.button_servo = tk.Button(frame_5,width = 10,height =5,text = "Move servo" , command = self.servo_move)
        self.button_servo.pack(side = tk.LEFT,anchor = 'w')



        self.button_speak = tk.Button(frame_7,width = 10,height =5,text = "Speak out" , command = self.speak_send)
        self.button_speak.pack(side = tk.LEFT, anchor = 'w')

        self.button_recognize = tk.Button(frame_5,width = 10,height =5,text = "Recognize" , command = self.recogize_send)
        self.button_recognize.pack(side = tk.LEFT, anchor = 'w')

        self.label_pan = tk.Label(frame_4,text = "pan:")
        self.label_tilt = tk.Label(frame_4,text = "tilt:")
        self.label_speak = tk.Label(frame_6,text = "speak text:")
        self.label_speak_text = tk.Label(self.frame_8,text = "")
        self.label_hear_text = tk.Label(self.frame_9,text = "")
        self.entry_pan = tk.Entry(frame_4)
        self.entry_tilt = tk.Entry(frame_4)
        self.entry_speak = tk.Entry(frame_6)
        self.label_pan.grid(row = 0,sticky = tk.E)
        self.label_tilt.grid(row = 1,sticky = tk.E)
        self.label_speak.grid(row = 0,sticky = tk.E)
        self.label_speak_text.pack(side = tk.LEFT , anchor = 'w')
        self.label_hear_text.pack(side = tk.LEFT , anchor = 'w')
        self.entry_pan.grid(row = 0, column = 1)
        self.entry_tilt.grid(row = 1, column = 1)
        self.entry_speak.grid(row =0, column = 1)

    def command_w(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="move"
        json_send["direction"]="up"
        json_send["send"]=True
        #print command

    def command_a(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="move"
        json_send["direction"]="left"
        json_send["send"]=True
        #print command

    def command_s(self):
         global json_send
         while json_send == True:
             i = 1
         json_send["command"]="move"
         json_send["direction"]="down"
         json_send["send"]=True
        #print command

    def command_d(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="move"
        json_send["direction"]="right"
        json_send["send"]=True
        #print command

    def command_quit(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="quit"
        json_send["send"]=True
        #print command

    def command_send(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="send"
        json_send["send"]=True

    def command_stop(self):
        global json_send
        while json_send == True:
            i = 1
        json_send["command"]="stop"
        json_send["send"]=True

    def servo_move(self):
        global comm_pub
        global json_send
        #json_send.pop("direction")
        try:
            pan_value = int(self.entry_pan.get())
        except:
            pan_value = "Invalid"
        try:
            tilt_value = int(self.entry_tilt.get())
        except:
            tilt_value = "Invalid"
        #print(pan_value)
        #print(tilt_value)
        if pan_value != "Invalid" and tilt_value != "Invalid":
            json_send["command"] = "move to"
            json_send["pan"] = pan_value
            json_send["tilt"] = tilt_value
            send_buff = json.dumps(json_send)
            comm_pub.publish(send_buff)
            json_send.pop("pan")
            json_send.pop("tilt")
        else:
            print("Syntax Error!")

    def speak_send(self):
        global speaker_pub
        global sound_msg
        global sound_play_pub
        speak_text = str(self.entry_speak.get())
        sound_msg.arg = speak_text
        sound_msg.volume = 1
        sound_msg.sound = -3
        sound_msg.command = 1
        if speak_text:
            #print(sound_msg.arg)
            speaker_pub.publish(speak_text)
            sound_play_pub.publish(sound_msg)


    def recogize_send(self):
        global send_flag
        if send_flag == True:
            send_flag = False
        else:
            send_flag = True



    def update_image(self,image_stream):
        try:
            self.photo = Image.open(image_stream)
            self.photo = ImageTk.PhotoImage(self.photo)
            #self.canvas.pack_forget()
            #self.canvas = tk.Canvas(self.master,height = 240,width = 320)
            self.canvas.create_image(20,20,image = self.photo,anchor = tk.NW)
            #self.canvas.pack(side = tk.BOTTOM)
            #self.label.pack_forget()
            #self.label = tk.Label(self.master, image = self.photo)
            #self.label.pack(side = tk.BOTTOM)
        except IOError:
            print("camera not ready yet, please try again")
        #while json_send == True:
        #    i = 1
        #json_send["command"] = "send"
        #send_buff = json.dumps(json_send)
        #comm_pub.publish(send_buff)

    def speak_text_update(self,speak_text):
        self.label_speak_text.pack_forget()
        self.label_speak_text = tk.Label(self.frame_8,text = speak_text)
        self.label_speak_text.pack()

    def hear_text_update(self,hear_text):
        self.label_hear_text.pack_forget()
        self.label_hear_text = tk.Label(self.frame_9,text = hear_text)
        self.label_hear_text.pack()




class GuiThread(threading.Thread):
    def run(self):
        self.gui_root = tk.Tk()
        self.gui_obj = Guis(master = self.gui_root)
        self.gui_root.mainloop()

    def image_update(self,image_stream):
        self.gui_obj.update_image(image_stream)

    def speak_text_update(self,speak_text):
        self.gui_obj.speak_text_update("Speak:" + speak_text)

    def hear_text_update(self,hear_text):
        self.gui_obj.hear_text_update("Hear:" + hear_text)

guiloop = GuiThread()
guiloop.start()



def image_recv_update(recv_image):
    #global image_stream
    global send_flag
    global send_image_pub
    global guiloop
    if recv_image.format == "jpeg":
        with io.BytesIO() as image_stream:
            #print(len(recv_image.data))
            image_stream.write(recv_image.data)
            #print(len(image_stream.getvalue()))
            guiloop.image_update(image_stream)
            #print(send_flag)
            #if send_flag == True:
                #send_image_pub.publish(recv_image)
                #send_flag = False



def speak_text(recv_text):
    global guiloop
    guiloop.speak_text_update(recv_text.data)

def sr_result(recv_text):
    global guiloop
    guiloop.hear_text_update(recv_text.data)

def send_switch(recv_data):
    global send_flag
    print("Here!")
    if recv_data.data == "Ready":
        send_flag = True


def command_sender():
    #rospy.Subscriber('image_receive_complete',String,update_image_func)
    rospy.Subscriber('image_stream',CompressedImage,image_recv_update)
    rospy.Subscriber('speaker_json',String,speak_text)
    rospy.Subscriber('image_send_save',String ,send_switch)
    rospy.Subscriber('sr_result',String, sr_result)
    while not rospy.is_shutdown():
        if json_send["send"] == True:
            json_send.pop("send")
            send_buff = json.dumps(json_send)
            comm_pub.publish(send_buff)
            json_send["send"] = False


if __name__ == '__main__':

    try:
        command_sender()
    except rospy.ROSInterruptException:
        pass
