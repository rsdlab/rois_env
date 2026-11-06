#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################​##################
import rospy
import math
import yaml
import os
from std_srvs.srv import Trigger, TriggerResponse
from rois_env_ros1.srv import *
import actionlib
from rois_env_ros1.msg import *




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
      
    elif component_ref == "Approach":
      get_name = '/get_parameter/' + component_ref
      get_param = rospy.ServiceProxy(get_name, approach_get_parameter)

    elif component_ref == "Pick_and_Place":
      get_name = '/get_parameter/' + component_ref
      get_param = rospy.ServiceProxy(get_name, approach_get_parameter)

    elif component_ref == "Pick":
      get_name = '/get_parameter/' + component_ref
      get_param = rospy.ServiceProxy(get_name, approach_get_parameter)

    elif component_ref == "Place":
      get_name = '/get_parameter/' + component_ref
      get_param = rospy.ServiceProxy(get_name, approach_get_parameter)

    elif component_ref == "Shelf":
      get_name = '/get_parameter/' + component_ref
      get_param = rospy.ServiceProxy(get_name, approach_get_parameter)

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
    
    ###
    elif component_ref == "Approach":
      set_name =  '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, approach_set_parameter)
      result = set_param(component_ref, parameters)
    ###
      
      print(result.Returncode_t)

    elif component_ref == "Pick_and_Place":
      set_name = '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, approach_set_parameter)
      result = set_param(component_ref, parameters)
      print(result.Returncode_t)

    elif component_ref == "Pick":
      set_name = '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, approach_set_parameter)
      result = set_param(component_ref, parameters)
      print(result.Returncode_t)

    elif component_ref == "Place":
      set_name = '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, approach_set_parameter)
      result = set_param(component_ref, parameters)
      print(result.Returncode_t)

    elif component_ref == "Shelf":
      set_name = '/set_parameter/' + component_ref
      set_param = rospy.ServiceProxy(set_name, approach_set_parameter)
      result = set_param(component_ref, parameters)
      print(result.Returncode_t)

    return 

  def execute(self, command_unit_list):
    """サービスで移動開始を要求する"""
    try:
      response = self.service_client(command_unit_list)
      print(response)
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


def format_shelf_command(args):
    if isinstance(args, str):
        return args

    if isinstance(args, dict):
        payload = {key: str(value) for key, value in args.items() if value is not None}
    elif isinstance(args, (list, tuple)):
        keys = ["layer", "time", "movement"]
        payload = {}
        for key, value in zip(keys, args):
            if value is not None:
                payload[key] = str(value)
    else:
        return str(args)

    if not payload:
        return ""

    return yaml.safe_dump(payload, default_flow_style=False, sort_keys=False).strip()


def format_pick_and_place_command(args):
    if isinstance(args, str):
        return args.strip()

    if isinstance(args, dict):
        ordered = {key: str(value) for key, value in args.items() if value is not None}
        return yaml.safe_dump(ordered, default_flow_style=False, sort_keys=False).strip()

    if isinstance(args, (list, tuple)):
        serialised = [str(value) for value in args]
        return yaml.safe_dump(serialised, default_flow_style=True).strip()

    return str(args)

def format_pick_place_command(task_id, args):
    payload = {}

    if task_id:
        payload["task_id"] = str(task_id)

    if isinstance(args, dict):
        target = (
            args.get("target")
            or args.get("object")
            or args.get("item")
        )
        location = (
            args.get("location")
            or args.get("place")
            or args.get("spot")
            or args.get("position")
            or args.get("from")
            or args.get("to")
            or args.get("source")
            or args.get("destination")
            or args.get("取る場所")
            or args.get("置く場所")
        )
        motion = (
            args.get("motion")
            or args.get("motion_name")
            or args.get("action")
        )
        if target:
            payload["target"] = str(target)
        if location:
            payload["location"] = str(location)
        if motion:
            payload["motion"] = str(motion)
    elif isinstance(args, (list, tuple)):
        if len(args) > 0 and args[0] is not None:
            payload["target"] = str(args[0])
        if len(args) > 1 and args[1] is not None:
            payload["location"] = str(args[1])
        if len(args) > 2 and args[2] is not None:
            payload["motion"] = str(args[2])
    elif args:
        payload["target"] = str(args)

    if not (payload.get("target") and payload.get("location") and payload.get("motion")):
        return ""

    return yaml.safe_dump(payload, default_flow_style=False, sort_keys=False).strip()


def speech(speech_text):
    component_ref = "Speech_Synthesis"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.set_parameter(component_ref, speech_text)
    rois.execute("start")
    # rospy.sleep(1)
    result = rois.monitor_progress() ###
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


def approach(approach_command):
    component_ref = "Approach"
    print(component_ref)
    rois.bind_any(component_ref)
    rois.set_parameter(component_ref, approach_command)###
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def shelf(command_args):
    component_ref = "Shelf"
    print(component_ref)
    rois.bind_any(component_ref)

    command_string = format_shelf_command(command_args)
    if not command_string:
        rospy.logwarn("Shelf command arguments are empty; skipping execution.")
        rois.release(component_ref)
        return None

    rois.set_parameter(component_ref, command_string)
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def pick_and_place(command_args):
    component_ref = "Pick_and_Place"
    print(component_ref)
    rois.bind_any(component_ref)

    command_string = format_pick_and_place_command(command_args)
    if not command_string:
        rospy.logwarn("Pick_and_Place command arguments are empty; skipping execution.")
        rois.release(component_ref)
        return None

    rois.set_parameter(component_ref, command_string)
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def pick(command_args, task_id=""):
    component_ref = "Pick"
    print(component_ref)
    rois.bind_any(component_ref)

    command_string = format_pick_place_command(task_id, command_args)
    if not command_string:
        rospy.logwarn("Pick command arguments are empty or invalid; skipping execution.")
        rois.release(component_ref)
        return None

    rois.set_parameter(component_ref, command_string)
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def place(command_args, task_id=""):
    component_ref = "Place"
    print(component_ref)
    rois.bind_any(component_ref)

    command_string = format_pick_place_command(task_id, command_args)
    if not command_string:
        rospy.logwarn("Place command arguments are empty or invalid; skipping execution.")
        rois.release(component_ref)
        return None

    rois.set_parameter(component_ref, command_string)
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



    print(person_detect())###
    rospy.sleep(1)

    speech("hello")###

    # print("recognition greeting")
    # response = recognize_response("japanese")###
    # print(response)
    
    person_id = patient_identify()###
    print(person_id)###

    rospy.sleep(1)

    print(person_localize())
    rospy.sleep(1)

    move_forward([[200, 0],[0, 0]])   
    rospy.sleep(3)

    ###
    # 福田さん
    if person_id == "Person4":
      # speech("Speech_Synthesis" ,"measure1")
      speech("measure3")
    # 水藤さん
    elif person_id == "Person5":
      speech("measure4")
    # 石崎さん
    elif person_id == "Person6":
      speech("measure5")
    ###

    # print("recognition responce")
    # response = recognize_response("japanese")
    # print(response)

    # rospy.sleep(1)
    
    speech("yorosiku")
    
    rospy.sleep(1)
    
    approach("approach1")###

    rospy.sleep(1)

    speech("check")

    rospy.sleep(1)

    approach("approach2")###

    rospy.sleep(1)

    approach("approach3")###

    # touch()###
    
    rospy.sleep(1)
    
    speech("thank")

    rospy.sleep(1)

    leave()
    rospy.sleep(1)




    speech("ask1")
    rospy.sleep(1)

    # response = recognize_response("japanese")
    response = "良い" #Test

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
        task_act = task.get('act', '')
        task_arg = task.get('arg', '')
        task_list.append((task_name, task_arg))

        if task_act:
          rospy.loginfo(f"Scenario action: {task_act}")

        if task_name == "Speech_Synthesis":
          print(task_arg)
          # 認識結果を反映させて発話
          if task_arg == "identification":
            # 福田さん
            if person_id == "Person4":
              # speech("Speech_Synthesis" ,"measure1")
              speech("measure3")
            # 水藤さん
            elif person_id == "Person5":
              speech("measure4")
            # 石崎さん
            elif person_id == "Person6":
              speech("measure5")
          
          # 解釈結果を反映させて発話
          elif task_arg == "decision":
            voice = judgement(response)
            print(voice)
            speech(voice)

          # 発話させたい内容を入力（デフォルト）
          else:
            speech(task_arg)

          rospy.sleep(2)###

        elif task_name == "Move":
          move_forward(task_arg)   
          # シミュレーション時のreturn OKが早いため
          rospy.sleep(3)###


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
          # approach()
          approach(task_arg)
          rospy.sleep(1)###

        elif task_name == "Pick":
          pick(task_arg, task_act)
          rospy.sleep(1)

        elif task_name == "Place":
          place(task_arg, task_act)
          rospy.sleep(1)

        elif task_name == "Pick_and_Place":
          pick_and_place(task_arg)
          rospy.sleep(1)

        elif task_name == "Shelf":
          shelf(task_arg)
          rospy.sleep(1)

        elif task_name == "Touch":
          touch()
          rospy.sleep(4)###

        elif task_name == "Leave":
          leave()
          rospy.sleep(1)###

    
 
    print(task_list)

    # # 機能名と引数を抽出
    # functions, launch_files = extract_function_and_parameters(scenario)

    # print(data)

    


if __name__ == '__main__':
  rospy.init_node('service_app_node')
  try:
    rois = ROIS_METHOD()

    user_input = input("選択してください: A.シナリオ,  B.デフォルト >>> ")
    print(user_input)
    if user_input == "A" or user_input == "a":
      # scenario_file = input("シナリオ名を入力してください: ")
      # scenario_ = os.environ['HOME'] + "/RTSI_FW/scenario.yaml" 
      # scenario_ = os.environ['HOME'] + "/RTSUI_FW/scenario.yaml" 
      scenario_ = os.environ['HOME'] + "/RTSI_FW_beta/scenario.yaml" 
      scenario(scenario_)

    elif user_input == "B" or user_input == "b":
      main()

    else:
      print("finish")

  except rospy.ROSInterruptException:
    rospy.loginfo("クライアントが中断されました。")
