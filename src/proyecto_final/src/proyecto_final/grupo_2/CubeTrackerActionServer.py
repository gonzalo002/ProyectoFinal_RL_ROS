#!/usr/bin/python3
import cv2, os, rospy, actionlib
from time import time
from math import pi
from copy import deepcopy
from threading import Thread
from cv_bridge import CvBridge
from collections import Counter
from sensor_msgs.msg import Image
from geometry_msgs.msg import Quaternion
from tf.transformations import quaternion_from_euler
from proyecto_final.vision.grupo_2.cube_tracker import CubeTracker
from proyecto_final.msg import CubosAction, CubosFeedback, CubosGoal, CubosResult, IdCubos
from proyecto_final.funciones_auxiliares import crear_mensaje


class CubeTrackerActionServer(object):
    
    def __init__(self):
        # Inicializar nodo
        rospy.init_node('cube_tracker_node')
        self.name = "CubeTrackerActionServer"

        # Obtenemos parámetro camara
        cam_on = rospy.get_param("~cam_on", False)
        if cam_on not in [True, False]:
            crear_mensaje("El parámetro 'cam_on' debe ser True o False. Se usará el valor predeterminado 'True'.", "WARN", self.name)
            rospy.logwarn("")
            cam_on = True

        # Definición de variables Python
        self.file_path = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:os.path.dirname(os.path.abspath(__file__)).split('/').index('proyecto_final')+1])
        self.running = False
        self.CubeTracker = CubeTracker(cam_calib_path=f"{self.file_path}/data/necessary_data/ost.yaml")

        # Definicion de variables ROS
        if cam_on:
            self.obtain_img = False
            self.cv_img = []
            self.bridge = CvBridge()
            self._subs_cam = rospy.Subscriber('/top_cam/image_raw', Image, self.cb_image)
            self.action_server = actionlib.SimpleActionServer('CubeTrackerActionServer', CubosAction, execute_cb=self.execute_cb_on, auto_start=False)
        else:
            self.action_server = actionlib.SimpleActionServer('CubeTrackerActionServer', CubosAction, execute_cb=self.execute_cb_off, auto_start=False)
        
        self.action_server.start()
        rospy.spin()
    
    def cb_image(self, image:Image)->None:
        ''' 
        Callback del subscriptor de la cámara.
            @param image (Image) - Imagen de la camara
        '''
        if self.obtain_img:
            if len(self.cv_img) < 11:
                img = deepcopy(self.bridge.imgmsg_to_cv2(image, desired_encoding='passthrough'))
                img = deepcopy(cv2.cvtColor(img, cv2.COLOR_RGB2BGR)) #Convertir imagen a BGR
                self.cv_img.append(img)
            else:
                self.obtain_img = False


    def execute_cb_off(self, goal:CubosGoal)->None:
        self.color_counter = [0,0,0,0]
        # Crear y ejecutar el hilo de feedback
        feedback = CubosFeedback()
        self.running = True
        feedback_thread = Thread(target=self.send_feedback, args=(feedback,))
        feedback_thread.start()

        img = cv2.imread(f"{self.file_path}/data/example_img/cubos_exparcidos/Cubos_Exparcidos_{goal.order}.png")
        if img is None:
            crear_mensaje("No se ha podido encontrar la imagen", "ERROR", self.name)
            feedback.feedback = -1
            self.action_server.publish_feedback(feedback)
            self.running = False
            feedback_thread.join()
            self.action_server.set_aborted()
            return
        
        resultado_final = CubosResult()
        img_process, resultado = self.CubeTracker.process_image(img)
        cv2.imwrite("CubeTracker.png", img_process)
        resultado_final.cubes_position = self._dict_to_cube(resultado)
        resultado_final.color_counter = self.color_counter

        # Paso 3: Finalizar la acción con el resultado procesado
        self.action_server.set_succeeded(resultado_final)

        # Esperar a que el hilo de feedback termine
        self.running = False
        feedback_thread.join()


    def execute_cb_on(self, goal:CubosGoal)->None:
        ''' 
        Callback del action server del CubeTracker
            @param goal (numpy array) - Goal recibido por el cliente
        '''
        self.color_counter = [0,0,0,0]
        self.obtain_img = True
        feedback = CubosFeedback()  # Crear un objeto de feedback

        # Crear y ejecutar el hilo de feedback
        self.running = True
        feedback_thread = Thread(target=self.send_feedback, args=(feedback,))
        feedback_thread.start()

        # Paso 1: Obtener la imagen con timeout
        timeout = 5
        start_time = time()
        while self.obtain_img:
            elapsed_time = time() - start_time
            if elapsed_time > timeout:
                crear_mensaje("Timeout al intentar obtener la imagen", "ERROR", self.name)
                feedback.feedback = -1
                self.action_server.publish_feedback(feedback)
                self.running = False
                feedback_thread.join()
                self.action_server.set_aborted()
                return

            rospy.sleep(0.2)
            
        L_img = deepcopy(self.cv_img)

        # Paso 2: Procesar la imagen
        L_resultado = []
        for i in range(len(L_img)):
            img_process, resultado = self.CubeTracker.process_image(L_img[i])
            L_resultado.append(resultado)

        resultado_final = CubosResult()
        cv2.imwrite("CubeTracker.png", img_process)
        resultado_final.cubes_position = self._dict_to_cube(resultado)
        resultado_final.color_counter = self.color_counter

        # Paso 3: Finalizar la acción con el resultado procesado
        self.action_server.set_succeeded(resultado_final)

        # Esperar a que el hilo de feedback termine
        self.running = False
        feedback_thread.join()
        self.cv_img = []

    def lista_mas_frecuente(lista_de_listas):
        # Convertir cada lista de diccionarios en una tupla de colores
        listas_colores = [tuple(sorted([item["color"] for item in lista])) for lista in lista_de_listas]

        # Contar las ocurrencias de cada "lista de colores"
        counter = Counter(listas_colores)

        # Obtener la lista más frecuente (más común)
        lista_mas_comun, _ = counter.most_common(1)[0]

        # Convertir la tupla más común de vuelta al formato original
        return list(lista_mas_comun)

    def send_feedback(self, feedback:CubosFeedback):
        ''' 
        Función que utiliza el hilo para enviar el feedback al cliente
            @param feedback (CubosActionFeedback) - Feedback
        '''
        while self.action_server.is_active() and self.running:
            feedback.feedback = 1
            self.action_server.publish_feedback(feedback)
            rospy.sleep(0.1)

    def _dict_to_cube(self, dict_cubos:list) -> list:
        ''' 
        Función que convierte la lista recibida por el procesador de cubos a IDCubos.
            @param dict_cubos (list) - Lista con el diccionario de los diferentes cubos
        '''
        cubos = []
        id = 0
        for dict in dict_cubos:
            # Declaramos IDCubos
            cubo = IdCubos()

            # Ajustamos la posición y orientación
            cubo.pose.position.x = dict['Position'][0]
            cubo.pose.position.y = dict['Position'][1]
            cubo.pose.position.z = 0.0125
            cubo.pose.orientation = Quaternion(*quaternion_from_euler(pi, 0, -dict['Angle'], 'sxyz'))

            # Ajustamos el color del cubo y su id
            cubo.color = dict['Color']
            cubo.id = id

            #Ajustamos el contador de color
            self.color_counter[cubo.color] += 1

            # Guardamos en la lista de cubos
            cubos.append(deepcopy(cubo))
            id += 1

        return cubos
            
            
if __name__ == "__main__":
    CubeTrackerActionServer()