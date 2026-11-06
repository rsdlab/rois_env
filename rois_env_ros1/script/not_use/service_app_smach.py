#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import smach
import smach_ros
from rois_env_ros1.srv import *
from rois_env_ros1.msg import *

# ============== ROIS_METHOD ==================
class ROIS_METHOD:
    def __init__(self):
        self.connect_ = rospy.ServiceProxy('/connect', system_interface)
        rospy.wait_for_service('/connect')
        self.bind = rospy.ServiceProxy('/bind_any', bind_any)
        self.release = rospy.ServiceProxy('/release', release)
        self.service_client = rospy.ServiceProxy('/execute', execute)

    # 以下サービスのラッパ関数（実機用にあとで修正可）
    def connect(self):
        return self.connect_("connect")

    def detect(self):
        component_ref = "Person_Detection"
        self.bind(component_ref)
        self.service_client("start")
        rospy.sleep(1)
        self.release(component_ref)
        return 1  # デモ用: 検出人数

    def speech(self, text):
        component_ref = "Speech_Synthesis"
        self.bind(component_ref)
        self.service_client("start")  # 実際はset_parameterなど入れる
        rospy.loginfo(f"Speech: {text}")
        rospy.sleep(1)
        self.release(component_ref)

    def identify(self):
        component_ref = "Person_Identification"
        self.bind(component_ref)
        self.service_client("start")
        rospy.sleep(1)
        self.release(component_ref)
        return "Person1"  # デモ用

    def localize(self):
        component_ref = "Person_Localization"
        self.bind(component_ref)
        self.service_client("start")
        rospy.sleep(1)
        self.release(component_ref)

    def approach(self, command):
        component_ref = "Approach"
        self.bind(component_ref)
        self.service_client("start")
        rospy.sleep(1)
        self.release(component_ref)

    def leave(self):
        component_ref = "Leave"
        self.bind(component_ref)
        self.service_client("start")
        rospy.sleep(1)
        self.release(component_ref)


rois = None  # グローバルインスタンス

# ============== 共通SafeState ==================
class SafeState(smach.State):
    def __init__(self, outcomes):
        super(SafeState, self).__init__(outcomes=outcomes)

    def check_preempt(self):
        if self.preempt_requested():
            self.service_preempt()
            rospy.logwarn("Preempt要求を受信。中断します。")
            return True
        return False

# ============== 各ステート実装 ================

class ConnectState(SafeState):
    def __init__(self):
        super(ConnectState, self).__init__(['succeeded', 'failed', 'preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            result = rois.connect()
            if result.returncode_t == "OK":
                return 'succeeded'
            else:
                return 'failed'
        except rospy.ServiceException as e:
            rospy.logerr(f"Connect error: {e}")
            return 'failed'


class PersonDetectState(SafeState):
    def __init__(self):
        super(PersonDetectState, self).__init__(['detected', 'not_detected', 'preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            num = rois.detect()
            if num > 0:
                return 'detected'
            else:
                return 'not_detected'
        except rospy.ServiceException as e:
            rospy.logerr(f"Detect error: {e}")
            return 'not_detected'


class GreetingState(SafeState):
    def __init__(self):
        super(GreetingState, self).__init__(['done', 'preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            rois.speech("hello")
            return 'done'
        except rospy.ServiceException as e:
            rospy.logerr(f"Greeting error: {e}")
            return 'done'


class IdentifyState(SafeState):
    def __init__(self):
        super(IdentifyState, self).__init__(['person1','person5','person6','unknown','preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            person_id = rois.identify()
            rospy.loginfo(f"Identified: {person_id}")
            if person_id == "Person1":
                return 'person1'
            elif person_id == "Person5":
                return 'person5'
            elif person_id == "Person6":
                return 'person6'
            else:
                return 'unknown'
        except rospy.ServiceException as e:
            rospy.logerr(f"Identify error: {e}")
            return 'unknown'


class SpeakPersonSpecificState(SafeState):
    def __init__(self, text):
        super(SpeakPersonSpecificState, self).__init__(['done', 'preempted'])
        self.text = text

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            rois.speech(self.text)
            return 'done'
        except rospy.ServiceException as e:
            rospy.logerr(f"Speech error: {e}")
            return 'done'


class LocalizeState(SafeState):
    def __init__(self):
        super(LocalizeState, self).__init__(['localized', 'preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            rois.localize()
            return 'localized'
        except rospy.ServiceException as e:
            rospy.logerr(f"Localize error: {e}")
            return 'localized'


class ApproachState(SafeState):
    def __init__(self, command):
        super(ApproachState, self).__init__(['done', 'preempted'])
        self.command = command

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            rois.approach(self.command)
            return 'done'
        except rospy.ServiceException as e:
            rospy.logerr(f"Approach error: {e}")
            return 'done'


class LeaveState(SafeState):
    def __init__(self):
        super(LeaveState, self).__init__(['done', 'preempted'])

    def execute(self, userdata):
        if self.check_preempt(): return 'preempted'
        try:
            rois.leave()
            return 'done'
        except rospy.ServiceException as e:
            rospy.logerr(f"Leave error: {e}")
            return 'done'


# ============== StateMachine本体 ================
def main():
    global rois
    rospy.init_node('smach_rois_node')
    rois = ROIS_METHOD()

    sm = smach.StateMachine(outcomes=['END', 'ERROR', 'PREEMPTED'])

    with sm:
        smach.StateMachine.add('CONNECT', ConnectState(),
                                transitions={'succeeded':'PERSON_DETECT', 'failed':'ERROR','preempted':'PREEMPTED'})
        smach.StateMachine.add('PERSON_DETECT', PersonDetectState(),
                                transitions={'detected':'GREETING','not_detected':'END','preempted':'PREEMPTED'})
        smach.StateMachine.add('GREETING', GreetingState(),
                                # transitions={'done':'IDENTIFY','preempted':'PREEMPTED'})
                                transitions={'done':'MEASURE5','preempted':'PREEMPTED'})
        # smach.StateMachine.add('IDENTIFY', IdentifyState(),
        #                         transitions={'person1':'MEASURE3','person5':'MEASURE4','person6':'MEASURE5','unknown':'END','preempted':'PREEMPTED'})
        smach.StateMachine.add('MEASURE3', SpeakPersonSpecificState('measure3'), transitions={'done':'LOCALIZE','preempted':'PREEMPTED'})
        smach.StateMachine.add('MEASURE4', SpeakPersonSpecificState('measure4'), transitions={'done':'LOCALIZE','preempted':'PREEMPTED'})
        smach.StateMachine.add('MEASURE5', SpeakPersonSpecificState('measure5'), transitions={'done':'LOCALIZE','preempted':'PREEMPTED'})
        smach.StateMachine.add('LOCALIZE', LocalizeState(), transitions={'localized':'APPROACH1','preempted':'PREEMPTED'})
        smach.StateMachine.add('APPROACH1', ApproachState('approach1'), transitions={'done':'APPROACH2','preempted':'PREEMPTED'})
        smach.StateMachine.add('APPROACH2', ApproachState('approach2'), transitions={'done':'APPROACH3','preempted':'PREEMPTED'})
        smach.StateMachine.add('APPROACH3', ApproachState('approach3'), transitions={'done':'LEAVE','preempted':'PREEMPTED'})
        smach.StateMachine.add('LEAVE', LeaveState(), transitions={'done':'END','preempted':'PREEMPTED'})

    # SMACH Viewer用サーバ起動
    sis = smach_ros.IntrospectionServer('rois_state_machine', sm, '/SM_ROOT')
    sis.start()

    outcome = sm.execute()

    rospy.spin()
    sis.stop()

if __name__ == '__main__':
    main()