from image_processor_front import ImageProcessor_Front
from image_processor_top import ImageProcessor_Top
from generacion_figura import FigureGenerator

import cv2
import numpy as np
from copy import deepcopy
import os
import matplotlib.pyplot as plt

class ImageProcessor:
    def __init__(self, matrix_size:int = 5) -> None:
        self.frame_front = None
        self.front = ImageProcessor_Front()

        self.frame_top = None
        self.top = ImageProcessor_Top()

        self.frame_side = None

        self.matrix3D = None
        self.generator = FigureGenerator()

        self.matrix_size = matrix_size
        self.matrix_alzado = np.full((self.matrix_size, self.matrix_size), -1)
        self.matrix_planta = np.full((self.matrix_size, self.matrix_size), -1)

        self.debug = False
    
    def save_images(self) -> None:
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        i = len(os.listdir(f'{file_path}/data/figuras_alzado/'))+1

        cv2.imwrite(f'{file_path}/data/figuras_alzado/Figura_{i}_L.png', self.frame_front)
        cv2.imwrite(f'{file_path}/data/figuras_planta/Figura_{i}_S.png', self.frame_top)
        cv2.imwrite(f'{file_path}/data/figuras_perfil/Figura_{i}_F.png', self.frame_side)
        print(f"\033[32m --- IMAGEN GUARDADA ---\033[0m")

    def on_key(event):
        if event.key == 'q':  # Si se presiona la tecla 'q'
            plt.close('all')  # Cierra todas las figuras abiertas

    def process_image(self, frame_top:np.ndarray, frame_front:np.ndarray, frame_side:np.ndarray, mostrar:bool=False, debug:bool=False, save_images:bool = False)-> tuple:
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
        self.frame_front = deepcopy(frame_front)
        self.frame_side = deepcopy(frame_side)
        self.debug = debug

        self.matrix_alzado, img_final_alzado  = self.front.process_image(self.frame_front, debug=debug)
        self.matrix_planta, img_final_planta = self.top.process_image(self.frame_top, debug=debug)
        self.matrix_perfil, img_final_perfil = self.front.process_image(frame=self.frame_side, debug=debug)

        if self.debug:
            print('Matriz Alzado')
            print(self.matrix_alzado)
            print('\n\n')
            print('Matriz Planta')
            print(self.matrix_planta)
            print('\n\n')
            print('Matriz Perfil')
            print(self.matrix_perfil)

        if save_images:
            self.save_images()

        if mostrar:
            fig = plt.figure()

            #fig, ax = plt.subplots(2,2, figsize=(10,10))
            ax = fig.add_subplot(2,2, 1, )
            img_final_alzado = cv2.cvtColor(img_final_alzado, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_alzado)
            ax.set_title('Imagen Alzado')
            ax.axis('off')

            ax = fig.add_subplot(2, 2, 2)
            img_final_perfil = cv2.cvtColor(img_final_perfil, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_perfil)
            ax.set_title('Imagen Perfil')
            ax.axis('off')

            ax = fig.add_subplot(2, 2, 3)
            img_final_planta = cv2.cvtColor(img_final_planta, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_planta)
            ax.set_title('Imagen Planta')
            ax.axis('off')
            

            fig_3d = self.generator.generate_figure_from_matrix(self.matrix_planta, self.matrix_perfil, self.matrix_alzado, paint=mostrar, tkinter=True)
            ax = fig.add_subplot(2, 2, 4)
            fig_3d.savefig("/tmp/figura_secundaria.png", format="png")
            ax.set_title('Figura 3D')
            ax.axis('off')
            ax.imshow(plt.imread("/tmp/figura_secundaria.png"))

            # Ajustar el espaciado entre los subgráficos
            plt.tight_layout()

            # Mostrar todos los gráficos
            plt.show()

if __name__ == '__main__':
    processor = ImageProcessor()

    use_cam = False
    num_figure = 1
    debug = False # Si se quiere que se muestre el proceso interno de cada clase

    if use_cam:    
        cam_front = cv2.VideoCapture(0)
        cam_top = cv2.VideoCapture(9)
        cam_side = cv2.VideoCapture(5)
        
        if not cam_front.isOpened() or not cam_top.isOpened() or not cam_side.isOpened():
            print("Error: No se pudo abrir el vídeo.")
        else:
            _, frame_top = cam_top.read()
            _, frame_front = cam_front.read()
            _, frame_side = cam_side.read()
    else:
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        frame_front = cv2.imread(f'{file_path}/data/figuras_alzado/Figura_{num_figure}_F.png')
        frame_top = cv2.imread(f'{file_path}/data/figuras_planta/Figura_{num_figure}_S.png')
        frame_side = cv2.imread(f'{file_path}/data/figuras_perfil/Figura_{num_figure}_L.png')

    
    processor.process_image(frame_top=frame_top, frame_front=frame_front, frame_side=frame_side, mostrar=True, debug=debug, save_images=False)

