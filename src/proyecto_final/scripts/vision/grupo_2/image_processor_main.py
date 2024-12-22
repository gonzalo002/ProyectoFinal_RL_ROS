from image_processor_front import ImageProcessor_Front
from image_processor_top import ImageProcessor_Top
from proyecto_final.scripts.vision.grupo_2.generacion_figura import FigureGenerator

import cv2
import numpy as np
from copy import deepcopy

class ImageProcessor:
    def __init__(self, matrix_size:int = 5) -> None:
        self.frame_front = None
        self.front = ImageProcessor_Front()

        self.frame_top = None
        self.top = ImageProcessor_Top()

        self.generator = FigureGenerator()

        self.matrix_size = matrix_size
        self.matrix_front = np.full((self.matrix_size, self.matrix_size), -1)
        self.matrix_top = np.full((self.matrix_size, self.matrix_size), -1)

        self.debug = False

    def process_image(self, frame_top:np.ndarray, frame_side:np.ndarray, area_size:int = 2000, mostrar:bool=False, debug:bool=False)-> tuple:
        ''' 
        Ejecuta el flujo completo de procesamiento de una imagen para detectar colores y posiciones de cubos.
            - Almacena la imagen original y una copia para dibujar contornos.
            - Realiza el preprocesamiento para limpiar la imagen y detectar bordes.
            - Encuentra y filtra los contornos relevantes basándose en su tamaño.
            - Identifica los colores predominantes dentro de cada contorno y calcula las posiciones en una matriz.
            - Dibuja contornos y anotaciones sobre la imagen de salida.
            @param frame (numpy array) - Imagen de entrada en formato BGR.
            @param area_size (int) - Umbral mínimo de área para considerar un contorno como válido. Por defecto, 2000.
            @param mostrar (bool) - Si es True, muestra la imagen procesada.
            @return (tuple) - Una tupla con:
                - matrix (numpy array) - Matriz 5x5 que representa la cuadrícula con los colores detectados.
                - contour_img (numpy array) - Imagen con los contornos y anotaciones dibujados.
        '''
        self.frame_top = deepcopy(frame_top)
        self.frame_front = deepcopy(frame_side)
        self.debug = debug

        self.matrix_front, cont_img_front  = self.front.process_image(self.frame_front, area_size=300, debug=self.debug)
        self.matrix_top, cont_img_top = self.top.process_image(self.frame_top, area_size=300, debug=self.debug)

        if self.debug:
            print('Matrix Front')
            print(self.matrix_front)
            print('\n\n')
            print('Matrix Top')
            print(self.matrix_top)

        if mostrar:
            cv2.imshow('Image_Front', cont_img_front)
            cv2.imshow('Image_Top', cont_img_top)

            self.generator._draw_pyramid_from_matrices(self.matrix_top, self.matrix_front)

            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyAllWindows()

if __name__ == '__main__':
    processor = ImageProcessor()

    cam_lateral = cv2.VideoCapture(5)
    cam_top = cv2.VideoCapture(0)
    
    if not cam_lateral.isOpened() or not cam_top.isOpened():
        print("Error: No se pudo abrir el vídeo.")
    else:
        _, frame_top = cam_top.read()
        _, frame_front = cam_lateral.read()
        processor.process_image(frame_top=frame_top, frame_side=frame_front, mostrar=True, debug=False)

