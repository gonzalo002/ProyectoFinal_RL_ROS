from turtle import color
import matplotlib.pyplot as plt
import numpy as np

class FigureGenerator:
    def __init__(self) -> None:
        pass
    
    def _recortar_matriz_por_dimension(self, matriz, num_filas, num_columnas):
        # Recortar la matriz hasta el tamaño deseado
        matriz_recortada = [fila[:num_columnas] for fila in matriz[5-num_filas:5]]
        return matriz_recortada
        
    def find_first_non_minus_one(self, matrix):
        i_max = None
        j_max = None
        # Iteramos sobre las filas de la última a la primera
        for i in range(len(matrix)):  # Desde la primera fila hasta la ultima
            for j in range(len(matrix[i])):  # Desde la última columna hasta la primera
                if matrix[i][4-j] != -1:  # Si encontramos un valor distinto a -1
                    if i_max == None:
                        i_max = 5-i  # Devolver la fila
                if matrix[j][4-i] != -1:
                    if j_max == None:
                        j_max = 5-i # Devolver la columna inversa
                if j_max != None and i_max != None:
                    return i_max, j_max, self._recortar_matriz_por_dimension(matrix, i_max, j_max)
                
        return None, None, matrix # Si no hay valores diferentes a -1, retornar None


    def _draw_pyramid_from_matrices(self, plant_matrix, side_matrix):
        
        anchura, profundidad, plant_matrix_recortada = self.find_first_non_minus_one(plant_matrix)
        altura, _, front_matrix_recortada = self.find_first_non_minus_one(side_matrix)
        
        print
        

        matriz3D = np.full((anchura, altura, profundidad), -1)
        # Usamos plt.subplots() para crear la figura y los ejes
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100, subplot_kw={'projection': '3d'})

        # Definir los colores de los cubos
        colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow', 4: 'gray'}

        # Definir el tamaño de cada cubo
        size = 0.2

        # Iterar sobre las matrices para colocar los cubos
        # for fila_planta in range(anchura-1, -1, -1):  # Para cada fila de la planta
        #     flag_cube_found_plant = False
        #     for columna_planta in range(profundidad-1, -1, -1):  # Para cada columna de la 
        #         if plant_matrix_recortada[fila_planta][columna_planta] != -1:  # Si hay un cubo en la vista de planta
        #             flag_cube_found_lateral = False
                    
        #             color_cubo = plant_matrix_recortada[fila_planta][columna_planta]

        #             x = col_lat = anchura-fila_planta-1
        #             y = profundidad - 1 - columna_planta
                    
        #             for fila_lateral in range(0, altura, 1):
        #                 if not flag_cube_found_lateral and color_cubo == side_matrix_recortada[fila_lateral][col_lat]:
        #                     flag_cube_found_lateral = True
        #                     flag_cube_found_plant = True
        #                     z = altura -1 -fila_lateral
        #                     matriz3D[x][z][y] = color_cubo            
        #                     #break
                            
                         
        #                 elif side_matrix[fila_lateral][col_lat] != -1:
                        
        #                     z = altura -1 -fila_lateral
        #                     matriz3D[x][z][y] = side_matrix[fila_lateral][col_lat]

        #                 if flag_cube_found_plant and plant_matrix[fila_planta][columna_planta]!=-1:
        #                     y = columna_planta
        #                     z = 0
        #                     matriz3D[x][z][y] = color_cubo
            
        for columna_planta in range(0, profundidad, 1):
            for fila_planta in range(anchura-1, -1, -1):
                if plant_matrix_recortada[fila_planta][columna_planta] != -1:
                    color_cubo = plant_matrix_recortada[fila_planta][columna_planta]
                    cube_found = False
                    for fila_lateral in range(0, altura, 1):
                        columna_lateral = anchura - fila_planta - 1
                        x = columna_lateral
                        y = profundidad - columna_planta - 1
                        z = altura -1 - fila_lateral
                        if plant_matrix_recortada[fila_planta][columna_planta] == front_matrix_recortada[fila_lateral][columna_lateral]:
                            matriz3D[x][z][y] = color_cubo
                            front_matrix_recortada[fila_lateral][columna_lateral] = -1
                            cube_found = True
                        
                        elif cube_found and front_matrix_recortada[fila_lateral][columna_lateral] == -1:
                            matriz3D[x][z][y] = 4
                        
                        elif cube_found and front_matrix_recortada[fila_lateral][columna_lateral] != -1:
                            matriz3D[x][z][y] = front_matrix_recortada[fila_lateral][columna_lateral]
                            front_matrix_recortada[fila_lateral][columna_lateral] = -1
                        
                    if not cube_found:
                        z= 0
                        matriz3D[x][z][y] = color_cubo
                            
                            
                            
                                
                                
                
                                

                                
        #matriz3D = self.adjust_cubes(matriz3D)
        print(matriz3D)
        ax = self.paint_matrix(matriz3D, ax, size, colors)

        # Configurar los límites del gráfico
        ax.set_xlim([0, len(plant_matrix[0]) * size])
        ax.set_ylim([0, len(plant_matrix) * size])
        ax.set_zlim([0, len(side_matrix) * size])

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Ajustar la vista para que la figura se vea al fondo
        ax.view_init(elev=30, azim=-60)

        # Mostrar la figura
        plt.show()

    def adjust_cubes(self, matriz3D):
        # Obtenemos las dimensiones de la matriz
        anchura, altura, profundidad = matriz3D.shape

        # Recorremos la matriz en las tres dimensiones
        for x in range(anchura):
            for y in range(profundidad):
                for z in range(altura - 1):  # No hace falta revisar la última capa en z
                    # Si hay un cubo en (x, y, z) y debajo no hay nada
                    if matriz3D[x, y, z+1] != -1 and matriz3D[x, y, z ] == -1:
                        matriz3D[x, y, z] = 4  # Cambiamos el valor del cubo

        return matriz3D

    def paint_matrix(self, matriz3D, ax, size, color_map):
        anchura, altura, profundidad = matriz3D.shape
        for x in range(anchura):
            for y in range(profundidad):
                for z in range(altura):  
                    if matriz3D[x, z, y] != -1:
                        ax.bar3d(x*size,y*size,z*size,size, size, size, color=color_map[matriz3D[x, z, y]])
        return ax
    
if __name__ in "__main__":
    generator = FigureGenerator()
    
    # Figura 1
    top_side = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 3, 1, -1, -1],
                [2, 0, 3, -1, -1]]

    front_side = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, -1, -1, -1, -1],
                [3, 1, -1, -1, -1]]
    
    # Figura 2
    top_side_1 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, -1, -1, -1, -1],
                [2, -1, -1, -1, -1],
                [0, 3, 1, 3, -1]]

    front_side_1 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, -1, -1, -1, -1],
                [3, 2, 0, -1, -1]]
    
    # Figura 3
    top_side_2 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 3, 0, -1, -1],
                [0, 1, 2, -1, -1],
                [-1, 3, 1, -1, -1]]

    front_side_2 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [1, 2, 0, -1, -1]]
    
    # Figura 4
    top_side_3 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 3, 1, -1, -1],
                [3, -1, 2, -1, -1],
                [-1, 3, 1, -1, -1]]

    front_side_3 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 3, 1, -1, -1],
                [1, 2, 0, -1, -1]]
    
    # Figura 5
    top_side_4 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 1, -1, -1, -1],
                [2, 3, 1, -1, -1],
                [-1, 0, -1, -1, -1]]

    front_side_4 = [[-1, 3, -1, -1, -1],
                    [-1, 0, -1, -1, -1],
                    [-1, 3, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [0, 1, 1, -1, -1]]
    
    # Figura 6 y Ultima
    top_side_1 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, 1, 3, -1, -1],
                [2, 3, 1, -1, -1],
                [1, 2, 3, -1, -1]]

    front_side_1 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [2, 3, 1, -1, -1],
                    [3, 1, 3, -1, -1]]

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

    
    generator._draw_pyramid_from_matrices(top_side_1, front_side_1)