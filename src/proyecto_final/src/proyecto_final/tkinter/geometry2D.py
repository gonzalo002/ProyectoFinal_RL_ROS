import matplotlib.pyplot as plt
import numpy as np
from proyecto_final.vision.grupo_2.cube_tracker import CubeTracker
import cv2

class Geometry2D:
    def __init__(self, square_size: int = 5):
        self.square_size = square_size  # Tamaño de los cuadrados en centímetros

    def draw_2d_space(self, cube_data, tkinter: bool = False):
        """
        Dibuja un espacio 2D con cubos representados como cuadrados.

        @param cube_data (list of dict): Lista de diccionarios, donde cada diccionario tiene:
            - 'Position': Tupla con la posición de los cubos relativas al Aruco [x, y] (en metros).
            - 'Angle': Ángulo de rotación en radianes.
            - 'Color': Número que representa el color del cubo.
        @param tkinter (bool): Booleano que indica si se quiere integrar en Tkinter o no. Por defecto, False.

        @return fig_2d (plt.Figure): Figura de la proyección 2D.
        """
        # Definir los colores de los cubos
        colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}

        # Configurar la figura
        if tkinter:
            fig_2d = plt.Figure(figsize=(8, 3.5), dpi=100)
            ax = fig_2d.add_subplot(1, 1, 1)
        else:
            fig_2d, ax = plt.subplots(figsize=(8, 3.5), dpi=100)

        # Representar el Aruco
        if len(cube_data) > 0:
            ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, 1, color='black', label='Aruco'))

        new_cube_data_min = None
        new_cube_data_max = None
        # Representar los cubos
        for cube in cube_data:
            position = cube['Position']
            angle = cube['Angle']
            color = colors.get(cube['Color'], 'gray')

            # Convertir posición a centímetros
            x_center = position[0] * 100  # metros a centímetros
            y_center = position[1] * 100

            # Crear las esquinas del cuadrado antes de la rotación
            half_size = self.square_size / 2
            square = np.array([
                [x_center - half_size, y_center - half_size],
                [x_center + half_size, y_center - half_size],
                [x_center + half_size, y_center + half_size],
                [x_center - half_size, y_center + half_size]
            ])

            if new_cube_data_min is None:
                    new_cube_data_min = [x_center - half_size, y_center - half_size]
            else:
                if (x_center - half_size) < new_cube_data_min[0]:
                    new_cube_data_min[0] = x_center - half_size
                    
                if (y_center - half_size) < new_cube_data_min[1]:
                    new_cube_data_min[1] = y_center - half_size

            if new_cube_data_max is None:
                    new_cube_data_max = [x_center + half_size, y_center + half_size]
            else:
                if (x_center + half_size) > new_cube_data_max[0]:
                    new_cube_data_max[0] = x_center + half_size
                    
                if (y_center + half_size) > new_cube_data_max[1]:
                    new_cube_data_max[1] = y_center + half_size
                        
            # Rotar el cuadrado alrededor de su centro
            cos_theta = np.cos(angle)
            sin_theta = np.sin(angle)
            rotation_matrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
            square_rotated = np.dot(square - [x_center, y_center], rotation_matrix) + [x_center, y_center]

            # Dibujar el cuadrado
            ax.add_patch(plt.Polygon(square_rotated, color=color, edgecolor='black', label=f'Cubo {cube["Color"]}'))

        # Ajustar los límites del gráfico
        if new_cube_data_max is not None and new_cube_data_min is not None:
            ax.set_xlim(new_cube_data_min[0]-5, new_cube_data_max[0]+5)
            ax.set_ylim(new_cube_data_min[1]-5, new_cube_data_max[1]+5)

        ax.set_xlabel('X (cm)', labelpad=-2.0)
        ax.set_ylabel('Y (cm)')
        ax.set_aspect('equal')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Mostrar la figura
        if tkinter:
            return fig_2d
        else:
            plt.show()
            return None
            
if __name__ == "__main__":

    use_cam = False
    cube_tracker = CubeTracker(cam_calib_path="/home/laboratorio/ros_workspace/src/proyecto_final/data/camera_data/ost.yaml")

    if use_cam:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            _, frame = cam.read()
            cv2.imshow("hola", frame)
    else:
        num = 3
        ruta = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Cubos_Exparcidos/Cubos_Exparcidos_{num}.png'
        frame = cv2.imread(ruta)

    _, resultado = cube_tracker.process_image(frame, area_size=1000, mostrar=False, debug=False)
    cv2.imwrite("prueba.png", _)
    print(resultado)
    if use_cam:
        cam.release()
    geomtria = Geometry2D()
    geomtria.draw_2d_space([0,0], resultado)