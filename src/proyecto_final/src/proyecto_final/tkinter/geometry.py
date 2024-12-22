

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

class FigureGenerator:
    def __init__(self) -> None:
        self.matriz3D = None

    def generate_figure_from_matrix(self, plant_matrix, side_matrix, tkinter:bool=False):

        anchura, profundidad, plant_matrix_recortada = self._cut_matrix_finding_shape(plant_matrix)
        altura, _, front_matrix_recortada = self._cut_matrix_finding_shape(side_matrix)
        
        if altura is None and anchura is None and profundidad is None:
            return self._paint_matrix(np.array([[[]]]), 1, tkinter)

        self.matriz3D = np.full((anchura, altura, profundidad), -1)
        matriz3D_positiva = np.full((anchura, altura, profundidad), -1)
        matriz3D_inversa = np.full((anchura, altura, profundidad), -1)
        front_matrix_recortada_inv = deepcopy(front_matrix_recortada)

        # Definir el tamaño de cada cubo
        size = 1

        for columna_planta in range(0, profundidad, 1):
            columna_planta_inversa = profundidad - 1 - columna_planta
            for fila_planta in range(anchura-1, -1, -1):
                if plant_matrix_recortada[fila_planta][columna_planta] != -1:
                    color_cubo = plant_matrix_recortada[fila_planta][columna_planta]
                    cube_found = False
                    for fila_lateral in range(0, altura, 1):
                        columna_lateral = anchura - fila_planta - 1
                        x = columna_lateral
                        y = profundidad - columna_planta - 1
                        z = altura -1 - fila_lateral
                        # Delante hacia atras = Positiva
                        if plant_matrix_recortada[fila_planta][columna_planta] == front_matrix_recortada[fila_lateral][columna_lateral]:
                            matriz3D_positiva[x][z][y] = color_cubo
                            front_matrix_recortada[fila_lateral][columna_lateral] = -1
                            cube_found = True

                        elif cube_found and front_matrix_recortada[fila_lateral][columna_lateral] == -1:
                            matriz3D_positiva[x][z][y] = 4

                        elif cube_found and front_matrix_recortada[fila_lateral][columna_lateral] != -1:
                            matriz3D_positiva[x][z][y] = front_matrix_recortada[fila_lateral][columna_lateral]
                            front_matrix_recortada[fila_lateral][columna_lateral] = -1

                    if not cube_found:
                        z= 0
                        matriz3D_positiva[x][z][y] = color_cubo
                
                # Atras hacia adelante = Inversa
                if plant_matrix_recortada[fila_planta][columna_planta_inversa] != -1:
                    color_cubo = plant_matrix_recortada[fila_planta][columna_planta_inversa]
                    cube_found = False
                    for fila_lateral in range(0, altura, 1):
                        columna_lateral = anchura - fila_planta - 1
                        x = columna_lateral
                        y = profundidad - columna_planta_inversa - 1
                        z = altura -1 - fila_lateral
                        # Atras hacia delante = Inversa
                        if plant_matrix_recortada[fila_planta][columna_planta_inversa] == front_matrix_recortada_inv[fila_lateral][columna_lateral]:
                            matriz3D_inversa[x][z][y] = color_cubo
                            front_matrix_recortada_inv[fila_lateral][columna_lateral] = -1
                            cube_found = True

                        elif cube_found and front_matrix_recortada_inv[fila_lateral][columna_lateral] == -1:
                            matriz3D_inversa[x][z][y] = 4

                        elif cube_found and front_matrix_recortada_inv[fila_lateral][columna_lateral] != -1:
                            matriz3D_inversa[x][z][y] = front_matrix_recortada_inv[fila_lateral][columna_lateral]
                            front_matrix_recortada_inv[fila_lateral][columna_lateral] = -1

                    if not cube_found:
                        z= 0
                        matriz3D_inversa[x][z][y] = color_cubo

        self._compare_matrix(matriz3D_positiva, matriz3D_inversa)
        return self._paint_matrix(self.matriz3D, size, tkinter)
                
    def _cut_matrix(self, matriz, num_filas, num_columnas):
        # Recortar la matriz hasta el tamaño deseado
        matriz_recortada = [fila[:num_columnas] for fila in matriz[5-num_filas:5]]
        return matriz_recortada

    def _cut_matrix_finding_shape(self, matrix):
        i_max = None
        j_max = None
        # Iteramos sobre las filas de la última a la primera
        for i in range(len(matrix)): # Desde la primera fila hasta la ultima
            for j in range(len(matrix[i])): # Desde la última columna hasta la primera
                if matrix[i][4-j] != -1: # Si encontramos un valor distinto a -1
                    if i_max == None:
                        i_max = 5-i # Devolver la fila
                if matrix[j][4-i] != -1:
                    if j_max == None:
                        j_max = 5-i # Devolver la columna inversa
                if j_max != None and i_max != None:
                    return i_max, j_max, self._cut_matrix(matrix, i_max, j_max)

        return None, None, matrix # Si no hay valores diferentes a -1, retornar None

    def _compare_matrix(self, matrix_pos, matrix_inv):
        x, z, y = self.matriz3D.shape
        for i in range(x):
            for j in range(z):
                for k in range(y):
                    if matrix_pos[i,j,k] == -1 or matrix_inv[i,j,k]== -1:
                        self.matriz3D[i,j,k] = -1
                    elif matrix_pos[i,j,k] == matrix_inv[i,j,k]:
                        self.matriz3D[i,j,k] = matrix_pos[i,j,k]
                    else:
                        self.matriz3D[i,j,k] = 4

    def _paint_matrix(self, matriz3D, size, tkinter:bool=False):

        # Definición de las variables
        color_map = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow', 4: 'gray'}
        anchura, altura, profundidad = matriz3D.shape

        # Dependiendo de si lo mostramos en la interfaz o no, se realizan dos acciones de plt
        if tkinter:
            fig_3d = plt.Figure(figsize=(8, 4), dpi=100)
            ax = fig_3d.add_subplot(111, projection='3d')
        else:
            fig_3d, ax = plt.subplots(figsize=(8, 4), dpi=100, subplot_kw={'projection': '3d'})


        # Se recorre la matriz para dibujar la figura
        for x in range(anchura):
            for y in range(profundidad):
                for z in range(altura): 
                    if matriz3D[x, z, y] != -1:
                        ax.bar3d(x*size,y*size,z*size, size, size, size, color=color_map[matriz3D[x, z, y]])
        
        # Configurar los límites del gráfico
        ax.set_xlim([0, 5 * size])
        ax.set_ylim([0,  5 * size])
        ax.set_zlim([0, 5 * size])

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Ajustar la vista para que la figura se vea al fondo
        ax.view_init(elev=30, azim=-60)

        # Mostrar o devolver la figura
        if tkinter:
            return fig_3d
        else:
            plt.show()
            return None
    

if __name__ in "__main__":
    generator = FigureGenerator()

    # Figura 1
    top_side_1 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [2, 0, 3, -1, -1]]

    front_side_1 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, -1, -1, -1, -1],
                    [3, 1, -1, -1, -1]]

    # Figura 2
    top_side_2 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, -1, -1, -1, -1],
                [2, -1, -1, -1, -1],
                [0, 3, 1, 3, -1]]

    front_side_2 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, -1, -1, -1, -1],
                    [3, 2, 0, -1, -1]]

    # Figura 3
    top_side_3 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 0, -1, -1],
                    [0, 1, 2, -1, -1],
                    [-1, 3, 1, -1, -1]]

    front_side_3 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [1, 2, 0, -1, -1]]

    # Figura 4
    top_side_4 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [3, -1, 2, -1, -1],
                    [-1, 3, 1, -1, -1]]

    front_side_4 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [1, 2, 0, -1, -1]]

    # Figura 5
    top_side_5 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [2, 3, 1, -1, -1],
                    [-1, 0, -1, -1, -1]]

    front_side_5 = [[-1, 3, -1, -1, -1],
                    [-1, 0, -1, -1, -1],
                    [-1, 3, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [0, 1, 1, -1, -1]]

    # Figura 6 y Ultima
    top_side_6 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, 1, 3, -1, -1],
                    [2, 3, 1, -1, -1],
                    [1, 2, 3, -1, -1]]

    front_side_6 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [2, 3, 1, -1, -1],
                    [3, 1, 3, -1, -1]]
    
    # Figura 7 y Ultima
    top_side_7 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [3, 3, 1, -1, -1],
                    [3, 1, 3, -1, -1],
                    [3, 3, 3, -1, -1]]

    front_side_7 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [1, 3, 3, -1, -1]]

    pruebas_front = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 0, -1, -1, -1],
                    [1, 2, -1, -1, -1],
                    [ 3, 3, -1, -1, -1]]


    pruebas_top=[[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 0, 1, -1, -1],
                [3, 1, -1, -1, -1]]

    pruebas_limites_top = [[-1, -1, -1, -1, -1],
                            [-1, -1, 0, -1, -1],
                            [-1, 2, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1]]

    pruebas_limites_front = [[-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, 0, -1, -1, -1],
                            [1, 2, -1, -1, -1],
                            [3, 2, -1, -1, -1]]

    vacia = [[-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1]]

    generator._draw_pyramid_from_matrices(vacia, vacia)