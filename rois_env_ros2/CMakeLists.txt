cmake_minimum_required(VERSION 3.8)
project(rois_env_ros2)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  # Messages
  "msg/Completed.msg"
  "msg/Notifyevent.msg"
  "msg/NotifyIdentified.msg"
  "msg/NotifyLocalrec.msg"
  "msg/NotifyPersondetect.msg"
  "msg/NotifySpeechrec.msg"
  "msg/NavigationTarget.msg"

  # Services
  "srv/ApproachAction.srv"
  "srv/ApproachGetParam.srv"
  "srv/ApproachGetParameter.srv"
  "srv/ApproachSetParam.srv"
  "srv/ApproachSetParameter.srv"
  "srv/BindAny.srv"
  "srv/Chat.srv"
  "srv/ComponentStatus.srv"
  "srv/Decision.srv"
  "srv/Detection.srv"
  "srv/Execute.srv"
  "srv/GetCommandResult.srv"
  "srv/GetEventDetail.srv"
  "srv/GetEventDetailPersonDetected.srv"
  "srv/GetEventDetailPersonIdentified.srv"
  "srv/GetEventDetailPersonLocalized.srv"
  "srv/GetEventDetailSpeechRecognized.srv"
  "srv/GetPosition.srv"
  "srv/JudgeParam.srv"
  "srv/MoveAction.srv"
  "srv/MoveGetParam.srv"
  "srv/MoveGetParameter.srv"
  "srv/MoveSetParam.srv"
  "srv/MoveSetParameter.srv"
  "srv/NavigationAction.srv"
  "srv/NaviGetParam.srv"
  "srv/NaviGetParameter.srv"
  "srv/NaviSetParam.srv"
  "srv/NaviSetParameter.srv"
  "srv/ObjectGraspingAction.srv"
  "srv/ObjectGraspingSetParam.srv"
  "srv/ObjectGraspingSetParameter.srv"
  "srv/ObjectGraspingGetParam.srv"
  "srv/ObjectGraspingGetParameter.srv"
  "srv/RecognitionTrigger.srv"
  "srv/Release.srv"
  "srv/RobotAction.srv"
  "srv/SpeechAction.srv"
  "srv/SpeechGetParam.srv"
  "srv/SpeechGetParameter.srv"
  "srv/SpeechSetParam.srv"
  "srv/SpeechSetParameter.srv"
  "srv/SpeechTrigger.srv"
  "srv/SpeechRecognitionAction.srv"
  "srv/SpeechRecognitionGetParam.srv"
  "srv/SpeechRecognitionGetParameter.srv"
  "srv/SpeechRecognitionSetParam.srv"
  "srv/SpeechRecognitionSetParameter.srv"
  "srv/Subscribe.srv"
  "srv/SubscribeSet.srv"
  "srv/SystemInterface.srv"
  "srv/Unsubscribe.srv"

  # Actions
  "action/Execute.action"
)


install(PROGRAMS
  script/service_app_ros2.py
  DESTINATION lib/${PROJECT_NAME}
)


ament_export_dependencies(rosidl_default_runtime)

ament_package()
