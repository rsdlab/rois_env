cmake_minimum_required(VERSION 3.0.2)
project(rois_env_ros1)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  actionlib_msgs
  message_generation
)

# Messages
add_message_files(
  FILES
  Completed.msg
  Notifyevent.msg
  NotifyIdentified.msg
  NotifyLocalrec.msg
  NotifyPersondetect.msg
  NotifySpeechrec.msg
  NavigationTarget.msg
)

# Services
add_service_files(
  FILES
  ApproachAction.srv
  ApproachGetParam.srv
  ApproachGetParameter.srv
  ApproachSetParam.srv
  ApproachSetParameter.srv
  BindAny.srv
  Chat.srv
  ComponentStatus.srv
  Decision.srv
  Detection.srv
  Execute.srv
  GetCommandResult.srv
  GetEventDetail.srv
  GetEventDetailPersonDetected.srv
  GetEventDetailPersonIdentified.srv
  GetEventDetailPersonLocalized.srv
  GetEventDetailSpeechRecognized.srv
  GetPosition.srv
  JudgeParam.srv
  MoveAction.srv
  MoveGetParam.srv
  MoveGetParameter.srv
  MoveSetParam.srv
  MoveSetParameter.srv
  NavigationAction.srv
  NaviGetParam.srv
  NaviGetParameter.srv
  NaviSetParam.srv
  NaviSetParameter.srv
  ObjectGraspingAction.srv
  ObjectGraspingSetParam.srv
  ObjectGraspingSetParameter.srv
  ObjectGraspingGetParam.srv
  ObjectGraspingGetParameter.srv
  RecognitionTrigger.srv
  Release.srv
  RobotAction.srv
  SpeechAction.srv
  SpeechGetParam.srv
  SpeechGetParameter.srv
  SpeechSetParam.srv
  SpeechSetParameter.srv
  SpeechTrigger.srv
  SpeechRecognitionAction.srv
  SpeechRecognitionGetParam.srv
  SpeechRecognitionGetParameter.srv
  SpeechRecognitionSetParam.srv
  SpeechRecognitionSetParameter.srv
  Subscribe.srv
  SubscribeSet.srv
  SystemInterface.srv
  Unsubscribe.srv
)

# Actions
add_action_files(
  FILES
  Execute.action
)

generate_messages(
  DEPENDENCIES
  std_msgs
  actionlib_msgs
)

catkin_package(
  CATKIN_DEPENDS
    rospy
    std_msgs
    actionlib_msgs
    message_runtime
)

catkin_install_python(
  PROGRAMS
    script/service_app_ros1.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
