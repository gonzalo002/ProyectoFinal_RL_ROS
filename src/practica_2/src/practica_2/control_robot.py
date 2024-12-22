#!/usr/bin/python3

import sys
import rospy
from moveit_commander import MoveGroupCommander, RobotCommander, roscpp_initialize, PlanningSceneInterface
from std_msgs.msg import String, Float32, Int8
from geometry_msgs.msg import Pose, PoseStamped
import yaml

class ControlRobot():
    def __init__(self, group_name:str = 'robot') -> None:
        roscpp_initialize(sys.argv)
        rospy.init_node("control_robot", anonymous=True)
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        self.group_name = group_name
        self.move_group = MoveGroupCommander(self.group_name)
        self.add_floor()

        self.publisher = rospy.Publisher('control_movimiento', Int8, queue_size=10)

    def get_joint_angles(self) -> list:
        return self.move_group.get_current_joint_values()
    
    def get_pose(self) -> Pose:
        return self.move_group.get_current_pose().pose
    
    def set_joint_angles(self, joint_goal: list, wait: bool = True) -> bool:
        return self.move_group.go(joint_goal, wait=wait)
    
    def set_pose(self, pose_goal: Pose, wait: bool = True) -> bool:
        self.move_group.set_pose_target(pose_goal)
        return self.move_group.go(wait=wait)
    
    def set_joint_trajectory(self, trajectory:list = []) -> bool:
        for i in range(len(trajectory)):
            state = self.set_joint_angles(trajectory[i])
            rospy.loginfo(f'Punto {i} alcanzado \n')
            if not state: print('Trayectoria Fallida'); return False
        rospy.loginfo('Trayectoria Finalizada')
        return state
    
    def set_pose_trajectory(self, trajectory:list = []) -> bool:
        for i in range(len(trajectory)):
            state = self.set_pose(trajectory[i])
            rospy.loginfo(f'Punto {i} alcanzado \n')
            if not state: print('Trayectoria Fallida'); return False
        rospy.loginfo('Trayectoria Finalizada')
        return state
    
    def set_carthesian_path(self, waypoints:list = [], eef_step:Float32 = 0.01, avoid_collisions:bool = True ,wait:bool = True) -> bool:
        if eef_step == 0.0:
            eef_step = 0.01
            print('eef_step modificado a valor 0.01 por requisitos de funcionamiento')
            
        waypoints.insert(0, self.get_pose())

        (plan, fraction) = self.move_group.compute_cartesian_path(waypoints, eef_step = eef_step, avoid_collisions= avoid_collisions)
        

        if fraction != 1.0:
            rospy.logwarn('Trayectoria Inalcanzable')
            rospy.loginfo(f'Porcentaje de la trayectoria alcanzable: {fraction*100:.2f}%')
            return False
        else: 
            rospy.loginfo('Ejecutando Trayectoria')
            message = Int8(1)
            self.publisher.publish(message)
            #sleep(1)
            result = self.move_group.execute(plan, wait=wait)
            message = Int8(0)
            self.publisher.publish(message)
            return result
        
    def set_box_obstacle(self, box_name:String, box_pose:Pose, size:tuple = (.1, .1, .1)) -> None:
        box_pose_stamped = PoseStamped()
        box_pose_stamped.header.frame_id = "base_link"
        box_pose_stamped.pose = box_pose
        self.scene.add_box(box_name, box_pose_stamped, size=size)

    def add_floor(self) -> None:
        pose_suelo = Pose()
        pose_suelo.position.z -= .03
        self.set_box_obstacle('floor', pose_suelo, (2,2,.05))

    def create_pose(self, pos_list:list, ori_list) -> Pose:
        if len(pos_list) != 3 or len(ori_list) != 4: return False
        pose = Pose()
        pose.position.x = pos_list[0]
        pose.position.y = pos_list[1]
        pose.position.z = pos_list[2]
        pose.orientation.x = ori_list[0]
        pose.orientation.y = ori_list[1]
        pose.orientation.z = ori_list[2]
        pose.orientation.w = ori_list[3]

        return pose
    
    def save_in_yaml(self, doc_name:str, key_name:str, data:list) -> None:
        diccionario_configuraciones = {key_name:data}
        with open(doc_name, '+a') as f:
            yaml.dump(diccionario_configuraciones, f)
    
    def get_point_from_yaml(self, doc_name:str, key_name:str) -> list:
        with open(doc_name, '+r') as f:
            configuraciones =  yaml.load(f, yaml.Loader)

        return configuraciones[key_name]

    def get_trayectory_from_yaml(self, doc_name:str) -> list:
        with open(doc_name, '+r') as f:
            configuraciones =  yaml.load(f, yaml.Loader)

        trayectoria = []
        for nombre_punto in list(configuraciones.keys()):
            trayectoria.append(configuraciones[nombre_punto])

        return trayectoria
    
    def get_dict_trayectory_from_yaml(self, doc_name:str) -> dict:
        with open(doc_name, '+r') as f:
            configuraciones =  yaml.load(f, yaml.Loader)

        return configuraciones


if __name__ == '__main__':

    control = ControlRobot('robot')

    print("------------------------------------------")
    print(" ¿Qué trayectoria quieres hacer?")
    print("      1. Semicircular")
    print("      2. Rectángulo")
    print("      3. Línea Recta")
    print()
    print(" Para salir cualquier otro número o tecla.")
    print("------------------------------------------")
    
    while True:
        trayectoria = input("\n Trayectoria: ")

        # Comprobar la entrada del usuario
        try:
            trayectoria = int(trayectoria)
        except:
            quit()
            
        # Cambiar el numero por el título de la trayectoria
        if trayectoria == 1:
            nombre_trayectoria = "Semicirculo"
            
        elif trayectoria == 2:
            nombre_trayectoria = "Rectangulo"
            
        elif trayectoria == 3:
            nombre_trayectoria = "LineaRecta"
            
        else:
            exit()

        # Importamos las trayectorias y el estado de los motores
        poses_trayectory = control.get_trayectory_from_yaml(f"./src/practica_2/src/practica_2/trayectorias/Trayectoria_{nombre_trayectoria}.yaml")
        joint_trayectory = control.get_dict_trayectory_from_yaml(f"./src/practica_2/src/practica_2/trayectorias/JointStates_{nombre_trayectoria}.yaml")

        # Ejecutamos el movimiento
        control.set_joint_angles(joint_trayectory["Inicio"])
        control.set_carthesian_path(poses_trayectory)
        control.set_joint_angles(joint_trayectory["Fin"])