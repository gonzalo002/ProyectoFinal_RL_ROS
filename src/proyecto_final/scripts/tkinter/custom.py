#!/usr/bin/python3

import os
# Configurar la variable de entorno para que no aparezcan mensajes de error de index de camara
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.font import Font
from tkinter import filedialog, IntVar
from PIL import Image, ImageTk, Image, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from PIL.ImageTk import PhotoImage
import cv2

from image_processor_top import ImageProcessor_Top
from image_processor_front import ImageProcessor_Front
from cube_tracker import CubeTracker
from camera_controller import CameraController
from geometry import FigureGenerator
#from TKINTER.camera_controller import CameraController

class DynamicTabsApp:
    def __init__(self):
        self.root = ttk.Window(title="Reconstrucción Cubos", themename="vision")
        self.root.resizable(True, True)  # Permitir redimensionar la ventana
        self.root.attributes('-zoomed', True) 
        self.root.attributes('-zoomed', True) 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.camera_mode = IntVar(value=0)

        #Definicion clases
        self.ImageProcessorFrontal = ImageProcessor_Front()
        self.ImageProcessorPlanta = ImageProcessor_Top()
        self.CubeLocalizator = CubeTracker("/home/laboratorio/ros_workspace/src/proyecto_final/data/camera_data/ost.yaml")
        self.FigureGenerator = FigureGenerator()


        #Definicion camara
        self.camera_controller = CameraController(10)

        #Definicion geometria
        self.plant_matrix = np.full((5,5), -1)
        self.side_matrix = np.full((5,5), -1)
        self.width = 320
        

        #Definicion imagenes y varibles
        self.img_front = None
        self.img_plant = None
        self.img_mesa_trabajo = None
        self.camera_entry1 = None
        self.camera_entry2 = None

        #Definicion estados del boton
        self.state_procesar = True
        
        #Al finalizar
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Crear un notebook (pestañas)
        self.estilo()
        self.create_notebook()
        self.vision_tab()
        self.root.mainloop()

    
    def create_notebook(self):
        self.tabs = ["Visión", "Robótica", "Reinforcement Learning"]
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook", padding=[10,10])
        self.notebook.pack(fill="both", expand=True)
        self._adjust_tab_titles(("Montserrat Medium", 12))

        self.tab_vision = ttk.Frame(self.notebook, style = "Custom.TFrame", padding=[10,10], relief='flat')
        self.notebook.add(self.tab_vision, text=self.tabs[0])

        tab_robotics = ttk.Frame(self.notebook, relief='flat')
        self.notebook.add(tab_robotics, text=self.tabs[1])

        tab_rl = ttk.Frame(self.notebook, relief='flat')
        self.notebook.add(tab_rl, text=self.tabs[2])
    
    def create_notebook_2(self):
        self.tabs = ["Procesado de Figura", "Detección de Cubos"]
        self.notebook = ttk.Notebook(self.tab_vision, style="Vision.TNotebook", padding=[1,1])
        self.notebook.pack(fill="both", expand=True)
        self._adjust_tab_titles(("Montserrat Medium", 10))

        self.tab_vision_figure = ttk.Frame(self.notebook, style = "Custom.TFrame", padding=[0,0], borderwidth=0)
        self.notebook.add(self.tab_vision_figure, text=self.tabs[0])

        self.tab_vision_cubes = ttk.Frame(self.notebook, borderwidth=0)
        self.notebook.add(self.tab_vision_cubes, text=self.tabs[1])


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


    
    def vision_tab(self):
        #self.create_notebook_2()

        # Crear un Frame para organizar los elementos dentro de la pestaña "Procesado de Figura"
        self.frame_vision = ttk.Frame(self.tab_vision, borderwidth=0)
        self.frame_vision.pack(fill="both", expand=True)

        #Configuración grid
        self.frame_vision.grid_columnconfigure(0, weight=2)
        self.frame_vision.grid_columnconfigure(1, weight=1)
        self.frame_vision.grid_columnconfigure(2, weight=4)
        

        

        
        # --- CHECK BUTTON ---
 
        self.camera_check_var = ttk.IntVar()  # Variable para el estado del Checkbutton
        self.camera_check = ttk.Checkbutton(
            self.frame_vision,
            text="Usar Cámara",
            variable=self.camera_check_var,
            
            command=self.toggle_mode,  # Función para manejar el cambio
        )
        self.camera_check.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.update_camera_button = ttk.Button(
            self.frame_vision,
            text="ACTUALIZAR CÁMARAS",
            command=self.update_cameras,  # Función para procesar las imágenes
            bootstyle="warning",  # Estilo del botón
            padding = [20,5]
        )
        self.update_camera_button.grid(row=0, column=0, columnspan=2, padx=[200,0], pady=10, sticky="nw")

        # --- IMAGE LABEL FRAME ---
        self.label_frame = ttk.LabelFrame(self.frame_vision, text="Imágenes")
        self.label_frame.grid(row=1, column=0, padx=[10,90], pady=10,  sticky="nsew")

        self.image1_frame = ttk.Frame(self.label_frame)
        self.image1_frame.grid_columnconfigure(0, weight=1)
        self.image1_frame.grid_columnconfigure(1, weight=1)
        self.image1_frame.grid_columnconfigure(2, weight=1)
        self.image1_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="NW")
        titulo = ttk.Label(self.image1_frame,text="Cámara Superior", font=("Montserrat SemiBold", 10))
        titulo.grid(row=0, column=0, columnspan=3, pady=[0,5],sticky="N")
        self.lbl_vision_figure1 = ttk.Label(self.image1_frame)
        self.lbl_vision_figure1.grid(row=1, column=0, columnspan=3)

        self.image2_frame = ttk.Frame(self.label_frame)
        self.image2_frame.grid_columnconfigure(0, weight=1)
        self.image2_frame.grid_columnconfigure(1, weight=1)
        self.image2_frame.grid_columnconfigure(2, weight=1)
        self.image2_frame.grid(row=1, column=3, columnspan=3, padx=10, pady=10, sticky="NW")
        titulo = ttk.Label(self.image2_frame,text="Cámara Lateral", font=("Montserrat SemiBold", 10))
        titulo.grid(row=0, column=0, columnspan=3, pady=[0,5],sticky="N")
        self.lbl_vision_figure2 = ttk.Label(self.image2_frame)
        self.lbl_vision_figure2.grid(row=1, column=0, columnspan=3)

        self.process_button = ttk.Button(
            self.label_frame,
            text="Procesar",
            command=self.process_images,  # Función para procesar las imágenes
            bootstyle="info",  # Estilo del botón
        )
        self.process_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(
            self.label_frame,
            text="Borrar",
            state = ttk.DISABLED,
            command=self.clear_images,  # Función para procesar las imágenes
            bootstyle="warning",  # Estilo del botón
        )
        self.clear_button.grid(row=3, column=3, columnspan=3, padx=10, pady=10, sticky="nsew")


        # --- GEOMETRY LABEL FRAME ---
        self.geometry_frame = ttk.LabelFrame(self.frame_vision, text="Geometría")
        self.geometry_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        fig_3d = self.FigureGenerator.generate_figure_from_matrix(self.plant_matrix, self.side_matrix, True)

        # Mostrar la figura 3D en el canvas
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.geometry_frame)
        self.canvas_3d.get_tk_widget().pack(padx=0, pady=0)

        # --- MESA DE TRABAJO ---
        self.label_frame_2 = ttk.LabelFrame(self.frame_vision, text="Mesa de Trabajo")
        self.label_frame_2.grid(row=2, column=0, padx=[10,90], pady=10,  sticky="nsew")
        
        

        self.lbl_vision_figure3 = ttk.Label(self.label_frame_2)
        self.lbl_vision_figure3.grid(row=0, rowspan=10, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        self.camera_entry3 = ttk.Combobox(self.label_frame_2,values=self.camera_controller.camera_names,  font=("Montserrat", 10))
        self.camera_entry3.grid(row=0, column=5, columnspan=2, padx=[10,0], pady=10, sticky="nsew")
        if len(self.camera_controller.cameras) > 0:
            self.camera_entry3.set(self.camera_controller.camera_names[0])
            


        # --- GEOMETRY LABEL FRAME ---
        self.geometry_2d_frame = ttk.LabelFrame(self.frame_vision, text="Espacio")
        self.geometry_2d_frame.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

        cube_data = [
            {'x': 0, 'y': 0, 'color': 0},   # Cubo rojo en (0, 0)
            {'x': 5, 'y': 0, 'color': 1},   # Cubo verde en (5, 0)
            {'x': 10, 'y': 5, 'color': 2},  # Cubo azul en (10, 5)
            {'x': 15, 'y': 10, 'color': 3}, # Cubo amarillo en (15, 10)
            {'x': 20, 'y': 15},             # Cubo gris por defecto en (20, 15)
        ]
        #fig_2d = self.draw_2d_space_tkinter(cube_data)

        # Convertir la figura en un widget de Tkinter
        #canvas_2d = FigureCanvasTkAgg(fig_2d, self.geometry_2d_frame)
        #canvas_2d.get_tk_widget().pack(pady=10)

        # Subpestaña: Detección de Cubos
        self._update_images()
        self.update_camera_feed_3()
        self.toggle_mode()

    

    def toggle_mode(self):
        """Maneja el cambio de estado del Checkbutton"""
        # Limpia filas específicas para evitar superposiciones
        for widget in self.frame_vision.grid_slaves():
            if int(widget.grid_info()["row"]) > 2:
                widget.destroy()

        if self.camera_check_var.get() == 1:
            self.remove_file_inputs()
            self.start_camera()

        else:
            self.create_file_inputs()
            self.stop_camera()

    def remove_file_inputs(self):
        """Elimina los campos de entrada y botones para cargar imágenes"""
        for widget in [self.file_entry1, self.browse_button1, self.file_entry2, self.browse_button2]:
            widget.grid_forget()
            
        self.camera_entry1 = ttk.Combobox(self.image1_frame,values=self.camera_controller.camera_names,  font=("Montserrat", 10))
        self.camera_entry1.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")
        if len(self.camera_controller.cameras) > 0:
            self.camera_entry1.set(self.camera_controller.camera_names[0])
            
        self.camera_entry2 = ttk.Combobox(self.image2_frame,values=self.camera_controller.camera_names,  font=("Montserrat", 10))
        self.camera_entry2.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")
        if len(self.camera_controller.cameras) > 1:
            self.camera_entry2.set(self.camera_controller.camera_names[1])
        
    
    def start_camera(self):
        self.camera_active = True
        self.update_camera_feed_1()
        self.update_camera_feed_2()
    
    def stop_camera(self):
        """Detiene el feed de la cámara."""
        self.camera_active = False

    def _update_camera(self, camera_index, size:list=(320, 240)):
        frame = self.camera_controller.get_frame(camera_index)

        if frame is not None:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Redimensionar la imagen
            aspect_ratio = img.height / img.width
            height = int(size[0] * aspect_ratio)
            img = img.resize((size[0], height), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
        else:
            imgtk = self._create_image_with_text("Cámara NO encontrada", size)
        
        return imgtk, frame
    
    def update_camera_feed_1(self):
        if self.state_procesar:
            if self.camera_active and self.camera_entry1.get() != '':
                index = self.camera_controller.camera_names.index(self.camera_entry1.get())
                imgtk, frame = self._update_camera(index)

            else:
                imgtk = self._create_image_with_text("Cámara NO encontrada")
                frame = None

            self.img_plant = frame
            self.lbl_vision_figure1.config(image=imgtk)
            self.lbl_vision_figure1.image = imgtk
            self.lbl_vision_figure1.update()

        # Es como un hilo, se llama a sí misma después de 10ms
        self.root.after(10, self.update_camera_feed_1)

    
    
    def update_camera_feed_2(self):
        """Actualiza el feed de la cámara y lo muestra en el Label."""
        if self.state_procesar:
            if self.camera_active and self.camera_entry2.get() != '':
                index = self.camera_controller.camera_names.index(self.camera_entry2.get())
                imgtk, frame = self._update_camera(index)

            else:
                imgtk = self._create_image_with_text("Cámara NO encontrada")
                frame = None

            self.img_front = frame
            self.lbl_vision_figure2.config(image=imgtk)
            self.lbl_vision_figure2.image = imgtk
            self.lbl_vision_figure2.update()

        # Es como un hilo, se llama a sí misma después de 10ms
        self.root.after(11, self.update_camera_feed_2)

    def update_camera_feed_3(self):
        """Actualiza el feed de la cámara y lo muestra en el Label."""
        if self.camera_entry3.get() != '':
            index = self.camera_controller.camera_names.index(self.camera_entry3.get())
            imgtk, frame = self._update_camera(index, (480, 360))

        else:
            imgtk = self._create_image_with_text("Cámara NO encontrada",(480, 360))
            frame = None

        self.img_ws = frame
        self.lbl_vision_figure3.config(image=imgtk)
        self.lbl_vision_figure3.image = imgtk
        self.lbl_vision_figure3.update()
            
        self.root.after(12, self.update_camera_feed_3)

    def create_file_inputs(self):
        """Crea los campos de entrada y botones para cargar imágenes"""
        if self.camera_entry1 and self.camera_entry2:
            for widget in [self.camera_entry1, self.camera_entry2]:
                widget.grid_forget()
        # Campo y botón para la primera imagen
        self.file_entry1 = ttk.Entry(self.image1_frame, width=25, font=("Montserrat", 10))
        self.file_entry1.grid(row=2, column=0, columnspan=2, pady=10, sticky="WN")

        self.browse_button1 = ttk.Button(
            self.image1_frame,
            text="Buscar...",
            command=lambda: self.load_save_frame_1(self.file_entry1, self.lbl_vision_figure1),
        )
        self.browse_button1.grid(row=2, column=2, padx=0, pady=10, sticky="EN")

        # Campo y botón para la segunda imagen
        self.file_entry2 = ttk.Entry(self.image2_frame, width=25, font=("Montserrat", 10))
        self.file_entry2.grid(row=2, column=0, columnspan=2, pady=10, sticky="WN")

        self.browse_button2 = ttk.Button(
            self.image2_frame,
            text="Buscar...",
            command=lambda: self.load_save_frame_2(self.file_entry2, self.lbl_vision_figure2),
        )
        self.browse_button2.grid(row=2, column=2, padx=0, pady=10, sticky="EN")

    def load_save_frame_1(self, entry, label):
        self.img_plant = self._load_file(entry, label)
    
    def load_save_frame_2(self, entry, label):
        self.img_front = self._load_file(entry, label)

    def _load_file(self, entry, label):
        """Permite seleccionar un archivo y actualizar la imagen correspondiente"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imagenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                entry.delete(0, END)
                entry.insert(0, file_path)

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
        
        return self._create_image_with_text("CARGAR IMAGEN", (480, 360))

    def process_images(self):
        """Procesa las imágenes y las muestra en los labels"""
        # Verifica que ambas imágenes estén cargadas
        if self.img_front is not None and self.img_plant is not None:
            self.process_button.state([ttk.DISABLED])
            self.clear_button.state(["!disabled"])
            self.state_procesar = False

            front_matrix, img_procesed_front = self.ImageProcessorFrontal.process_image(self.img_front, area_size=800)
            plant_matrix, img_procesed_plant = self.ImageProcessorPlanta.process_image(self.img_plant, area_size=800)
            
            

            #Resize
            img_procesed_front = Image.fromarray(cv2.cvtColor(img_procesed_front, cv2.COLOR_BGR2RGB))
            img_procesed_plant = Image.fromarray(cv2.cvtColor(img_procesed_plant, cv2.COLOR_BGR2RGB))
            photo1 = self._resize_image(img_procesed_plant, self.width)
            photo2 = self._resize_image(img_procesed_front, self.width)

            photo1 = ImageTk.PhotoImage(photo1)
            self.lbl_vision_figure1.config(image=photo1)
            self.lbl_vision_figure1.image = photo1

            photo2 = ImageTk.PhotoImage(photo2)
            self.lbl_vision_figure2.config(image=photo2)
            self.lbl_vision_figure2.image = photo2

            fig_3d = self.FigureGenerator.generate_figure_from_matrix(plant_matrix, front_matrix, True)

             # Actualizar canvas_3d
            if hasattr(self, "canvas_3d") and self.canvas_3d is not None:
                # Eliminar canvas previo si existe
                self.canvas_3d.get_tk_widget().destroy()

            # Crear y asignar nueva figura
            self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.geometry_frame)
            self.canvas_3d.get_tk_widget().pack(padx=0, pady=0)

    def _resize_image(self, img, width):
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio)
        return img.resize((width, height))    
    
    def clear_images(self):
        self.clear_button.state([ttk.DISABLED])
        self.process_button.state(["!disabled"])
        self.state_procesar = True

        # --- VACIAR MATRIZ ---
        fig_3d = self.FigureGenerator.generate_figure_from_matrix(self.plant_matrix, self.side_matrix, True)

        if hasattr(self, "canvas_3d") and self.canvas_3d is not None:
                # Eliminar canvas previo si existe
                self.canvas_3d.get_tk_widget().destroy()

            # Crear y asignar nueva figura
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.geometry_frame)
        self.canvas_3d.get_tk_widget().pack(padx=0, pady=0)

        #self._update_images()
        self.toggle_mode()

    def update_cameras(self):
        self.camera_controller.stop()
        self.camera_controller.start(10)
        self.camera_entry1['values'] = self.camera_controller.camera_names
        self.camera_entry2['values'] = self.camera_controller.camera_names
        self.camera_entry3['values'] = self.camera_controller.camera_names
        
        
        
        
        
# Función para actualizar las imágenes en la interfaz
    def _update_images(self):
        img1 = self._create_image_with_text("CARGAR IMAGEN")
        img2 = self._create_image_with_text("CARGAR IMAGEN")
        

        # Actualizar las etiquetas en la interfaz
        self.lbl_vision_figure1.config(image=img1)
        self.lbl_vision_figure1.image = img1

        self.lbl_vision_figure2.config(image=img2)
        self.lbl_vision_figure2.image = img2


    def _create_image_with_text(self, text, size=(320, 240)):
        # Crear una imagen negra de tamaño 320x240
        image = Image.new('RGB', size, color='black')
        
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
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        # Dibujar el texto en la imagen
        draw.text(position, text, font=font, fill=text_color)
        
        # Convertir la imagen a un formato compatible con tkinter
        tk_image = PhotoImage(image, master=self.root)
        
        return tk_image


    def draw_2d_space_tkinter(self, cube_data):
        """
        Dibuja un espacio 2D con cubos representados como cuadrados y lo devuelve como un widget para Tkinter.
        
        Parameters:
        cube_data (list of dict): Lista de diccionarios, donde cada diccionario tiene:
            - 'x': Coordenada x del cubo (en cm).
            - 'y': Coordenada y del cubo (en cm).
            - 'color': Número que representa el color del cubo.
        tk_frame: Frame de Tkinter donde se incrustará el gráfico.
            
        Returns:
        FigureCanvasTkAgg: El dibujo como un widget para Tkinter.
        """
        # Definir los colores de los cubos
        colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow', 4: 'gray'}
        
        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=(8, 3.5))
        
        # Dibujar cada cubo según las coordenadas y el color
        for cube in cube_data:
            x = cube['x']
            y = cube['y']
            color = cube.get('color', 4)  # Por defecto el color es gris (4)
            
            # Dibujar un cuadrado de 5x5 cm
            ax.add_patch(plt.Rectangle((x, y), 5, 5, color=colors.get(color, 'black')))
        
        # Ajustar los límites del gráfico
        ax.set_xlim(0, max(cube['x'] for cube in cube_data) + 10)
        ax.set_ylim(0, max(cube['y'] for cube in cube_data) + 10)
        
        # Etiquetas y grid
        ax.set_xlabel('X (cm)')
        ax.set_ylabel('Y (cm)')
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.subplots_adjust(bottom=0.2)
        
        return fig


    def _adjust_tab_titles(self, fuente):
        
        # Obtener el ancho disponible para las pestañas
        font = Font(font=fuente)
        total_width = self.notebook.winfo_screenwidth()
        tab_count = len(self.tabs)
        tab_width = total_width // tab_count

        # Ajustar el texto de cada pestaña
        for index, tab in enumerate(self.tabs):
            # Calcular el número de espacios necesarios
            spaces_needed = (tab_width - len(tab) * 8) // 2  # Aproximadamente 8 píxeles por carácter
            spaces = " " * max(spaces_needed // font.measure(" "), 0)  # Dividir espacios entre ambos lados
            self.tabs[index] = f"{spaces}{tab}{spaces}"

    def _on_closing(self):
        """Esta función se ejecuta cuando la ventana se cierra."""
        self.camera_controller.stop()
        
        # Cerrar la ventana de Tkinter
        self.root.destroy()
        exit()

if __name__ == "__main__":

    app = DynamicTabsApp()
    