#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################​##################
import rclpy
from rclpy.node import Node
import time
import math
import yaml
import os

from rois_env_ros2.srv import (
    SystemInterface,
    BindAny,
    Release,
    Subscribe,
    Unsubscribe,
    Execute,
    MoveGetParameter,
    MoveSetParameter,
    SpeechGetParameter,
    SpeechSetParameter,
    ApproachGetParameter,
    ApproachSetParameter,
    ObjectGraspingSetParameter,
    GetCommandResult,
    GetEventDetailSpeechRecognized,
    GetEventDetailPersonDetected,
    GetEventDetailPersonLocalized,
    GetEventDetailPersonIdentified,
    Chat,
    Decision,
    RobotAction,
)
from rois_env_ros2.msg import Completed, Notifyevent


class ROIS_METHOD:
  def __init__(self):

    self.node = Node('service_app_node')

    self.connect_client = self.node.create_client(SystemInterface, '/connect')
    self.connect_client.wait_for_service()

    self.disconnect_client = self.node.create_client(SystemInterface, '/disconnect')

    self.bind_client = self.node.create_client(BindAny, '/bind_any')
    self.bind_client.wait_for_service()

    self.release_client = self.node.create_client(Release, '/release')
    self.subscribe_client = self.node.create_client(Subscribe, '/subscribe')
    self.service_client = self.node.create_client(Execute, '/execute')
    self.arm_client = self.node.create_client(RobotAction, '/robot_action')


  def _wait_future(self, future):
    rclpy.spin_until_future_complete(self.node, future)

    if future.exception() is not None:
      raise RuntimeError(f"サービス呼び出しに失敗しました: {future.exception()}")

    return future.result()


  def _call(self, client, request):
    client.wait_for_service()
    future = client.call_async(request)
    return self._wait_future(future)


  def _call_once(self, srv_type, service_name, request):
    client = self.node.create_client(srv_type, service_name)

    try:
      result = self._call(client, request)
    finally:
      self.node.destroy_client(client)

    return result


  def test_execute(self,component_ref):
    self.component_ref = component_ref
    print(f"test_execute {component_ref}")
    time.sleep(3)
    return 'succeeded'


  def connect(self,connect):
    print("connect_engine")

    request = SystemInterface.Request()
    request.connect = connect

    result = self._call(self.connect_client, request)

    return result.returncode_t


  def disconnect(self, connect):
    print("connect_engine")

    request = SystemInterface.Request()
    request.connect = connect

    result = self._call(self.disconnect_client, request)

    if result.returncode_t == "OK":
      return "succeeded"
    else:
      return "retry"


  def bind_any(self,component_ref):
    request = BindAny.Request()
    request.component_ref = component_ref

    bind = self._call(self.bind_client, request)

    return bind.returncode_t


  def release(self, component_ref):
    request = Release.Request()
    request.component_ref = component_ref

    release = self._call(self.release_client, request)

    return release.returncode_t


  def subscribe(self, event_type):
    request = Subscribe.Request()
    request.event_type = event_type

    subscribe = self._call(self.subscribe_client, request)

    return subscribe


  def get_parameter(self, component_ref):
    if component_ref == "Move":
      get_name =  '/get_parameter/' + component_ref

      request = MoveGetParameter.Request()
      request.component_ref = component_ref

      return self._call_once(
        MoveGetParameter,
        get_name,
        request
      )

    elif component_ref == "Speech_Synthesis":
      get_name =  '/get_parameter/' + component_ref

      request = SpeechGetParameter.Request()
      request.component_ref = component_ref

      return self._call_once(
        SpeechGetParameter,
        get_name,
        request
      )

    elif component_ref == "Approach":
      get_name = '/get_parameter/' + component_ref

      request = ApproachGetParameter.Request()
      request.component_ref = component_ref

      return self._call_once(
        ApproachGetParameter,
        get_name,
        request
      )


  def set_parameter(self, component_ref, parameters):
    if component_ref == "Move":
      set_name =  '/set_parameter/' + component_ref

      request = MoveSetParameter.Request()
      request.component_ref = component_ref

      # 既存scenario形式を変更しない
      # parameters = [line, curve] をそのまま使用
      request.line = list(parameters[0])
      request.curve = list(parameters[1])

      # 共通srvには time があるため、既存scenarioに指定がなければ0
      if len(parameters) >= 3:
        request.time = int(parameters[2])
      else:
        request.time = 0

      result = self._call_once(
        MoveSetParameter,
        set_name,
        request
      )


    elif component_ref == "Speech_Synthesis":
      set_name =  '/set_parameter/' + component_ref

      request = SpeechSetParameter.Request()
      request.component_ref = component_ref
      request.speech_text = parameters

      result = self._call_once(
        SpeechSetParameter,
        set_name,
        request
      )

      print(result.returncode_t)

    ###
    elif component_ref == "Approach":
      set_name =  '/set_parameter/' + component_ref

      request = ApproachSetParameter.Request()
      request.component_ref = component_ref
      request.approach_command = parameters

      result = self._call_once(
        ApproachSetParameter,
        set_name,
        request
      )
    ###

      print(result.returncode_t)

    elif component_ref == "Object_Grasping":
      set_name = '/set_parameter/' + component_ref

      request = ObjectGraspingSetParameter.Request()
      request.object_id = str(parameters[0])
      request.grasp_force = float(parameters[1])

      result = self._call_once(
        ObjectGraspingSetParameter,
        set_name,
        request
      )

      # MainEngine側の実装差を吸収して返り値を表示
      if hasattr(result, "returncode_t"):
        print(result.returncode_t)
      elif hasattr(result, "set_return"):
        print(result.set_return)

    return


  def execute(self, command_unit_list):
    """サービスで移動開始を要求する"""
    try:
      request = Execute.Request()
      request.command_unit_list = command_unit_list

      response = self._call(
        self.service_client,
        request
      )

      print(response)

      if response.return_t == "OK":
        self.node.get_logger().info("コマンドを開始しました。アクションで進捗を確認します。")

        return response.return_t
      else:
        self.node.get_logger().warning("コマンドの開始に失敗しました。")

    except Exception as e:
      self.node.get_logger().error(f"サービス呼び出しに失敗しました: {e}")


  def monitor_progress(self):
    self.node.get_logger().info("待機中...")

    result_holder = {'msg': None}

    def callback(msg):
      result_holder['msg'] = msg

    sub = self.node.create_subscription(
      Completed,
      '/completed',
      callback,
      10
    )

    try:
      while rclpy.ok() and result_holder['msg'] is None:
        rclpy.spin_once(self.node, timeout_sec=0.1)

      result = result_holder['msg']

    finally:
      self.node.destroy_subscription(sub)

    self.node.get_logger().info(f"Received message: {result.command_id}")
    self.node.get_logger().info(f"Received message: {result.status}")


  def monitor_event(self):
    self.node.get_logger().info("待機中...")

    result_holder = {'msg': None}

    def callback(msg):
      result_holder['msg'] = msg

    sub = self.node.create_subscription(
      Notifyevent,
      '/notify_event',
      callback,
      10
    )

    try:
      while rclpy.ok() and result_holder['msg'] is None:
        rclpy.spin_once(self.node, timeout_sec=0.1)

      result = result_holder['msg']

    finally:
      self.node.destroy_subscription(sub)

    self.node.get_logger().info(f"Received message: {result.event_id}")
    self.node.get_logger().info(f"Received message: {result.event_type}")
    self.node.get_logger().info(f"Received message: {result.subscribe_id}")

    return result.event_id


  def unsubscribe(self, subscribe_id):
    request = Unsubscribe.Request()
    request.subscribe_id = subscribe_id

    result = self._call_once(
      Unsubscribe,
      '/unsubscribe',
      request
    )

    return result



  def get_command_result(self, command_id):
    request = GetCommandResult.Request()
    request.command_id = command_id
    request.condition = ""

    result = self._call_once(
      GetCommandResult,
      '/get_command_result',
      request
    )

    return result


  def get_event_detail(self, event_id):
    print(event_id)

    if "recog" in  event_id:
      request = GetEventDetailSpeechRecognized.Request()
      request.event_id = event_id

      event_result = self._call_once(
        GetEventDetailSpeechRecognized,
        '/recognized_event_detail',
        request
      )

    elif "detected" in event_id:
      request = GetEventDetailPersonDetected.Request()
      request.event_id = event_id

      event_result = self._call_once(
        GetEventDetailPersonDetected,
        '/detected_event_detail',
        request
      )

    elif "local" in event_id:
      request = GetEventDetailPersonLocalized.Request()
      request.event_id = event_id

      event_result = self._call_once(
        GetEventDetailPersonLocalized,
        '/local_event_detail',
        request
      )

    elif "ident" in event_id:
      request = GetEventDetailPersonIdentified.Request()
      request.event_id = event_id

      event_result = self._call_once(
        GetEventDetailPersonIdentified,
        '/identified_event_detail',
        request
      )

    return event_result



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


def object_grasping(parameters):
    component_ref = "Object_Grasping"
    print(component_ref)
    rois.bind_any(component_ref)

    rois.set_parameter(component_ref, parameters)
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def object_release():
    component_ref = "Object_Release"
    print(component_ref)
    rois.bind_any(component_ref)

    # Object_Release はコンポーネント固有パラメータなし
    rois.execute("start")
    result = rois.monitor_progress()
    rois.release(component_ref)
    return result


def judgement(input_response):
  request = Chat.Request()
  request.input_text = input_response

  result = rois._call_once(
    Chat,
    "/chat_service",
    request
  )

  print(result.response_text)

  request = Decision.Request()
  request.input_text = result.response_text

  judge = rois._call_once(
    Decision,
    "/check_service",
    request
  )

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
    time.sleep(1)
    touch("Touch")
    time.sleep(1)

    leave("Leave")



def main():

    rois.connect("connect")

    speech_bind("Speech_Synthesis")
    speech_bind("Speech_Recognition")



    print(person_detect())###
    time.sleep(1)

    speech("hello")###

    # print("recognition greeting")
    # response = recognize_response("japanese")###
    # print(response)

    person_id = patient_identify()###
    print(person_id)###

    time.sleep(1)

    print(person_localize())
    time.sleep(1)

    move_forward([[200, 0],[0, 0]])
    time.sleep(3)

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

    time.sleep(1)

    approach("approach1")###

    time.sleep(1)

    speech("check")

    time.sleep(1)

    approach("approach2")###

    time.sleep(1)

    approach("approach3")###

    # touch()###

    time.sleep(1)

    speech("thank")

    time.sleep(1)

    leave()
    time.sleep(1)




    speech("ask1")
    time.sleep(1)

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
        task_arg = task.get('arg', '')
        task_list.append((task_name, task_arg))


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

          time.sleep(2)###

        elif task_name == "Object_Grasping":
          object_grasping(task_arg)
          time.sleep(1)

        elif task_name == "Object_Release":
          object_release()
          time.sleep(1)

        elif task_name == "Move":
          move_forward(task_arg)
          # シミュレーション時のreturn OKが早いため
          time.sleep(3)###


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
          time.sleep(1)###

        elif task_name == "Touch":
          touch()
          time.sleep(4)###

        elif task_name == "Leave":
          leave()
          time.sleep(1)###



    print(task_list)

    # # 機能名と引数を抽出
    # functions, launch_files = extract_function_and_parameters(scenario)

    # print(data)


if __name__ == '__main__':
  rclpy.init()

  try:
    rois = ROIS_METHOD()

    user_input = input("選択してください: A.シナリオ,  B.デフォルト >>> ")
    print(user_input)

    if user_input == "A" or user_input == "a":
      # scenario_file = input("シナリオ名を入力してください: ")
      scenario_ = os.environ['HOME'] + "/RTSI_FW/scenario.yaml"
      # scenario_ = os.environ['HOME'] + "/RTSUI_FW/scenario.yaml"
      # scenario_ = os.environ['HOME'] + "/RTSI_FWasanbonWeb_master/scenario.yaml"
      # scenario_ = os.environ['HOME'] + "/rtsi_fw/scenario.yaml"
      scenario(scenario_)

    elif user_input == "B" or user_input == "b":
      main()

    else:
      print("finish")

  except KeyboardInterrupt:
    rois.node.get_logger().info("クライアントが中断されました。")

  finally:
    if 'rois' in globals():
      rois.node.destroy_node()

    if rclpy.ok():
      rclpy.shutdown()
