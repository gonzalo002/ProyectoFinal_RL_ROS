#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32

def order_publisher():
    pub = rospy.Publisher('/consignas', Int32, queue_size=10)
    rospy.init_node('order_node', anonymous=True)
    rate = rospy.Rate(1) # 1 Hz
    while not rospy.is_shutdown():
        print("\nSeleccione una acción:")
        print("1: Añadir obstáculos a la escena de planificación (suelo)")
        print("2: Mover el robot a una pose (posición y orientación del extremo)")
        print("3: Mover el robot a una configuración (ángulos de las articulaciones)")
        print("4: Mover el extremo del robot por una trayectoria dada")
        print("5: Activar control por detección de manos")
        print("6: Desactivar control por detección de manos")
        print("Ingrese el código de acción (1-6), o 'q' para salir:")
        input_str = input()
        if input_str.lower() == 'q':
            break
        try:
            action_code = int(input_str)
            if action_code < 1 or action_code > 6:
                print("Código de acción inválido. Ingrese un número entre 1 y 6.")
                continue
            msg = Int32()
            msg.data = action_code
            pub.publish(msg)
            print(f"Se ha publicado el código de acción {action_code} en /consignas.")
        except ValueError:
            print("Entrada inválida. Ingrese un número entre 1 y 6.")
        rate.sleep()

if __name__ == '__main__':
    try:
        order_publisher()
    except rospy.ROSInterruptException:
        pass