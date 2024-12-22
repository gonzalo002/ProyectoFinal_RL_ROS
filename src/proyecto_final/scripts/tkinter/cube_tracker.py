import cv2
import numpy as np
from copy import deepcopy
import yaml

class CubeTracker:
    ''' 
    Clase que procesa imágenes para detectar cubos y asignarles un color en función de su forma y tonalidad en el espacio de color HSV.
    
    Esta clase implementa varios métodos para:
        - Convertir imágenes a escala de grises o al espacio de color HSV.
        - Aplicar umbrales de Otsu para binarización.
        - Detectar bordes utilizando el filtro de Canny.
        - Encontrar contornos en las imágenes procesadas.
        - Identificar cubos en las imágenes y asignarles un color basado en su tonalidad.
        - Mostrar la imagen procesada y cerrar las ventanas de visualización.
    
    Métodos:
        - __init__() - Inicializa el objeto y crea un espacio para almacenar la imagen.
        - _aplicar_filtro_grises() - Convierte la imagen a escala de grises.
        - _aplicar_filtro_hsv() - Convierte la imagen a espacio de color HSV.
        - _procesar_umbral_otsu() - Aplica un umbral de Otsu para binarizar la imagen.
        - _detectar_bordes() - Detecta los bordes en una imagen utilizando Canny.
        - _encontrar_contornos() - Encuentra los contornos de una imagen binarizada.
        - _identificar_cubo_y_color() - Identifica cubos y les asigna un color basado en el espacio HSV.
        - analizar_imagen() - Procesa la imagen, detecta cubos y muestra los resultados si es necesario.
    
    Atributos:
        - frame (numpy array) - Almacena la imagen de entrada que se va a procesar.
    '''
    def __init__(self, cam_calib_path:str, aruco_dict=cv2.aruco.DICT_4X4_50, marker_length=0.05) -> None:
        '''
        Inicializa la clase y configura los parámetros de Aruco.
            @param aruco_dict (int) - Diccionario de Aruco (por defecto, 4x4 con 50 marcadores).
            @param marker_length (float) - Longitud del lado del marcador en metros.
            @param camera_matrix (numpy array) - Matriz intrínseca de la cámara.
            @param dist_coeffs (numpy array) - Coeficientes de distorsión de la cámara.
        '''
        self.frame = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)
        self.aruco_params = cv2.aruco.DetectorParameters()

        self._get_camara_calibration(cam_calib_path)

        self.marker_length = marker_length
        self.marker_position = None
        self.debug = False

    def _get_camara_calibration(self, path:str)->None:
        with open(path, '+r') as f:
            fichero =  yaml.load(f, yaml.Loader)

        self.camera_matrix = np.array(fichero["camera_matrix"]["data"]).reshape(fichero["camera_matrix"]["rows"], fichero["camera_matrix"]["cols"])
        self.dist_coeffs = np.array(fichero["distortion_coefficients"]["data"])
        

    def _aplicar_filtro_grises(self, frame:np.ndarray) -> np.ndarray:
        ''' 
        Convierte una imagen de color a escala de grises.
            @param frame (numpy array) - Imagen en formato BGR.
            @return gray_frame (numpy array) - Imagen en escala de grises.
        '''
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def _aplicar_filtro_hsv(self, frame:np.ndarray) -> np.ndarray:
        ''' 
        Convierte una imagen de color a espacio de color HSV.
            @param frame (numpy array) - Imagen en formato BGR.
            @return hsv_frame (numpy array) - Imagen en espacio de color HSV.
        '''
        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    def _procesar_umbral_otsu(self, gray:np.ndarray) -> np.ndarray:
        ''' 
        Aplica un umbral de Otsu para binarizar la imagen.
            @param gray (numpy array) - Imagen en escala de grises.
            @return otsu_thresh (numpy array) - Imagen binarizada tras el umbral de Otsu.
        '''
        _, otsu_thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
        #_, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.debug:
            cv2.imshow("Otsu", otsu_thresh)
        kernel = np.ones((3, 3), np.uint8)
        return cv2.morphologyEx(otsu_thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    def _detectar_bordes(self, imagen:np.ndarray) -> np.ndarray:
        ''' 
        Detecta los bordes de una imagen utilizando el filtro de Canny.
            @param imagen (numpy array) - Imagen de entrada (en escala de grises o color).
            @return edges (numpy array) - Imagen con bordes detectados.
        '''
        desenfocada = cv2.GaussianBlur(imagen, (5, 5), 0)
        canny = cv2.Canny(desenfocada, 0, 255)
        
        if self.debug:
            cv2.imshow("Canny", canny)
            
        return canny
            
    
    def _encontrar_contornos(self, edges:np.ndarray) -> list:
        ''' 
        Encuentra los contornos en una imagen binarizada.
            @param edges (numpy array) - Imagen binarizada con bordes detectados.
            @return contours (list) - Lista de contornos encontrados.
        '''
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar los contornos externos que tienen un padre
        filtered_contours = []
        for i, (next_bro, prev_bro, child, parent) in enumerate(hierarchy[0]):
            if next_bro != 0:  # Contorno exterior con padre
                filtered_contours.append(contours[i])

        if self.debug:
            img = self.frame.copy()
            cv2.drawContours(img, filtered_contours, -1, (0,255,0))
            cv2.imshow('Todos los Contornos', img)
        return filtered_contours


    def _identificar_cubo_y_color(self, contours: list, frame: np.ndarray, hsv_frame: np.ndarray, gray: np.ndarray, area_size: int = 1000) -> np.ndarray:
        ''' 
        Identifica cubos en la imagen y les asigna un color basado en el espacio HSV.
        '''
        # Definir el mapa de colores y sus índices numéricos
        color_map = {0: "Red", 1: "Green", 2: "Blue", 3: "Yellow", 4: "Unknown"}
        colores = {0: (0, 0, 255), 1: (0, 255, 0), 2: (255, 0, 0), 3: (0, 255, 255), 4: (205, 205, 205)}  # RGB
        
        resultado = frame.copy()
        dicionario_resultado = []
        
        # Tolerancia para verificar que el rectángulo sea un cuadrado
        tolerancia = 0.2
        mask = np.zeros_like(gray)  # Crear una máscara una sola vez
        
        # Recorrer los contornos y realizar las operaciones necesarias
        for cnt in contours:
            # Calcular el área y el rectángulo mínimo
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            if area < area_size:  # Si el área es demasiado pequeña, lo ignoramos
                continue
            
            # Calcular el rectángulo mínimo y verificar si es un cuadrado
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect).astype(np.int32)
            w, h = rect[1]  # Rectángulo (w, h)
            
            # Verificar si el contorno es un cuadrado
            if abs(w / h - 1) < tolerancia:
                center = tuple(map(int, rect[0]))  # Convertir a enteros
                angle = rect[2]
                
                # Dibujar el centro y el texto con el ángulo
                cv2.circle(resultado, center, 3, (255, 0, 0), -1)
                cv2.putText(resultado, f"Position: {center}", (center[0] + 20, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                cv2.putText(resultado, f"Angle: {angle:.2f}", (center[0] + 20, center[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                # Determinar el color predominante dentro del contorno
                color = self._get_dominant_color(cnt, hsv_frame)
                
                # Dibujar el contorno con el color identificado
                cv2.drawContours(resultado, [box], 0, colores[color], 2)
                
                # Añadir la información al diccionario de resultados
                dicionario_resultado.append({
                    "Position": center,
                    "Angel": angle,
                    "Color": color  # Usar el índice de color directamente
                })
                

        self.imagen_analizada = resultado
        return dicionario_resultado


    def _get_dominant_color(self, contour: np.ndarray, hsv_frame: np.ndarray) -> int:
        ''' 
        Determina el color (rojo, verde, azul y amarillo) predominante dentro de un contorno basado en el espacio de color HSV.
        @param contour (numpy array) - Contorno del que se quiere extraer el color predominante.
        @param hsv_frame (numpy array) - Imagen en espacio HSV.
        @return dominant_color (int) - Índice numérico que representa el color predominante (0=Rojo, 1=Verde, 2=Azul, 3=Amarillo).
        '''
        # Definir los rangos de colores en el espacio HSV
        color_ranges = {
            "Red": [(0, 100, 100), (15, 255, 255)],
            "Green": [(40, 50, 50), (80, 255, 255)],
            "Blue": [(100, 100, 100), (130, 255, 255)],
            "Yellow": [(20, 100, 100), (30, 255, 255)]
        }
        
        # Crear una máscara para la región definida por el contorno
        mask = np.zeros(hsv_frame.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, (255), thickness=cv2.FILLED)
        
        # Crear un diccionario para contar los píxeles de cada color
        color_counts = {color: 0 for color in color_ranges}
        
        # Recorrer cada rango de color y contar los píxeles que están dentro del rango
        for color, (lower, upper) in color_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            
            # Crear la máscara para el color
            color_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
            
            # Aplicar la máscara al área del contorno
            color_mask = cv2.bitwise_and(color_mask, color_mask, mask=mask)
            
            # Contar la cantidad de píxeles del color
            color_counts[color] = cv2.countNonZero(color_mask)
        
        # Determinar el color predominante
        dominant_color = max(color_counts, key=color_counts.get)
        
        # Asignar un valor numérico a cada color
        color_map = {"Red": 0, "Green": 1, "Blue": 2, "Yellow": 3}
        
        return color_map.get(dominant_color, 4)  # Devuelve 4 para "Unknown" si no se encuentra



    
    def _detectar_aruco(self, frame: np.ndarray) -> None:
        '''
        Detecta un marcador Aruco en la imagen y calcula su posición y orientación.
            @param frame (numpy array) - Imagen en formato escala de grises.
        '''
        corners, ids, _ = cv2.aruco.detectMarkers(frame, self.aruco_dict, parameters=self.aruco_params)
        
        if ids is not None:
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # Estimar pose del marcador
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_length, self.camera_matrix, self.dist_coeffs)
            # Guardar la posición del primer marcador detectado
            self.marker_position = tvecs[0]
            frame = cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvecs[0], tvecs[0], 0.1)


    def analizar_imagen(self, frame:np.ndarray, area_size:int=1000, mostrar:bool = False, debug:bool = False) -> list:
        ''' 
        Procesa una imagen para detectar cubos y sus colores, y muestra los resultados.
            @param frame (numpy array) - Imagen de entrada en formato BGR.
            @param area_size (int) - Umbral mínimo de área para considerar un contorno como válido. Por defecto, 2000.
            @param mostrar (bool) - Si es True, muestra la imagen procesada. Por defecto, False.
            @return resultado (list) - Imagen procesada con cubos identificados y etiquetados.
        '''
        self.debug = debug
        # Realizar copia del frame
        self.frame = deepcopy(frame)

        # Detectar Aruco
        self._detectar_aruco(frame)
            
        gray = self._aplicar_filtro_grises(frame)
        hsv_frame = self._aplicar_filtro_hsv(frame)
        morph_clean = self._procesar_umbral_otsu(gray)
        edges = self._detectar_bordes(morph_clean)
        contours = self._encontrar_contornos(edges)
        
        resultado = self._identificar_cubo_y_color(contours, frame, hsv_frame, gray, area_size)

        if mostrar:
            cv2.imshow('Contoured Image', self.imagen_analizada)

            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyAllWindows()

        return resultado

if __name__ == "__main__":
    use_cam = True
    cube_tracker = CubeTracker(cam_calib_path="/home/laboratorio/ros_workspace/src/proyecto_final/data/camera_data/ost.yaml")

    if use_cam:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            _, frame = cam.read()
    else:
        num = 1
        ruta = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Cubos_Exparcidos/Cubos_Exparcidos_{num}.png'
        frame = cv2.imread(ruta)

    resultado = cube_tracker.analizar_imagen(frame, area_size=1000, mostrar=True, debug=True)
    print(resultado)
    if use_cam:
        cam.release()