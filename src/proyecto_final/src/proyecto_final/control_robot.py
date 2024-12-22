#!/usr/bin/python3

import sys, os
from copy import deepcopy
import rospy
from math import pi
from moveit_commander import MoveGroupCommander, RobotCommander, roscpp_initialize, PlanningSceneInterface
from control_msgs.msg import GripperCommandAction, GripperCommandGoal, GripperCommandResult
from std_msgs.msg import String, Float32, Bool
from moveit_commander.conversions import list_to_pose
from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion
from sensor_msgs.msg import JointState
import yaml
from actionlib import SimpleActionClient
from proyecto_final.funciones_auxiliares import crear_mensaje

class ControlRobot:
    def __init__(self, group_name:str = 'robot', train_env:bool = False) -> None:
        roscpp_initialize(sys.argv)
        try:
            rospy.init_node("control_robot", anonymous=True) # En caso de ya existir
        except:
            pass
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        self.group_name = group_name
        self.move_group = MoveGroupCommander(self.group_name)
        self.gripper_action_client = SimpleActionClient("rg2_action_server", GripperCommandAction)
        self.SubsGripStates = rospy.Subscriber("/rg2/joint_states", JointState, self._gripper_states_callback)
        self.SubsGripEffort = rospy.Subscriber("/rg2/grip_detected", Bool, self._gripper_effort_callback)
        self.get_gripper_state = False
        self.get_gripper_effort = False
        self.name = "ControlRobot"

        self.train_env = train_env
        if train_env:
            self.move_group.set_planning_time(2)
        self.reset_planning_scene()
        self.move_group.set_num_planning_attempts(5)
    
    def get_jointstates(self) -> list:
        return self.move_group.get_current_joint_values()
    
    def get_pose(self) -> Pose:
        return self.move_group.get_current_pose().pose
    
    def move_jointstates(self, joint_goal: list, wait: bool = True) -> bool:
        return self.move_group.go(joint_goal, wait=wait)
    
    def move_pose(self, pose_goal: Pose, wait: bool = True) -> bool:
        self.move_group.set_pose_target(pose_goal)
        return self.move_group.go(wait=wait)
    
    def plan_pose(self, pose_goal:Pose) -> bool:
        self.move_group.set_num_planning_attempts(5)
        self.move_group.set_pose_target(pose_goal)
        return self.move_group.plan()
    
    def move_jointstates_trayectory(self, trajectory:list = []) -> bool:
        for i in range(len(trajectory)):
            state = self.move_jointstates(trajectory[i])
            crear_mensaje(f"Punto {i} alcanzado", "INFO", self.name)
            if not state: crear_mensaje(f"Trayectoria fallida", "ERROR", self.name); return False
        crear_mensaje(f"Trayectoria alzanzada", "SUCCESS", self.name)
        return state
    
    def move_pose_trayectory(self, trajectory:list = []) -> bool:
        for i in range(len(trajectory)):
            state = self.move_pose(trajectory[i])
            crear_mensaje(f"Punto {i} alcanzado", "INFO", self.name)
            if not state: crear_mensaje(f"Trayectoria fallida", "ERROR", self.name); return False
        crear_mensaje(f"Trayectoria alzanzada", "SUCCESS", self.name)
        return state
    
    def move_carthesian_trayectory(self, waypoints:list = [], eef_step:Float32 = 0.01, avoid_collisions:bool = True ,wait:bool = True) -> bool:
        if eef_step == 0.0:
            eef_step = 0.01
            crear_mensaje("Parámetro eef_step modificado a valor 0.01 por requisitos de funcionamiento", "INFO", self.name)
            
        waypoints.insert(0, self.get_pose())
        (plan, fraction) = self.move_group.compute_cartesian_path(waypoints, eef_step = eef_step, avoid_collisions= avoid_collisions)
        
        if fraction != 1.0:
            crear_mensaje(f"Trayectoria Inalcanzable. Porcentaje de la trayectoria alcanzable: {fraction*100:.2f}%", "WARN", self.name)
            return False
        else: 
            crear_mensaje(f"Ejecutando Trayectoria", "INFO", self.name)
            return self.move_group.execute(plan, wait=wait)
        
    def add_box_obstacle(self, box_name:String, box_pose:Pose, size:tuple = (.1, .1, .1)) -> None:
        box_pose_stamped = PoseStamped()
        box_pose_stamped.header.frame_id = "base_link"
        box_pose_stamped.pose = box_pose
        self.scene.add_box(box_name, box_pose_stamped, size=size)
        
    def reset_planning_scene(self) -> None:
        # Optionally: clear the octomap (which stores obstacles in the environment)
        self.scene.clear()
        self._generate_scene()

    def _generate_scene(self) -> None:
        pose_suelo = Pose()
        pose_suelo.position.z -= .03

        pose_vertical_support = Pose(Point(x=0,y=-0.1,z=0.5),
                                     Quaternion(x=0,y=0,z=0,w=1))
        pose_camera_support = Pose(Point(x=0.0,y=0.0,z=0.85),
                                     Quaternion(x=0,y=0,z=0,w=1))
        
        self.add_box_obstacle('floor', pose_suelo, (2,2,.05))
        self.add_box_obstacle('vertical_support', pose_vertical_support, (0.05,0.05,1.0))
        self.add_box_obstacle('camera_support', pose_camera_support, (0.1,1.0,.05))

    def list_to_pose(self, pos_list:list, ori_list) -> Pose:
        if len(pos_list) != 3 or len(ori_list) != 4: return False
        return list_to_pose(pose_list=pos_list)
    
    def save_in_yaml(self, doc_name:str, key_name:str, data:list, delete_info:bool=False) -> None:
        diccionario_configuraciones = {key_name:data}
        if delete_info:
            mode = '+w'
        else:
            mode = '+a'
        with open(doc_name, mode) as f:
            yaml.dump(diccionario_configuraciones, f)
    
    def read_from_yaml(self, doc_name:str, key_name:str) -> list:
        with open(doc_name, '+r') as f:
            configuraciones =  yaml.load(f, yaml.Loader)

        return configuraciones[key_name]
    
    def _gripper_states_callback(self, data:JointState) -> float:
        if self.get_gripper_state:
            self.gripper_joint_state = deepcopy(self._rad_to_width(data.position[0]))
            self.get_gripper_state = False
    
    def _gripper_effort_callback(self, data:Bool) -> float:
        if self.get_gripper_effort:
            self.gripper_effort_state = deepcopy(data.data)
            self.get_gripper_effort = False
    
    def _rad_to_width(self, data:float = 0.0) -> None:
        return data * pi / 180
    
    def move_gripper(self, gripper_width: float, max_effort: float, sleep_before:float = 0.4, sleep_after:float = 0.2) -> bool:
        goal = GripperCommandGoal()
        goal.command.position = gripper_width
        goal.command.max_effort = max_effort
        
        rospy.sleep(sleep_before)
        self.gripper_action_client.send_goal(goal)
        self.gripper_action_client.wait_for_result()
        result = self.gripper_action_client.get_result()

        rospy.sleep(sleep_after)
        
        return result.reached_goal
    
    def get_pinza_state(self) -> list:
        self.get_gripper_state = True
        self.get_gripper_effort = True

        
        while self.get_gripper_state or self.get_gripper_effort:
            rospy.sleep(0.1)

        return self.gripper_joint_state, self.gripper_effort_state




if __name__ == '__main__':
    control = ControlRobot('robot')
    file_path = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:os.path.dirname(os.path.abspath(__file__)).split('/').index('proyecto_final')+1])
    
    #control.move_jointstates(control.read_from_yaml(f'{file_path}/data/trayectorias/master_points', 'P_MATRIX_ORIGIN'))
    control.save_in_yaml(f'{file_path}/data/trayectorias/master_positions', 'J_DISCARD_ORIGIN', control.get_jointstates())
    
    #trayectoria=[]
    #punto = control.get_pose()
    #print('Punto inicial de la trayectoria')
    #print(punto)
    #trayectoria.append(copy.deepcopy(punto))
    #punto.position.x -= 0.01
    #trayectoria.append(copy.deepcopy(punto))
    #punto.position.y -= 0.1
    #trayectoria.append(copy.deepcopy(punto))
    #print('Punto final de la trayectoria')
    #print(punto)
    ##control.set_pose_trajectory(trayectoria_pose)
    ##control.set_joint_trajectory(trayectoria_joint)
    #if not control.set_carthesian_path(trayectoria, eef_step=0.01):
    #    pass
    #else:
    #    punto = control.get_pose()
    #    print('Posición Alcanzada')
    #    print(punto)
    

# Funcion que cree un array de Poses
# Terminar funcion de trayectoria cartesiana
# Funcion que cree un JointTarget
# ,,.