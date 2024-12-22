#!/usr/bin/python3

from control_robot import ControlRobot
import rospy
from geometry_msgs.msg import Pose, PoseStamped, PoseArray

class EjecuciónRobot:
    def __init__(self) -> None:
        self.robot = ControlRobot('robot')
          
    def move_home(self) -> bool:
        pose_home = self.robot.get_from_yaml('puntos_trayectoria', 'home')
        success = self.robot.set_pose(pose_home)
        
        if success == True:
            rospy.loginfo('Posición Home alcanzada')
        else:
            rospy.logwarn('Posición Home inalcanzable')
        return success
    
    def trayectoria_agarre(self, pose_cubos:PoseArray = [], num_cubos:int=0):
        for pose in pose_cubos.poses:
            trayectoria = []
            trayectoria.append(self.robot.get_from_yaml('puntos_trayectoria', 'home'))
            trayectoria.append(pose)
            self.robot.set_carthesian_path(trayectoria)