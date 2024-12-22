import matplotlib.pyplot as plt
import numpy as np

class Geometry2D:
    def __init__(self, square_size:int=5):
        self.square_size = square_size  

    def draw_2d_space_tkinter(self, aruco_pose, cube_data, tkinter:bool=False):
            """
            Dibuja un espacio 2D con cubos representados como cuadrados y lo devuelve como un widget para Tkinter.

                @param aruco_pose (list) - Lista con la posición de Aruco [x, y] (en m) 
                
                @param cube_data (list of dict): Lista de diccionarios, donde cada diccionario tiene:
                    - 'Position': Lista con la posición de los cubos relativas al Aruco [x, y] (en m)
                    - 'Angle': Angulo de rotación en z
                    - 'Color': Número que representa el color del cubo.

                @param tkinter (bool) - Booleano que indica si se quiere integrar en Tkinter o no. Por defecto, False.

                @return fig_3d (plt.Figure) - Figura de la proyección 2D
            """

            # Definir los colores de los cubos
            colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}
            
            # Dependiendo de si lo mostramos en la interfaz o no, se realizan dos acciones de plt
            if tkinter:
                fig_3d = plt.Figure(figsize=(8, 3.5), dpi=100)
                ax = fig_3d.add_subplot(11)
            else:
                fig_3d, ax = plt.subplots(figsize=(8, 3.5), dpi=100)

            # --- REPRESENTACIÓN DEL ARUCO ---
            ax.add_patch(plt.Rectangle((aruco_pose[0], aruco_pose[1]), 1, 1, color='black'))

            # --- REPRESENTACIÓN DE LOS CUBOS ---
            new_cube_data_max = None
            new_cube_data_min = None

            for cube in cube_data:
                # Obtener parametros del cubo
                angle = cube['Angle'] 
                x = cube['Position'][0] * np.cos(angle) - cube['Position'][1] * np.sin(angle)
                y = cube['Position'][0] * np.sin(angle) + cube['Position'][1] * np.cos(angle)

                # Calcular posición respecto al Aruco
                x_rot = (aruco_pose[0] + (-1)*x)*100
                y_rot = (aruco_pose[1] + y)*100

                # Crear un cuadrado y rotarlo 
                square = np.array([
                    [x_rot, y_rot],  
                    [x_rot + self.square_size, y_rot],  
                    [x_rot + self.square_size, y_rot + self.square_size],  
                    [x_rot, y_rot + self.square_size] 
                ])

                # Rotar las esquinas del cuadrado alrededor del origen
                cos_theta = np.cos(angle)
                sin_theta = np.sin(angle)
                rotation_matrix = np.array([[cos_theta, -sin_theta],
                                            [sin_theta, cos_theta]])

                # Rotar todas las esquinas
                square_rotated = np.dot(square - [x_rot, y_rot], rotation_matrix) + [x_rot, y_rot]

                # Dibujar el cuadrado rotado
                ax.add_patch(plt.Polygon(square_rotated, color=colors.get(cube['Color']), edgecolor='black'))

                # Determinar límites del gráfico
                if new_cube_data_max is None:
                    new_cube_data_max = [x_rot + self.square_size, y_rot + self.square_size]
                else:
                    if (x_rot + self.square_size) > new_cube_data_max[0]:
                        new_cube_data_max[0] = x_rot + self.square_size
                    
                    if (y_rot + self.square_size) > new_cube_data_max[1]:
                        new_cube_data_max[1] = y_rot + self.square_size
                
                if new_cube_data_min is None:
                    new_cube_data_min = [x_rot, y_rot]
                else:
                    if x_rot < new_cube_data_min[0]:
                        new_cube_data_min[0] = x_rot
                    
                    if y_rot < new_cube_data_min[1]:
                        new_cube_data_min[1] = y_rot

            
            # Ajustar los límites del gráfico
            ax.set_xlim(new_cube_data_min[0]-10, new_cube_data_max[0]+10)
            ax.set_ylim(new_cube_data_min[1]-10, new_cube_data_max[1]+10)
            
            # Etiquetas y grid
            ax.set_xlabel('X (cm)')
            ax.set_ylabel('Y (cm)')
            ax.set_aspect('equal', adjustable='box')
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            plt.subplots_adjust(bottom=0.2)

            # Mostrar o devolver la figura
            if tkinter:
                return fig_3d
            else:
                plt.show()
                return None
            
if __name__ == "__main__":
    dicionario_resultado = [
    {
        "Position": [0.07, 0.04],  # Distancia ficticia calculada
        "Angle": 0.785398,  # Aproximación de pi/4 en radianes
        "Color": 0  # Índice para color azul (0, 0, 255)
    },
    {
        "Position": [0.05, -0.05],  # Otra distancia ficticia
        "Angle": 1.5708,  # Aproximación de pi/2 en radianes
        "Color": 1  # Índice para color verde (0, 255, 0)
    },
    {
        "Position": [-0.15, 0.04],  # Distancia ficticia adicional
        "Angle": 2.35619,  # Aproximación de 3pi/4 en radianes
        "Color": 2  # Índice para color rojo (255, 0, 0)
    },
    {
        "Position": [0.01, -0.02],
        "Angle": 3.14159,  # Aproximación de pi en radianes
        "Color": 3  # Índice para color cian (0, 255, 255)
    }
    ]
    aruco_pose = [0.1, 0.05]

    geomtria = Geometry2D()
    geomtria.draw_2d_space_tkinter(aruco_pose, dicionario_resultado)