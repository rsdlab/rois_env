#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################​##################
import rospy
import math
import yaml
import os
from std_srvs.srv import Trigger, TriggerResponse
from rois_env.srv import *
import actionlib
from rois_env.msg import *

class ROIS_METHOD:
  def __init__(self):

    self.connect = rospy.ServiceProxy( '/connect', system_interface)
    rospy.wait_for_service( '/connect')
    self.disconnect = rospy.ServiceProxy( '/disconnect', system_interface)
    rospy.wait_for_service( '/bind_any')
    self.bind = rospy.ServiceProxy( '/bind_any', bind_any)
    self.release = rospy.ServiceProxy( '/release', release)
    self.subscribe = rospy.ServiceProxy( '/subscribe', subscribe_)
    self.service_client = rospy.ServiceProxy( '/execute', execute)
    self.arm = rospy.ServiceProxy("/robot_action",RobotAction)



  def test_execute(self,component_ref):
    self.component_ref = component_ref
    print(f"test_execute {component_ref}")
    rospy.sleep(3)
    return 'succeeded'

  def connect(self,connect):
    print("connect_engine")
    
    result = self.connect(connect)
    
    return result.returncode_t 


  def disconnect(self, connect):
    print("connect_engine")
    system_if = rospy.ServiceProxy('/disconnect_engine', system_interface)
    result = system_if(connect)
    
    if result.returncode_t == "OK":
      return "succeeded"
    else:
      return "retry"

  def bind_any(self,component_ref):
    bind = self.bind(component_ref)
    return bind.Returncode_t

  def release(self, component_ref):
    release = self.release(component_ref)
    return release.Returncode_t

  def subscribe(self, event_type):
    subscribe = self.subscribe(event_type)
    return subscribe.Returncode_t

  def get_parameter(self, component_ref):
    if component_ref == "Move":
      get_name =  '/get_parameter/' + component_ref  
      get_param = rospy.ServiceProxy(get_name, move_get_parameter)

    elif component_ref == "Speech_Synthesis":
      get_name =  '/get_parameter/' + component_ref 
      get_param = rospy.ServiceProxy(get_name, speech_get_parameter)
      
      
      return get_param(component_ref)


  def set_parameter(self, component_ref, parameters):
    if component_ref == "Move":
      set_name =  '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, move_set_parameter)

      result = set_param(parameters[0],parameters[1])


    elif component_ref == "Speech_Synthesis":
      set_name =  '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, speech_set_parameter)
      result = set_param(component_ref, parameters)
      
      print(result.Returncode_t)

      return 

  def execute(self, command_unit_list):
    """サービスで移動開始を要求する"""
    try:
      response = self.service_client(command_unit_list)
      if response.return_t == "OK":
        rospy.loginfo("コマンドを開始しました。アクションで進捗を確認します。")

        return response.return_t
      else:
        rospy.logwarn("コマンドの開始に失敗しました。")
    except rospy.ServiceException as e:
      rospy.logerr(f"サービス呼び出しに失敗しました: {e}")

  def monitor_progress(self):
    rospy.loginfo("待機中...")
    result = rospy.wait_for_message( '/completed', completed)
    rospy.loginfo(f"Received message: {result.command_id}", )
    rospy.loginfo(f"Received message: {result.status}", )


  def monitor_event(self):
    rospy.loginfo("待機中...")
    result = rospy.wait_for_message( '/notify_event', notifyevent)
    rospy.loginfo(f"Received message: {result.event_id}", )
    rospy.loginfo(f"Received message: {result.event_type}", )
    rospy.loginfo(f"Received message: {result.subscribe_id}", )

    return result.event_id


  def subscribe(self, event_type):
    subservice = rospy.ServiceProxy( '/Subscribe', subscribe_)
    result = subservice(event_type)

    return result

  def unsubscribe(self, subscribe_id):
    unsubservice = rospy.ServiceProxy( '/Unsubscribe', unsubscribe_)
    result = unsubservice(subscribe_id)

    return result



  def get_command_result(self, command_id):
    command_result = rospy.ServiceProxy( '/get_command_result', get_command_result)
    result = command_result(command_id, "")
    return result


  def get_event_detail(self, event_id):
    print(event_id)
    if "recog" in  event_id:
      event_result = rospy.ServiceProxy( '/recognized_event_detail', get_event_detail_speech_recognized)

    elif "detected" in event_id:
      event_result = rospy.ServiceProxy( '/detected_event_detail', get_event_detail_person_detected)

    elif "local" in event_id:
      event_result = rospy.ServiceProxy( '/local_event_detail', get_event_detail_person_localized)

    elif "ident" in event_id:
      event_result = rospy.ServiceProxy( '/identified_event_detail', get_event_detail_person_identified)

    result = event_result(event_id)
    return result
  
    

def add_item(_list, item):
  if item not in _list:
    _list.append(item)
    print(f"{item} を追加しました")
    return True
  else:
    print(f"{item} は既にリストに存在します")
    print(_list)
    return False


def speech(speech_text):
    component_ref = "Speech_Synthesis"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.set_parameter(component_ref, speech_text)
    rois.execute("start")
    rospy.sleep(1)
    result = rois.monitor_progress()
    rois.release(component_ref)

    return 

def speech_bind(component_ref):
  rois.bind_any(component_ref)
  rois.release(component_ref)

def recognize_response(languages):
    component_ref = "Speech_Recognition"
    event_id = "speech_recognized"
    rois.bind_any(component_ref)
    rois.subscribe(event_id)
    rois.execute("start")
    result = rois.monitor_event()

    event_result = rois.get_event_detail(result)
    print(event_result)
    rois.release(component_ref)    
    return event_result.recognized_text


def patient_identify():
    component_ref = "Person_Identification"
    print(component_ref)
    event_id = "person_identified"
    rois.bind_any(component_ref)
    rois.subscribe(event_id)
    rois.execute("start")
    result = rois.monitor_event()

    event_result = rois.get_event_detail(result)
    rois.release(component_ref)    
    return event_result.person_ref[0]


def person_detect():
    component_ref = "Person_Detection"
    print(component_ref)
    event_id = "person_detected"
    rois.bind_any(component_ref)
    rois.subscribe(event_id)
    rois.execute("start")
    result = rois.monitor_event()

    event_result = rois.get_event_detail(result)
    rois.release(component_ref)    
    return event_result.number

def person_localize():
    component_ref = "Person_Localization"
    print(component_ref)
    event_id = "person_localized"
    rois.bind_any(component_ref)
    rois.subscribe(event_id)
    rois.execute("start")
    result = rois.monitor_event()

    event_result = rois.get_event_detail(result)
    rois.release(component_ref)    
    return event_result



def move_forward(line):
    component_ref = "Move"
    rois.bind_any(component_ref)

    print(line)
    rois.set_parameter(component_ref, line)
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def judgement(input_response):
  chat = rospy.ServiceProxy("/chat_service", Chat)
  result = chat(input_response)
  print(result.response_text)
  check = rospy.ServiceProxy("/check_service", decision)
  judge = check(result.response_text)
  return judge.response_text


def approach():
    component_ref = "Approach"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result

def leave():
    component_ref = "Leave"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def touch():
    component_ref = "Touch"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def main_action():
    rois.connect("connect")

    approach("Approach")
    rospy.sleep(1)
    touch("Touch")
    rospy.sleep(1)

    leave("Leave")
    


def main():

    rois.connect("connect")

    speech_bind("Speech_Synthesis")
    speech_bind("Speech_Recognition")

    print(person_detect())
    rospy.sleep(1)

    speech("hello")
    response = recognize_response("japanese")
    print(response)
    
    person_id = patient_identify()
    print(person_id)

    rospy.sleep(2)

    print(person_localize())

    move_forward( [[300, 0, 0],[0,0]])   
    rospy.sleep(3)

    if person_id == "Person4":
      speech("measure3")
    elif person_id == "Person3":
      speech("measure2")

    rospy.sleep(5)
    

    speech("yorosiku")
    
    rospy.sleep(3)
    
    approach()

    rospy.sleep(3)

    speech("check")

    rospy.sleep(5)

    touch()
    
    rospy.sleep(4)
    
    speech("thank")

    rospy.sleep(3)

    leave()
    rospy.sleep(3)

    speech("ask1")
    rospy.sleep(0.5)
    response = recognize_response("japanese")
    print(response)

    voice = judgement(response)
    print(voice)
  
    speech(voice)


def scenario(scenario):
    with open(scenario , 'r') as infile:
        data = yaml.safe_load(infile)


    scenario = data.get('scenario', [])

    task_list =[]

    rois.connect("connect")

    for task in scenario:
        task_name = task.get('task', '')
        task_arg = task.get('arg', '')
        task_list.append((task_name, task_arg))


        if task_name == "Speech_Synthesis":
          speech(task_arg)

          rospy.sleep(2)


        elif task_name == "Move":
          move_forward(task_arg)   
          rospy.sleep(3)


        elif task_name == "Person_Detection":
          person_detect()
        
        elif task_name == "Speech_Recognition":
          response = recognize_response(task_arg)
          print(f"reconized word :{response}")

        elif task_name == "Person_Identification":
          person_id = patient_identify()
          print(person_id)

        elif task_name == "Person_Localization":
          person_localize()

        elif task_name == "Approach":
          approach()

        elif task_name == "Touch":
          touch()

        elif task_name == "Leave":
          leave()
          rospy.sleep(4)


 
    print(task_list)

    


if __name__ == '__main__':
  rospy.init_node('service_app_node')
  try:
    rois = ROIS_METHOD()

    user_input = input("選択してください: A.シナリオ,  B.デフォルト >>> ")
    print(user_input)
    if user_input == "A":
      scenario_ = os.environ['HOME'] + "/RTSI_FW/scenario.yaml" 
      scenario(scenario_)

    elif user_input == "B":
      main()

    else:
      print("finish")

  except rospy.ROSInterruptException:
    rospy.loginfo("クライアントが中断されました。")

