import cv2
import os
import sys

colores = {
    "rojo": "\033[31m",      # Rojo
    "verde": "\033[32m",     # Verde
    "amarillo": "\033[33m",  # Amarillo
    "azul": "\033[34m",      # Azul
    "magenta": "\033[35m",   # Magenta
    "cian": "\033[36m",      # Cian
    "blanco": "\033[37m",    # Blanco
    "reset": "\033[0m"       # Restablecer al color predeterminado
}

def detectar_camaras():
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"\033[32m--- CAMARA {i} DISPONIBLE ---\033[0m")
            cap.release()


def main():
    # detectar_camaras()
    save_xy = True
    
    cam_lateral = cv2.VideoCapture(4)
    cam_top = cv2.VideoCapture(0)
    
    if not cam_lateral.isOpened():
        print("Error: No se pudo abrir el vídeo.")
        return
    
    if save_xy:
        i = len(os.listdir('/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Cubos_Exparcidos'))+1
        
    else:
        i = len(os.listdir('/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral'))+1
        
    if save_xy:
        while True:
            success_2, frame_top = cam_top.read()
            
            cv2.imshow('camara_planta', frame_top)
            
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite(f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Cubos_Exparcidos/Cubos_Exparcidos_{i}.png', frame_top)
                print(f"{colores['verde']}--- IMAGEN GUARDADA ---{colores['reset']}")
                i += 1 
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cam_lateral.release()
                cam_top.release()
                cv2.destroyAllWindows()
    else:
        while True:
            _, frame_lateral = cam_lateral.read()
            _, frame_top = cam_top.read()
            
            cv2.imshow('camara_lateral', frame_lateral)
            cv2.imshow('camara_planta', frame_top)
            
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite(f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral/Figura_{i}_L.png', frame_lateral)
                cv2.imwrite(f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Superior/Figura_{i}_S.png', frame_top)
                print(f"{colores['verde']}--- IMAGEN GUARDADA ---q")
                i += 1 
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cam_lateral.release()
                cam_top.release()
                cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()