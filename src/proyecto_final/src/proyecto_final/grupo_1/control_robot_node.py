#!/usr/bin/env python3
import sys
import copy
import rospy
import moveit_commander
from std_msgs.msg import Int32
from typing import List
from geometry_msgs.msg import Pose, PoseStamped
from moveit_commander import RobotCommander, MoveGroupCommander, PlanningSceneInterface
from mi_robot_pkg.msg import HandData

class ControlRobot:
    def __init__(self) -> None:
        moveit_commander.roscpp_initialize(sys.argv)
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        self.group_name = "robot"
        self.move_group = MoveGroupCommander(self.group_name)
        self.add_floor()

    def get_motor_angles(self) -> List[float]:
        return self.move_group.get_current_state().joint_state.position

    def move_motors(self, joint_goal: List[float], wait: bool=True) -> bool:
        return self.move_group.go(joint_goal, wait=wait)

    def get_pose(self) -> Pose:
        return self.move_group.get_current_pose().pose

    def move_to_pose(self, pose_goal: Pose, wait: bool=True) -> bool:
        self.move_group.set_pose_target(pose_goal)
        return self.move_group.go(wait=wait)

    def move_to_xyz(self, x: float, y: float, z: float, wait: bool=True) -> bool:
        current_pose = self.get_pose()
        current_pose.position.x = x
        current_pose.position.y = y
        current_pose.position.z = z
        return self.move_to_pose(current_pose, wait)

    def add_to_planning_scene(self, pose_box: Pose, name: str, size: tuple = (0.1, 0.1, 0.1)) -> None:
        box_pose = PoseStamped()
        box_pose.header.frame_id = "base_link"
        box_pose.pose = pose_box
        self.scene.add_box(name, box_pose, size=size)

    def move_trajectory(self, poses: List[Pose], wait: bool=True) -> bool:
        (plan, fraction) = self.move_group.compute_cartesian_path(poses, 0.01, 0.0)

        if fraction != 1.0:
            return False

        return self.move_group.execute(plan, wait=wait)

    def add_floor(self) -> None:
        pose_floor = Pose()
        pose_floor.position.z = -0.026
        self.add_to_planning_scene(pose_floor, "floor", (2, 2, 0.05))

control_por_mano_activado = False  # Variable global para controlar el estado

def control_callback(msg, control_robot):
    global control_por_mano_activado
    action_code = msg.data
    if action_code == 1:
        control_robot.add_floor()
        print("Se ha añadido el suelo a la escena de planificación.")
    elif action_code == 2:
        current_pose = control_robot.get_pose()
        print(f"Pose actual del robot: ")
        print(f"Posición: x={current_pose.position.x}, y={current_pose.position.y}, z={current_pose.position.z}")
        print(f"Orientación: qx={current_pose.orientation.x}, qy={current_pose.orientation.y}, qz={current_pose.orientation.z}, qw={current_pose.orientation.w}")

        print("Introduzca los valores para X, Y, Z (separados por espacios):")
        input_str = input()
        values = [float(x) for x in input_str.strip().split()]
        if len(values) != 3:
            print("Entrada inválida. Se esperaban 3 valores.")
            return
        x, y, z = values
        success = control_robot.move_to_xyz(x, y, z)
        if success:
            print(f"El robot se ha movido a la posición (X={x}, Y={y}, Z={z}) manteniendo la orientación actual.")
        else:
            print("No se pudo mover a la posición deseada.")
    elif action_code == 3:
        print("Introduzca los ángulos de las articulaciones (en radianes) separados por espacios:")
        input_str = input()
        joint_goal = [float(x) for x in input_str.strip().split()]
        success = control_robot.move_motors(joint_goal)
        if success:
            print("El robot se ha movido a la configuración objetivo.")
        else:
            print("No se pudo mover a la configuración objetivo.")
    elif action_code == 4:
        print("Introduzca el número de puntos de la trayectoria:")
        num_waypoints = int(input())
        waypoints = []
        for i in range(num_waypoints):
            print(f"Introduzca el punto {i+1} (x y z):")
            input_str = input()
            values = [float(x) for x in input_str.strip().split()]
            if len(values) != 3:
                print("Entrada inválida. Se esperaban 3 valores.")
                return
            pose = Pose()
            pose.position.x = values[0]
            pose.position.y = values[1]
            pose.position.z = values[2]
            current_pose = control_robot.get_pose()
            pose.orientation = current_pose.orientation
            waypoints.append(pose)
        success = control_robot.move_trajectory(waypoints)
        if success:
            print("El robot se ha movido a lo largo de la trayectoria.")
        else:
            print("No se pudo completar la trayectoria.")
    elif action_code == 5:
        control_por_mano_activado = True
        print("Control por detección de manos activado.")
    elif action_code == 6:
        control_por_mano_activado = False
        print("Control por detección de manos desactivado.")
    else:
        print("Código de acción inválido recibido.")

def hand_data_callback(msg, control_robot):
    global control_por_mano_activado
    if not control_por_mano_activado:
        return

    x = msg.x
    y = msg.y
    is_open = msg.is_open

    if is_open:
        # Mapear posición de la mano a coordenadas del robot
        # Ajustar según el rango de movimiento del robot
        robot_x = x * 0.001  # Escalamiento ejemplo
        robot_y = y * 0.001

        current_pose = control_robot.get_pose()
        new_pose = copy.deepcopy(current_pose)
        new_pose.position.x += robot_x
        new_pose.position.y += robot_y

        success = control_robot.move_to_pose(new_pose)
        if success:
            rospy.loginfo("El robot se ha movido basado en la posición de la mano.")
        else:
            rospy.loginfo("No se pudo mover el robot a la nueva posición.")
    else:
        rospy.loginfo("Mano cerrada; el robot no se mueve.")

def listener():
    rospy.init_node('control_robot_node', anonymous=True)
    control_robot = ControlRobot()
    rospy.Subscriber('/consignas', Int32, control_callback, callback_args=control_robot)
    rospy.Subscriber('/hand_data', HandData, hand_data_callback, callback_args=control_robot)
    rospy.spin()

if __name__ == '__main__':
    listener()