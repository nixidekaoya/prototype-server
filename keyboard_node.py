#!/usr/bin/env python
import time
import rospy
import json
from std_msgs.msg import String



def keyboard_input():
    file_path = __file__.replace("keyboard_node.py","")
    setting_file = open(file_path + "settings.txt",'r')
    js = setting_file.read()
    settings = json.loads(js)
    setting_file.close()
    comm_pub = rospy.Publisher('command_topic', String, queue_size = 1)
    speaker_pub = rospy.Publisher('speaker_text',String,queue_size = 1)
    sr_pub = rospy.Publisher('sr_result',String,queue_size = 1)
    input_buff = ""
    json_send = {}
    #sound_msg = SoundRequest()
    rospy.init_node('keyboard_node')
    while True:
        if input_buff == "":
            input_buff = raw_input()
            #print(input_buff)
            if input_buff.startswith("camera on"):
                json_send["command"] = "send"
                send_buff = json.dumps(json_send)
                comm_pub.publish(send_buff)
                print(send_buff)
            elif input_buff.startswith("camera off"):
                json_send["command"] = "stop"
                send_buff = json.dumps(json_send)
                comm_pub.publish(send_buff)
                print(send_buff)
            elif input_buff.startswith("speak "):
                send_buff = input_buff[6:]
                speaker_pub.publish(send_buff)
                print(send_buff)
            elif input_buff.startswith("default"):
                json_send["command"] = "default"
                send_buff = json.dumps(json_send)
                comm_pub.publish(send_buff)
                print(send_buff)
            elif input_buff.startswith("hear "):
                send_buff = input_buff[5:]
                sr_pub.publish(send_buff)
                print(send_buff)
            json_send = {}
            input_buff = ""


if __name__ == '__main__':
    try:
        keyboard_input()
    except rospy.ROSInterruptException:
        pass
