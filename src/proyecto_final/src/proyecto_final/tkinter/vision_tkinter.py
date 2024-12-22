#!/usr/bin/python3

import os
# Configurar la variable de entorno para que no aparezcan mensajes de error de index de camara
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.font import Font
from tkinter import filedialog
from PIL import Image, ImageTk, Image, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL.ImageTk import PhotoImage
import cv2

from proyecto_final.vision.grupo_2.image_processor_top import ImageProcessor_Top
from proyecto_final.vision.grupo_2.image_processor_front import ImageProcessor_Front
from proyecto_final.vision.grupo_2.cube_tracker import CubeTracker
from proyecto_final.vision.grupo_2.camera_controller import CameraController
from proyecto_final.vision.grupo_2.generacion_figura import FigureGenerator
from geometry2D import Geometry2D

class VisionTab:
    def __init__(self,) -> None:
        # --- ROOT ---
        self.root = ttk.Window(title="Reconstrucción Cubos", themename="custom-vision")
        self.root.resizable(True, True)  # Permitir redimensionar la ventana
        self.root.attributes('-zoomed', True) 
        self.root.attributes('-zoomed', True) 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Definición de clases
        self.ImageProcessorFrontal = ImageProcessor_Front()
        self.ImageProcessorPlanta = ImageProcessor_Top()
        self.CubeLocalizator = CubeTracker("/home/laboratorio/ros_workspace/src/proyecto_final/data/camera_data/ost.yaml")
        self.Geometry3D = FigureGenerator()
        self.Geometry2D = Geometry2D()
        self.camera_controller = CameraController(10)
        
        #Definicion imagenes y varibles
        self.img_front = None
        self.img_plant = None
        self.img_mesa_trabajo = None

        # Definición de Objetos ttk
        self.camera_entry1 = None
        self.camera_entry2 = None
        self.F_input_1 = None
        self.F_input_2 = None

        #Definicion geometria
        self.width = 320
        self.cube_data = []
        
        #Definicion estados del boton
        self.state_procesar = True
        self.state_procesar_xy = True
        
        
        self.estilo()
        self.vision_tab()
        self.root.mainloop()
    
    
    def vision_tab(self):
        self.frame_vision = ttk.Frame(self.root)
        self.frame_vision.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        self.frame_vision.grid_rowconfigure(0, weight=1)
        self.frame_vision.grid_columnconfigure(0, weight=1)
        self.frame_vision.grid_columnconfigure(1, weight=1)

        self.F_col_1 = ttk.Frame(self.frame_vision)
        self.F_col_1.grid(row=0, column=0, sticky="nsew")
        self.F_col_1.grid_rowconfigure(0, weight=1)
        self.F_col_1.grid_rowconfigure(1, weight=2)
        self.F_col_1.grid_rowconfigure(2, weight=2)
        self.F_col_1.grid_columnconfigure(0, weight=1)

        self.F_col_2 = ttk.Frame(self.frame_vision)
        self.F_col_2.grid(row=0, column=1, sticky="nsew")
        self.F_col_2.grid_rowconfigure(0, weight=1)
        self.F_col_2.grid_rowconfigure(1, weight=1)
        self.F_col_2.grid_columnconfigure(0, weight=1)

        self._primera_fila()
        self._fila_camaras()
        self._fila_ws()
        self._fila_3D()
        self._fila_2D()

        # Subpestaña: Detección de Cubos
        self._update_3D_file_images()
        self.update_camera_geometry_2D()
        self.toggle_mode()


    def _primera_fila(self):

        # --- FRAME: Primera fila ---
        self.F_primera_fila = ttk.Frame(self.F_col_1)
        self.F_primera_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=5)
        self.F_primera_fila.grid_rowconfigure(0, weight=1)
        self.F_primera_fila.grid_columnconfigure(0, weight=1)
        self.F_primera_fila.grid_columnconfigure(1, weight=1)

        self.LF_primera_col = ttk.LabelFrame(self.F_primera_fila, text="  Modo Funcionamiento  ")
        self.LF_primera_col.grid(row=0, column=0, sticky="nsew", padx=[0,10], pady=0)
        self.LF_primera_col.grid_rowconfigure(0, weight=1)
        self.LF_primera_col.grid_columnconfigure(0, weight=1)


        self.F_primera_col = ttk.Frame(self.LF_primera_col)
        self.F_primera_col.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_primera_col.grid_rowconfigure(0, weight=1)
        self.F_primera_col.grid_columnconfigure(0, weight=2)
        self.F_primera_col.grid_columnconfigure(1, weight=1)
        self.F_primera_col.grid_columnconfigure(2, weight=2)

        # --- ELEMENTS ---
        # Text MANUAL
        self.L_camOFF = ttk.Label(self.F_primera_col, text="CAMARA OFF" )
        self.L_camOFF.grid(row=0, column=0, sticky="e", padx=[0, 10])

            # Checkbutton
        self.V_modo = ttk.IntVar()  # Variable para el estado del Checkbutton
        self.CB_modo = ttk.Checkbutton(
            self.F_primera_col,
            variable=self.V_modo,
            command=self.toggle_mode,
            bootstyle="primary-round-toggle")
        self.CB_modo.grid(row=0, column=1)

        # Text MANUAL
        self.L_camON = ttk.Label(self.F_primera_col, text="CAMARA ON" )
        self.L_camON.grid(row=0, column=2, sticky="w", padx=[10, 0])

        # --- SEGUNDA COLUMNA ---
        self.LF_segunda_col = ttk.LabelFrame(self.F_primera_fila, text="  Control de las Cámaras  ")
        self.LF_segunda_col.grid(row=0, column=1, sticky="nsew", padx=[10,0], pady=0)
        self.LF_segunda_col.grid_rowconfigure(0, weight=1)
        self.LF_segunda_col.grid_columnconfigure(0, weight=1)


        self.F_segunda_col= ttk.Frame(self.LF_segunda_col)
        self.F_segunda_col.grid(row=0, column=0, sticky="nsew",padx=0, pady=0)
        self.F_segunda_col.grid_rowconfigure(0, weight=1)
        self.F_segunda_col.grid_columnconfigure(0, weight=1)
        
        self.B_ActualizarCam = ttk.Button(self.F_segunda_col, 
                                 text="ACTUALIZAR CAMARAS",
                                 bootstyle="warning",
                                 command=self.update_cameras)
        self.B_ActualizarCam.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
         

    def _fila_camaras(self):
        # --- FRAME ---
        # Label Frame
        self.LF_segunda_fila = ttk.LabelFrame(self.F_col_1, text="  Visualización Cámaras  ")
        self.LF_segunda_fila.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_segunda_fila.grid_rowconfigure(0, weight=1)
        self.LF_segunda_fila.grid_columnconfigure(0, weight=1)

        # Inner Frame
        self.F_segunda_fila = ttk.Frame(self.LF_segunda_fila)
        self.F_segunda_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_segunda_fila.grid_rowconfigure(0, weight=1)
        self.F_segunda_fila.grid_columnconfigure(0, weight=1)
        self.F_segunda_fila.grid_columnconfigure(1, weight=1)

        # --- ELEMENTS ---
        # Image Frame 1
        self.F_image_1 = ttk.Frame(self.F_segunda_fila)
        self.F_image_1.grid_rowconfigure(0, weight=1)
        self.F_image_1.grid_rowconfigure(1, weight=1)
        self.F_image_1.grid_rowconfigure(2, weight=1)
        self.F_image_1.grid_columnconfigure(0, weight=1)
        self.F_image_1.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.F_image_1,text="CÁMARA SUPERIOR", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        self.L_img_top = ttk.Label(self.F_image_1)
        self.L_img_top.grid(row=1, column=0, sticky="N")


        # Image Frame 2
        self.F_image_2 = ttk.Frame(self.F_segunda_fila)
        self.F_image_2.grid_rowconfigure(0, weight=1)
        self.F_image_2.grid_rowconfigure(1, weight=1)
        self.F_image_2.grid_rowconfigure(2, weight=1)
        self.F_image_2.grid_columnconfigure(0, weight=1)
        self.F_image_2.grid(row=0, column=1, sticky="nsew")

        ttk.Label(self.F_image_2,text="CÁMARA LATERAL", 
                  font=("Montserrat SemiBold", 10),
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        
        self.L_img_front = ttk.Label(self.F_image_2)
        self.L_img_front.grid(row=1, column=0, sticky="N")

    
        self.process_button = ttk.Button(
            self.F_segunda_fila,
            text="PROCESAR",
            command=self.process_images,  # Función para procesar las imágenes
            bootstyle="secondary",  # Estilo del botón
        )
        self.process_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(
            self.F_segunda_fila,
            text="BORRAR",
            state = ttk.DISABLED,
            command=self.clear_images,  # Función para procesar las imágenes
            bootstyle="danger-outline",  # Estilo del botón
        )
        self.clear_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    def _fila_ws(self):
        # --- FRAME ---
        # Label Frame
        self.LF_tercera_fila = ttk.LabelFrame(self.F_col_1, text="  Mesa de Trabajo  ")
        self.LF_tercera_fila.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_tercera_fila.grid_rowconfigure(0, weight=1)
        self.LF_tercera_fila.grid_columnconfigure(0, weight=1)

        # Inner Frame
        self.F_tercera_fila = ttk.Frame(self.LF_tercera_fila)
        self.F_tercera_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_tercera_fila.grid_rowconfigure(0, weight=1)
        self.F_tercera_fila.grid_columnconfigure(0, weight=1)
        self.F_tercera_fila.grid_columnconfigure(1, weight=3)

        self._col_ws_1()
        self._col_ws_2()


    def _col_ws_1(self):
        self.F_ws_col_1 = ttk.Frame(self.F_tercera_fila)
        self.F_ws_col_1.grid(row=0, column=0, sticky="nsew")
        self.F_ws_col_1.grid_rowconfigure(0, weight=1)
        self.F_ws_col_1.grid_columnconfigure(0, weight=1)

        self.L_img_ws = ttk.Label(self.F_ws_col_1)
        self.L_img_ws.grid(row=0, column=0)
    
    def _col_ws_2(self):
        # --- FRAME ---
        self.F_ws_col_2 = ttk.Frame(self.F_tercera_fila)
        self.F_ws_col_2.grid(row=0, column=1, sticky="nsew")
        self.F_ws_col_2.grid_rowconfigure(0, weight=1)
        self.F_ws_col_2.grid_rowconfigure(1, weight=1)
        self.F_ws_col_2.grid_rowconfigure(2, weight=1)
        self.F_ws_col_2.grid_columnconfigure(0, weight=1)
        
        self.CB_cam_ws = ttk.Combobox(self.F_ws_col_2, 
                                          values=self.camera_controller.camera_names,
                                          font=("Montserrat", 10))
        self.CB_cam_ws.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        if len(self.camera_controller.cameras) > 0:
            self.CB_cam_ws.set(self.camera_controller.camera_names[0])

        self.xy_process_button = ttk.Button(
            self.F_ws_col_2,
            text="PROCESAR",
            command=self.xy_process_images,   # Función para procesar las imágenes
            bootstyle="secondary",
        )
        self.xy_process_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10,)
        
        self.xy_clear_button = ttk.Button(
            self.F_ws_col_2,
            text="Borrar",
            state = ttk.DISABLED,
            command=self.xy_clear_images,  # Función para procesar las imágenes
            bootstyle="warning", 
        )
        self.xy_clear_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)


    def _fila_3D(self):
        # --- FRAME ---
        # Label Frame
        self.LF_3d_fila = ttk.LabelFrame(self.F_col_2, text="  Representación 3D de Figura  ")
        self.LF_3d_fila.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_3d_fila.grid_rowconfigure(0, weight=1)
        self.LF_3d_fila.grid_columnconfigure(0, weight=1)

        # --- ELEMENTS ---
        fig_3d = self.Geometry3D.generate_figure_from_matrix(np.full((5,5),-1), 
                                                             np.full((5,5),-1), 
                                                             paint=True,
                                                             tkinter=True)
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.LF_3d_fila)
        self.canvas_3d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

    def _fila_2D(self):
        # --- FRAME ---
        # Label Frame
        self.LF_2d_fila = ttk.LabelFrame(self.F_col_2, text="  Representación 3D de Figura  ")
        self.LF_2d_fila.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_2d_fila.grid_rowconfigure(0, weight=1)
        self.LF_2d_fila.grid_columnconfigure(0, weight=1)

        # --- ELEMENTS ---
        fig_2d = self.Geometry2D.draw_2d_space([], True)
        self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.LF_2d_fila)
        self.canvas_2d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

    def toggle_mode(self):
        """Maneja el cambio de estado del Checkbutton"""
        # Limpia filas específicas para evitar superposiciones
        for widget in self.frame_vision.grid_slaves():
            if int(widget.grid_info()["row"]) > 2:
                widget.destroy()

        if self.V_modo.get() == 1:
            self.L_camOFF.config(font=("Montserrat", 10), foreground="#474B4E")
            self.L_camON.config(font=("Montserrat", 10, "bold"), foreground="#5eaae8")
            self.camera_inputs()
            self.start_camera()

        else:
            self.L_camOFF.config(font=("Montserrat", 10, "bold"), foreground="#5eaae8")
            self.L_camON.config(font=("Montserrat", 10), foreground="#474B4E")
            self.stop_camera()
            self.file_inputs()
            self._update_3D_file_images()

    def camera_inputs(self):
        """Elimina los campos de entrada y botones para cargar imágenes"""
        if self.F_input_1 is not None:
            self.F_input_1.destroy()
        if self.F_input_2 is not None:
            self.F_input_2.destroy()
        
        self.F_input_1 = ttk.Frame(self.F_image_1, width=320)
        self.F_input_1.grid_columnconfigure(0, weight=1)
        self.F_input_1.grid_rowconfigure(0, weight=1)
        self.F_input_1.grid(row=2, column=0)
        self.camera_entry1 = ttk.Combobox(self.F_input_1,
                                          values=self.camera_controller.camera_names,
                                          font=("Montserrat", 10),
                                          width=33)
        self.camera_entry1.grid(row=0, column=0, padx=0, pady=0,sticky="nsew")
        if len(self.camera_controller.cameras) > 0:
            self.camera_entry1.set(self.camera_controller.camera_names[0])
        
        self.F_input_2 = ttk.Frame(self.F_image_2, width=320)
        self.F_input_2.grid_columnconfigure(0, weight=1)
        self.F_input_2.grid_rowconfigure(0, weight=1)
        self.F_input_2.grid(row=2, column=0)
        self.camera_entry2 = ttk.Combobox(self.F_input_2,
                                          values=self.camera_controller.camera_names,
                                          font=("Montserrat", 10),
                                          width=33)
        self.camera_entry2.grid(row=0, column=0)
        if len(self.camera_controller.cameras) > 1:
            self.camera_entry2.set(self.camera_controller.camera_names[1])
        
    def file_inputs(self):
        """Crea los campos de entrada y botones para cargar imágenes"""
        if self.F_input_1 is not None:
            self.F_input_1.destroy()
        if self.F_input_2 is not None:
            self.F_input_2.destroy()
        
        self.F_input_1 = ttk.Frame(self.F_image_1, width=320)
        self.F_input_1.grid_columnconfigure(0, weight=1)
        self.F_input_1.grid_columnconfigure(1, weight=1)
        self.F_input_1.grid_rowconfigure(0, weight=1)
        self.F_input_1.grid(row=2, column=0)

        self.E_input_1 = ttk.Entry(self.F_input_1, width=25, font=("Montserrat", 10), bootstyle="dark")
        self.E_input_1.grid(row=0, column=0, padx=[0,10], sticky="nsew")
        self.E_input_1.delete(0, END)
        self.E_input_1.configure(foreground="#5a5a5a")
        self.E_input_1.state([ttk.DISABLED])

        self.B_browse_1 = ttk.Button(
            self.F_input_1,
            text="Buscar...",
            command=lambda: self.load_save_frame("img_plant", self.E_input_1, self.L_img_top),
        )
        self.B_browse_1.grid(row=0, column=1, sticky="nsew")

        self.F_input_2 = ttk.Frame(self.F_image_2, width=320)
        self.F_input_2.grid_columnconfigure(0, weight=1)
        self.F_input_2.grid_columnconfigure(1, weight=1)
        self.F_input_2.grid_rowconfigure(0, weight=1)
        self.F_input_2.grid(row=2, column=0)

        self.E_input_2 = ttk.Entry(self.F_input_2, width=25, font=("Montserrat", 10), bootstyle="dark")
        self.E_input_2.grid(row=0, column=0, padx=[0,10], sticky="nsew")
        self.E_input_2.delete(0, END)
        self.E_input_2.state([ttk.DISABLED])
        self.E_input_2.configure(foreground="#5a5a5a")

        self.B_browse_2 = ttk.Button(
            self.F_input_2,
            text="Buscar...",
            command=lambda: self.load_save_frame("img_front", self.E_input_2, self.L_img_front),
        )
        self.B_browse_2.grid(row=0, column=1, sticky="nsew")
    
    def start_camera(self):
        self.camera_active = True
        self.camera_feed_geometry_3D()
    
    def stop_camera(self):
        """Detiene el feed de la cámara."""
        self.camera_active = False
        self.camera_feed_geometry_3D()
        

    def _update_camera(self, camera_index, aspect_ratio:float=0.5):
        frame = self.camera_controller.get_frame(camera_index)

        if frame is not None:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = self._resize_image(img, aspect_ratio)
            imgtk = ImageTk.PhotoImage(image=img)
        else:
            imgtk = self._create_image_with_text("Cámara NO encontrada", aspect_ratio)
        
        return imgtk, frame
    
    def camera_feed_geometry_3D(self):
        if self.camera_active:
            if self.state_procesar:
                if self.camera_entry1.get() != '':
                    index = self.camera_controller.camera_names.index(self.camera_entry1.get())
                    imgtk, frame = self._update_camera(index)

                else:
                    imgtk = self._create_image_with_text("Cámara NO encontrada")
                    frame = None

                self.img_plant = frame
                self.L_img_top.config(image=imgtk)
                self.L_img_top.image = imgtk
                self.L_img_top.update()
                
                if self.camera_entry2.get() != '':
                    index = self.camera_controller.camera_names.index(self.camera_entry2.get())
                    imgtk, frame = self._update_camera(index)

                else:
                    imgtk = self._create_image_with_text("Cámara NO encontrada")
                    frame = None

                self.img_front = frame
                self.L_img_front.config(image=imgtk)
                self.L_img_front.image = imgtk
                self.L_img_front.update()

            # Es como un hilo, se llama a sí misma después de 10ms
            self.root.after(10, self.camera_feed_geometry_3D)
    

    def update_camera_geometry_2D(self):
        """Actualiza el feed de la cámara y lo muestra en el Label."""
        if self.state_procesar_xy:
            if self.CB_cam_ws.get() != '':
                index = self.camera_controller.camera_names.index(self.CB_cam_ws.get())
                imgtk, frame = self._update_camera(index, 0.8)

            else:
                imgtk = self._create_image_with_text("Cámara NO encontrada", 0.8)
                frame = None

            self.img_ws = frame
            self.L_img_ws.config(image=imgtk)
            self.L_img_ws.image = imgtk
            self.L_img_ws.update()
            
            self.camera_feed_job_3 = self.root.after(12, self.update_camera_geometry_2D)
        else:
            if self.camera_feed_job_3 is not None:
                self.root.after_cancel(self.camera_feed_job_3)
                self.camera_feed_job_3 = None
            
    def load_save_frame(self, img_name, entry:ttk.Entry, label):
        loaded_image = self._load_file(entry, label)
        setattr(self, img_name, loaded_image) 

    def _load_file(self, entry:ttk.Entry, label:ttk.Label):
        """Permite seleccionar un archivo y actualizar la imagen correspondiente"""
        file_path = filedialog.askopenfilename(
            initialdir="/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp *.gif"),
                       ("Todos los archivos", "*.*")])
        if file_path:
            try:
                directorio_padre = os.path.dirname(file_path)
                nombre_archivo = os.path.basename(file_path)
                ultimo_directorio = os.path.basename(directorio_padre)

                entry.state(["!disabled"])
                entry.delete(0, END)
                entry.insert(0, f".../{ultimo_directorio}/{nombre_archivo}")
                entry.state([ttk.DISABLED])

                # Actualizar la imagen
                frame = cv2.imread(file_path)
                image = Image.open(file_path)

                # Mantener la anchura constante (320) y ajustar la altura proporcional
                aspect_ratio = image.height / image.width
                height = int(self.width * aspect_ratio)
                image = image.resize((self.width, height))

                # Crear objeto PhotoImage y actualizar la etiqueta con la nueva imagen
                photo = ImageTk.PhotoImage(image)
                label.config(image=photo)
                label.image = photo

            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
        
            return frame
        
        return self._create_image_with_text("CARGAR IMAGEN", 0.8)

    def xy_process_images(self):
        if self.img_ws is not None:
            self.xy_process_button.state([ttk.DISABLED])
            self.xy_clear_button.state(["!disabled"])
            self.state_procesar_xy = False
            self.update_camera_geometry_2D()
            

            img_ws_processed, coordenadas = self.CubeLocalizator.process_image(self.img_ws, area_size=1000)
            #self.aruco_pose = self.CubeLocalizator.aruco_corner_pos

            #Resize
            img_ws_processed = Image.fromarray(cv2.cvtColor(img_ws_processed, cv2.COLOR_BGR2RGB))
            photo1 = self._resize_image(img_ws_processed, 0.8)

            photo1 = ImageTk.PhotoImage(photo1)
            self.L_img_ws.config(image=photo1)
            self.L_img_ws.image = photo1

            # Actualizar canvas_3d
            if hasattr(self, "canvas_2d"):
                self.canvas_2d.get_tk_widget().destroy()

            fig_2d = self.Geometry2D.draw_2d_space([], True)
            self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.LF_2d_fila)
            self.canvas_2d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
    
    def _expand_corners(self, corners, factor=1.2):
        """
        Expande las esquinas del marcador ArUco aumentando su tamaño.
        :param corners: Esquinas de los marcadores detectados (forma de (1, 4, 2)).
        :param factor: Factor de escala para aumentar o reducir el tamaño del marcador.
        :return: Nuevas coordenadas de las esquinas ajustadas.
        """
        expanded_corners = []

        for corner in corners:
            # corner es un array de 4 puntos del marcador, por ejemplo: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            
            # Calcular el centro del marcador como el promedio de las 4 esquinas
            centro = np.mean(corner, axis=0)  # El centro es el promedio de los puntos

            # Crear una lista para las nuevas coordenadas ajustadas
            new_corners = []

            # Ajustar las esquinas en función del factor
            for point in corner:
                # Calcular el vector desde el centro hacia la esquina
                vector = point - centro
                # Ajustar el tamaño del vector con el factor
                new_point = centro + vector * factor  # Escalar el vector para aumentar el tamaño
                # Añadir el nuevo punto a la lista de esquinas ajustadas
                new_corners.append(new_point)

            # Convertir a tipo entero (por si acaso) y agregar el marcador ajustado a la lista final
            expanded_corners.append(np.array(new_corners, dtype=np.int32))

        return expanded_corners
    
    def process_images(self):
        """Procesa las imágenes y las muestra en los labels"""
        # Verifica que ambas imágenes estén cargadas
        if self.img_front is not None and self.img_plant is not None:
            self.process_button.state([ttk.DISABLED])
            self.clear_button.state(["!disabled"])

            self.state_procesar = False

            front_matrix, img_procesed_front = self.ImageProcessorFrontal.process_image(self.img_front)
            plant_matrix, img_procesed_plant = self.ImageProcessorPlanta.process_image(self.img_plant)

            #Resize
            img_procesed_front = Image.fromarray(cv2.cvtColor(img_procesed_front, cv2.COLOR_BGR2RGB))
            img_procesed_plant = Image.fromarray(cv2.cvtColor(img_procesed_plant, cv2.COLOR_BGR2RGB))
            photo1 = self._resize_image(img_procesed_plant)
            photo2 = self._resize_image(img_procesed_front)

            photo1 = ImageTk.PhotoImage(photo1)
            self.L_img_top.config(image=photo1)
            self.L_img_top.image = photo1

            photo2 = ImageTk.PhotoImage(photo2)
            self.L_img_front.config(image=photo2)
            self.L_img_front.image = photo2


            if hasattr(self, "canvas_3d"):
                self.canvas_3d.get_tk_widget().destroy()

            fig_3d = self.Geometry3D.generate_figure_from_matrix(plant_matrix, front_matrix, paint=True, tkinter=True)
            self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.LF_3d_fila)
            self.canvas_3d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

    def _resize_image(self, img:Image.Image, aspect_ratio:float=0.5):
        img_size = (int(img.width * aspect_ratio), int(img.height * aspect_ratio))
        return img.resize(img_size)    
    
    def clear_images(self):
        self.clear_button.state([ttk.DISABLED])
        self.process_button.state(["!disabled"])
        if self.V_modo == 1:
            self.B_browse_1.state(["!disabled"])
            self.B_browse_2.state(["!disabled"])
        self.state_procesar = True

        # --- VACIAR MATRIZ ---
        if hasattr(self, "canvas_3d"):
            self.canvas_3d.get_tk_widget().destroy()

        fig_3d = self.Geometry3D.generate_figure_from_matrix(np.full((5,5),-1), 
                                                             np.full((5,5),-1),
                                                             paint=True, 
                                                             tkinter=True)
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.LF_3d_fila)
        self.canvas_3d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
            
        self.toggle_mode()
    
    def xy_clear_images(self):
        self.xy_clear_button.state([ttk.DISABLED])
        self.xy_process_button.state(["!disabled"])
        self.state_procesar_xy = True

        # --- VACIAR MATRIZ ---
        if hasattr(self, "canvas_2d") and self.canvas_2d is not None:
            self.canvas_2d.get_tk_widget().destroy()

        fig_2d = self.Geometry2D.draw_2d_space([], True)

        self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.LF_2d_fila)
        self.canvas_2d.get_tk_widget().pack(padx=0, pady=0)
        
        self.update_camera_geometry_2D()

    def update_cameras(self):
        self.camera_controller.stop()
        self.camera_controller.start(10)
        if self.camera_controller.camera_names != []:
            self.camera_entry1['values'] = self.camera_controller.camera_names
            self.camera_entry2['values'] = self.camera_controller.camera_names
            self.CB_cam_ws['values'] = self.camera_controller.camera_names
        self.camera_feed_geometry_3D()
        self.update_camera_geometry_2D()
        
        
# Función para actualizar las imágenes en la interfaz
    def _update_3D_file_images(self):
        img1 = self._create_image_with_text("CARGAR IMAGEN")
        img2 = self._create_image_with_text("CARGAR IMAGEN")
        

        # Actualizar las etiquetas en la interfaz
        self.L_img_top.config(image=img1)
        self.L_img_top.image = img1

        self.L_img_front.config(image=img2)
        self.L_img_front.image = img2


    def _create_image_with_text(self, text, aspect_ratio:float=0.5):

        img_size = (int(640 * aspect_ratio), int(480 * aspect_ratio))

        # Crear una imagen negra de tamaño 320x240
        image = Image.new('RGB', img_size, color='black')
        
        # Crear un objeto para dibujar en la imagen
        draw = ImageDraw.Draw(image)
        
        # Establecer el texto y su color
        text_color = (255, 255, 255)  # Blanco
        
        # Intentar cargar una fuente del sistema o usar una por defecto
        try:
            font = ImageFont.truetype("C:/Users/itsas/AppData/Local/Microsoft/Windows/Fonts/Montserrat-Regular.ttf", 20)  # Usa una fuente si está disponible
        except IOError:
            font = ImageFont.load_default()  # Si no se encuentra, usa la fuente predeterminada
        
        # Calcular el tamaño del texto y su posición para centrarlo
        text_bbox = draw.textbbox((0, 0), text, font=font)  # Obtiene las dimensiones del texto
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        position = ((img_size[0] - text_width) // 2, (img_size[1] - text_height) // 2)
        
        # Dibujar el texto en la imagen
        draw.text(position, text, font=font, fill=text_color)
        
        # Convertir la imagen a un formato compatible con tkinter
        tk_image = PhotoImage(image, master=self.root)
        
        return tk_image
    
    def estilo(self):
        style = ttk.Style()
        style.configure("Custom.TNotebook.Tab",
            font= ("Montserrat Medium", 12), 
            background= "white",
            )

        style.configure("Custom.TNotebook",
            background= "white",
            )

        style.configure("Custom.TFrame",
            font= ("Montserrat Medium", 12), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", "#8C85F7"), ("active", "#8C85F7"), ("!selected", "white")],     # Background color when hovered
            foreground=[("selected", "black"), ("active", "black"), ("!selected", "black")],   # Text color when hovered
        )

        style.configure("Vision.TNotebook.Tab",
            font= ("Montserrat Medium", 10), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.configure("Vision.TNotebook",
            background= "white",
            borderwidth=0
            )

        style.configure("Custom.TFrame",
            font= ("Montserrat Medium", 12), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.map(
            "Vision.TNotebook.Tab",
            background=[("selected", "#C5C1F7"), ("active", "#C5C1F7"), ("!selected", "white")],     # Background color when hovered
            foreground=[("selected", "black"), ("active", "black"), ("!selected", "black")],   # Text color when hovered
        )

        style.configure(
        "TCheckbutton",  # Nombre del estilo
        font=("Montserrat", 10),  # Fuente personalizada
        )

        style.configure(
        "TButton",  # Nombre del estilo
        font=("Montserrat", 10),  # Fuente personalizada
        )

        style.configure(
        "TLabelframe.Label",  # Nombre del estilo
            font=("Montserrat", 10),
        )
    
    def _on_closing(self):
        """Esta función se ejecuta cuando la ventana se cierra."""
        self.camera_controller.stop()
        
        # Cerrar la ventana de Tkinter
        self.root.destroy()
        exit()
            
if __name__ == "__main__":
    VisionTab()