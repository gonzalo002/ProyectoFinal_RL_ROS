from proyecto_final.control_robot import ControlRobot
from proyecto_final.vision.grupo_2.generacion_figura import FigureGenerator
import os

robot = ControlRobot()
generator = FigureGenerator()

abs_path = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:os.path.dirname(os.path.abspath(__file__)).split('/').index('proyecto_final')+1])

alzado_matrix = [[-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [-1,  1, -1, -1, -1],
                 [ 2,  3, -1, -1, -1]]
    
perfil_matrix = [[-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [-1,  1, -1, -1, -1],
                 [ 0,  2, -1, -1, -1]]

planta_matrix = [[-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [-1, -1, -1, -1, -1],
                 [ 1,  2, -1, -1, -1],
                 [ 0, -1, -1, -1, -1]]


robot.save_in_yaml(f'{abs_path}/data/debug_data/matrix', 'matriz_alzado', alzado_matrix, True)
robot.save_in_yaml(f'{abs_path}/data/debug_data/matrix', 'matriz_perfil', perfil_matrix)
robot.save_in_yaml(f'{abs_path}/data/debug_data/matrix', 'matriz_planta', planta_matrix)


# alzado_matrix = robot.read_from_yaml(f'{abs_path}/data/debug_data/matrix', 'matriz_alzada')

generator.generate_figure_from_matrix(planta_matrix, alzado_matrix, perfil_matrix, paint=True)