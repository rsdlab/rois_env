#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import rospy

from rois_env_ros1.srv import (
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
from rois_env_ros1.msg import Completed, Notifyevent


class ROIS_METHOD:
    def __init__(self):
        rospy.wait_for_service('/connect')
        rospy.wait_for_service('/bind_any')

        self.connect_client = rospy.ServiceProxy('/connect', SystemInterface)
        self.disconnect_client = rospy.ServiceProxy('/disconnect', SystemInterface)
        self.bind_client = rospy.ServiceProxy('/bind_any', BindAny)
        self.release_client = rospy.ServiceProxy('/release', Release)
        self.subscribe_client = rospy.ServiceProxy('/subscribe', Subscribe)
        self.service_client = rospy.ServiceProxy('/execute', Execute)
        self.arm_client = rospy.ServiceProxy('/robot_action', RobotAction)

    def test_execute(self, component_ref):
        self.component_ref = component_ref
        print(f"test_execute {component_ref}")
        rospy.sleep(3)
        return 'succeeded'

    def connect(self, connect):
        print("connect_engine")
        result = self.connect_client(connect)
        return result.returncode_t

    def disconnect(self, connect):
        print("disconnect_engine")
        result = self.disconnect_client(connect)
        if result.returncode_t == "OK":
            return "succeeded"
        return "retry"

    def bind_any(self, component_ref):
        result = self.bind_client(component_ref)
        return result.returncode_t

    def release(self, component_ref):
        result = self.release_client(component_ref)
        return result.returncode_t

    def subscribe(self, event_type):
        return self.subscribe_client(event_type)

    def unsubscribe(self, subscribe_id):
        rospy.wait_for_service('/unsubscribe')
        client = rospy.ServiceProxy('/unsubscribe', Unsubscribe)
        return client(subscribe_id)

    def get_parameter(self, component_ref):
        if component_ref == "Move":
            srv_type = MoveGetParameter
        elif component_ref == "Speech_Synthesis":
            srv_type = SpeechGetParameter
        elif component_ref == "Approach":
            srv_type = ApproachGetParameter
        else:
            raise ValueError(f"Unsupported component_ref: {component_ref}")

        service_name = '/get_parameter/' + component_ref
        rospy.wait_for_service(service_name)
        client = rospy.ServiceProxy(service_name, srv_type)
        return client(component_ref)

    def set_parameter(self, component_ref, parameters):
        service_name = '/set_parameter/' + component_ref
        rospy.wait_for_service(service_name)

        if component_ref == "Move":
            client = rospy.ServiceProxy(service_name, MoveSetParameter)
            line = list(parameters[0])
            curve = list(parameters[1])
            move_time = int(parameters[2]) if len(parameters) >= 3 else 0
            return client(
                component_ref=component_ref,
                line=line,
                curve=curve,
                time=move_time,
            )

        if component_ref == "Speech_Synthesis":
            client = rospy.ServiceProxy(service_name, SpeechSetParameter)
            result = client(
                component_ref=component_ref,
                speech_text=parameters,
            )
            print(result.returncode_t)
            return result

        if component_ref == "Approach":
            client = rospy.ServiceProxy(service_name, ApproachSetParameter)
            result = client(
                component_ref=component_ref,
                approach_command=parameters,
            )
            print(result.returncode_t)
            return result

        if component_ref == "Object_Grasping":
            if not isinstance(parameters, (list, tuple)) or len(parameters) != 2:
                raise ValueError("Object_Grasping parameters must be [object_id, grasp_force]")
            client = rospy.ServiceProxy(service_name, ObjectGraspingSetParameter)
            result = client(
                component_ref=component_ref,
                object_id=str(parameters[0]),
                grasp_force=float(parameters[1]),
            )
            if hasattr(result, "returncode_t"):
                print(result.returncode_t)
            return result

        raise ValueError(f"Unsupported component_ref: {component_ref}")

    def execute(self, command_unit_list):
        try:
            response = self.service_client(command_unit_list)
            print(response)
            if response.return_t == "OK":
                rospy.loginfo("コマンドを開始しました。アクションで進捗を確認します。")
                return response.return_t
            rospy.logwarn("コマンドの開始に失敗しました。")
            return response.return_t
        except rospy.ServiceException as e:
            rospy.logerr(f"サービス呼び出しに失敗しました: {e}")
            return None

    def monitor_progress(self):
        rospy.loginfo("待機中...")
        result = rospy.wait_for_message('/completed', Completed)
        rospy.loginfo(f"Received message: {result.command_id}")
        rospy.loginfo(f"Received message: {result.status}")
        return result

    def monitor_event(self):
        rospy.loginfo("待機中...")
        result = rospy.wait_for_message('/notify_event', Notifyevent)
        rospy.loginfo(f"Received message: {result.event_id}")
        rospy.loginfo(f"Received message: {result.event_type}")
        rospy.loginfo(f"Received message: {result.subscribe_id}")
        return result.event_id

    def get_command_result(self, command_id):
        rospy.wait_for_service('/get_command_result')
        client = rospy.ServiceProxy('/get_command_result', GetCommandResult)
        return client(command_id, "")

    def get_event_detail(self, event_id):
        print(event_id)
        if "recog" in event_id:
            service_name = '/recognized_event_detail'
            srv_type = GetEventDetailSpeechRecognized
        elif "detected" in event_id:
            service_name = '/detected_event_detail'
            srv_type = GetEventDetailPersonDetected
        elif "local" in event_id:
            service_name = '/local_event_detail'
            srv_type = GetEventDetailPersonLocalized
        elif "ident" in event_id:
            service_name = '/identified_event_detail'
            srv_type = GetEventDetailPersonIdentified
        else:
            raise ValueError(f"Unknown event_id: {event_id}")

        rospy.wait_for_service(service_name)
        client = rospy.ServiceProxy(service_name, srv_type)
        return client(event_id)


def add_item(_list, item):
    if item not in _list:
        _list.append(item)
        print(f"{item} を追加しました")
        return True
    print(f"{item} は既にリストに存在します")
    print(_list)
    return False


def speech(speech_text):
    component_ref = "Speech_Synthesis"
    print(component_ref)
    rois.bind_any(component_ref)
    rois.set_parameter(component_ref, speech_text)
    rois.execute("start")
    rois.monitor_progress()
    rois.release(component_ref)


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
    rospy.wait_for_service('/chat_service')
    chat = rospy.ServiceProxy('/chat_service', Chat)
    result = chat(input_response)
    print(result.response_text)

    rospy.wait_for_service('/check_service')
    check = rospy.ServiceProxy('/check_service', Decision)
    judge = check(result.response_text)
    return judge.response_text


def approach(approach_command):
    component_ref = "Approach"
    print(component_ref)
    rois.bind_any(component_ref)
    rois.set_parameter(component_ref, approach_command)
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
    # Object_Releaseには固有パラメータがない
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
    touch()
    rospy.sleep(1)
    leave()


def main():
    rois.connect("connect")
    speech_bind("Speech_Synthesis")
    speech_bind("Speech_Recognition")

    print(person_detect())
    rospy.sleep(1)
    speech("hello")

    person_id = patient_identify()
    print(person_id)
    rospy.sleep(1)

    print(person_localize())
    rospy.sleep(1)

    move_forward([[200, 0], [0, 0]])
    rospy.sleep(3)

    if person_id == "Person4":
        speech("measure3")
    elif person_id == "Person5":
        speech("measure4")
    elif person_id == "Person6":
        speech("measure5")

    speech("yorosiku")
    rospy.sleep(1)
    approach("approach1")
    rospy.sleep(1)
    speech("check")
    rospy.sleep(1)
    approach("approach2")
    rospy.sleep(1)
    approach("approach3")
    rospy.sleep(1)
    speech("thank")
    rospy.sleep(1)
    leave()
    rospy.sleep(1)

    speech("ask1")
    rospy.sleep(1)
    response = "良い"  # Test
    print(response)
    voice = judgement(response)
    print(voice)
    speech(voice)


def scenario(scenario_file):
    with open(scenario_file, 'r') as infile:
        data = yaml.safe_load(infile)

    scenario_data = data.get('scenario', [])
    task_list = []
    rois.connect("connect")

    for task in scenario_data:
        task_name = task.get('task', '')
        task_arg = task.get('arg', '')
        task_list.append((task_name, task_arg))

        if task_name == "Speech_Synthesis":
            print(task_arg)
            if task_arg == "identification":
                if person_id == "Person4":
                    speech("measure3")
                elif person_id == "Person5":
                    speech("measure4")
                elif person_id == "Person6":
                    speech("measure5")
            elif task_arg == "decision":
                voice = judgement(response)
                print(voice)
                speech(voice)
            else:
                speech(task_arg)
            rospy.sleep(2)

        elif task_name == "Object_Grasping":
            object_grasping(task_arg)

        elif task_name == "Object_Release":
            object_release()

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
            approach(task_arg)
            rospy.sleep(1)

        elif task_name == "Touch":
            touch()
            rospy.sleep(4)

        elif task_name == "Leave":
            leave()
            rospy.sleep(1)

    print(task_list)


if __name__ == '__main__':
    rospy.init_node('service_app_node')
    try:
        rois = ROIS_METHOD()
        user_input = input("選択してください: A.シナリオ,  B.デフォルト >>> ")
        print(user_input)

        if user_input == "A" or user_input == "a":
            scenario_ = os.environ['HOME'] + "/RTSI_FWasanbonWeb_master/scenario.yaml"
            scenario(scenario_)
        elif user_input == "B" or user_input == "b":
            main()
        else:
            print("finish")

    except rospy.ROSInterruptException:
        rospy.loginfo("クライアントが中断されました。")
