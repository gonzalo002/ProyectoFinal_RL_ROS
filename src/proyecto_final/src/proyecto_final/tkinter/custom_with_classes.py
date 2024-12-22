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

from proyecto_final.vision.grupo_2.image_processor_top import ImageProcessor_Top
from proyecto_final.vision.grupo_2.image_processor_front import ImageProcessor_Front
from proyecto_final.vision.grupo_2.cube_tracker import CubeTracker
from camera_controller import CameraController
from geometry import FigureGenerator
from geometry2D import Geometry2D
from robotica_tab import RoboticaTkinter
from vision_tab import VisionTab
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

        
        
        


        


        #Al finalizar
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Crear un notebook (pestañas)
        self.estilo()
        self.create_notebook()
        #self.vision_tab()
        self.root.mainloop()

    
    def create_notebook(self):
        self.tabs = ["Visión", "Robótica", "Reinforcement Learning"]
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook", padding=[10,10])
        self.notebook.pack(fill="both", expand=True)
        self._adjust_tab_titles(("Montserrat Medium", 12))

        self.tab_vision = ttk.Frame(self.notebook, style = "Custom.TFrame", padding=[10,10], relief='flat')
        self.notebook.add(self.tab_vision, text=self.tabs[0])
        self.VisionTab = VisionTab(self.root, self.tab_vision, True)

        self.tab_robotics = ttk.Frame(self.notebook, relief='flat')
        self.notebook.add(self.tab_robotics, text=self.tabs[1])
        self.RoboticaTab = RoboticaTkinter(self.tab_robotics, False)

        tab_rl = ttk.Frame(self.notebook, relief='flat')
        self.notebook.add(tab_rl, text=self.tabs[2])
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Método que se ejecuta cuando cambia la pestaña"""
        active_tab = self.notebook.select() 
        

        if active_tab == str(self.tab_vision):
            self.VisionTab.tab_active = True
            self.RoboticaTab.tab_active = False
            self.VisionTab.camera_controller.start()

        elif active_tab == str(self.tab_robotics):
            self.VisionTab.tab_active = False
            self.RoboticaTab.tab_active = True
            self.VisionTab.camera_controller.stop()
            
        else:
            self.VisionTab.tab_active = False
            self.RoboticaTab.tab_active = False


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
        self.VisionTab.camera_controller.stop()
        
        # Cerrar la ventana de Tkinter
        self.root.destroy()
        exit()

if __name__ == "__main__":

    app = DynamicTabsApp()
    