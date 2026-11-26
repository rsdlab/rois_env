# rois_env

## 概要

`rois_env` とは，Robotic Interaction Service Framework (RTSI-FW) に必要な，サービスアプリケーション，メッセージやサービスの定義ファイル等をまとめたパッケージである．

ROS 1使用時は rois_env_ros1，ROS 2使用時は rois_env_ros2を利用する．


## パッケージ構成

| パッケージ | 概要 |
| --- | --- |
| `rois_env_ros1` | ROS 1環境用 |
| `rois_env_ros2` | ROS 2環境用 |


## インストール手順

### ROS 1

catkinワークスペースにリポジトリ内のrois_env_ros1のみをクローン，ビルドする．

```bash
cd ~/catkin_ws/src
git clone -b ros1-ros2 --single-branch --sparse https://github.com/rsdlab/rois_env.git
git -C rois_env sparse-checkout set rois_env_ros1

cd ~/catkin_ws
catkin build rois_env_ros1
source devel/setup.bash
```

### ROS 2

colconワークスペースにリポジトリ内のrois_env_ros2のみをクローン，ビルドする．

```bash
cd ~/colcon_ws/src
git clone -b ros1-ros2 --single-branch --sparse https://github.com/rsdlab/rois_env.git
git -C rois_env sparse-checkout set rois_env_ros2

cd ~/colcon_ws
colcon build --packages-select rois_env_ros2 --symlink-install
source install/setup.bash
```


## 関連リポジトリ

- [RTSI_FW](https://github.com/rsdlab/RTSI_FW)
  - 異種サービスロボットを運用するためのフレームワーク
- [common_hri](https://github.com/rsdlab/common_hri)
  - HRI EngineおよびHRI Componentの共通実装
