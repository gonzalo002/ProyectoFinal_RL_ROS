import cv2
import os
import sys

def detectar_camaras():
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"\033[32m--- CAMARA {i} DISPONIBLE ---\033[0m")
            cap.release()


def main():
    # detectar_camaras()
    cam_lateral = cv2.VideoCapture(4)
    cam_top = cv2.VideoCapture(0)
    
    if not cam_lateral.isOpened():
        print("Error: No se pudo abrir el vídeo.")
        return
    
    if os.listdir('/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral') == []:
        i = 0
    else:
        i = len(os.listdir('/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral'))+1
        
    
    while True:
        success_1, frame_lateral = cam_lateral.read()
        success_2, frame_top = cam_top.read()
        
        cv2.imshow('camara_lateral', frame_lateral)
        cv2.imshow('camara_planta', frame_top)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral/Figura_{i}_L.png', frame_lateral)
            cv2.imwrite(f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Superior/Figura_{i}_S.png', frame_top)
            i += 1 
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cam_lateral.release()
            cam_top.release()
            cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()