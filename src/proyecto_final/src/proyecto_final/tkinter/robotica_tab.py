#!/usr/bin/python3

from sympy import Ge
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, Image, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL.ImageTk import PhotoImage
from proyecto_final.vision.grupo_2.generacion_figura import FigureGenerator
from geometry2D import Geometry2D
import subprocess
from time import sleep


class RoboticaTkinter:
    def __init__(self) -> None:
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

        self.Geometry3D = FigureGenerator()
        self.Geometry2D = Geometry2D()

        self.LF_rviz = None
        self.F_cuarta_fila = None

        self.estilo()
        self.start_robot_tab()
        self._rviz_frame()
        self.root.mainloop()
        
    
    def start_robot_tab(self):
        # Crear un Frame para organizar los elementos dentro de la pestaña "Procesado de Figura"
        self.frame_rob = ttk.Frame(self.root, borderwidth=0)
        self.frame_rob.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        width = self.frame_rob.winfo_width()*0.6

        #Configuración grid
        self.frame_rob.grid_columnconfigure(0, weight=1)
        self.frame_rob.grid_columnconfigure(1, minsize=width)
        self.frame_rob.grid_rowconfigure(0, weight=1)
        self.frame_rob.grid_rowconfigure(1, weight=2)
        self.frame_rob.grid_rowconfigure(2, weight=2)
        self.frame_rob.grid_rowconfigure(3, weight=1)


        self._primera_fila()

    def stop_robot_tab(self):
        self.close_rviz()
    
    def manual_tab(self):
        self._clear_tab()
        self._fila_camaras()


    def auto_tab(self):
        self._clear_tab()
        self._fila_camaras()
        self._fila_geometria()
        self._file_acciones()
    
    def _clear_tab(self):
        for widget in self.frame_rob.winfo_children():
            if widget == self.F_primera_fila or widget in self.F_primera_col.winfo_children():
                continue
            if widget == self.LF_segunda_col or widget in self.F_segunda_col.winfo_children():
                continue
            
            if self.LF_rviz is not None:
                if widget == self.LF_rviz or widget in self.F_Rviz.winfo_children():
                    continue
                if widget == self.LF_terminal  or widget in self.F_terminal.winfo_children():
                    continue
            
            widget.destroy() 
        

    def _primera_fila(self):
        # --- FRAME: Primera fila ---
        self.F_primera_fila = ttk.Frame(self.frame_rob)
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
        self.L_manual = ttk.Label(self.F_primera_col, text="MANUAL" )
        self.L_manual.grid(row=0, column=0, sticky="e", padx=[0, 10])

            # Checkbutton
        self.V_modo = ttk.IntVar()  # Variable para el estado del Checkbutton
        self.CB_modo = ttk.Checkbutton(
            self.F_primera_col,
            variable=self.V_modo,
            command=self.cambio_funcionamiento,
            bootstyle="primary-round-toggle")
        self.CB_modo.grid(row=0, column=1)

        # Text MANUAL
        self.L_automatico = ttk.Label(self.F_primera_col, text="AUTOMÁTICO" )
        self.L_automatico.grid(row=0, column=2, sticky="w", padx=[10, 0])

        # --- SEGUNDA COLUMNA ---
        self.LF_segunda_col = ttk.LabelFrame(self.F_primera_fila, text="  Control del Robot  ")
        self.LF_segunda_col.grid(row=0, column=1, sticky="nsew", padx=[10,0], pady=0)
        self.LF_segunda_col.grid_rowconfigure(0, weight=1)
        self.LF_segunda_col.grid_columnconfigure(0, weight=1)


        self.F_segunda_col= ttk.Frame(self.LF_segunda_col)
        self.F_segunda_col.grid(row=0, column=0, sticky="nsew",padx=0, pady=0)
        self.F_segunda_col.grid_rowconfigure(0, weight=1)
        self.F_segunda_col.grid_columnconfigure(0, weight=1)

        self.B_Stop = ttk.Button(self.F_segunda_col, bootstyle="danger", text="STOP")
        self.B_Stop.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)

        self.cambio_funcionamiento()


    def cambio_funcionamiento(self):
        # --- AUTOMATICO ---
        if self.V_modo.get() == 1:  
            self.L_manual.config(font=("Montserrat", 10), foreground="#474B4E")
            self.L_automatico.config(font=("Montserrat", 10, "bold"), foreground="#8c85f7")
            self.auto_tab()
        
        # --- MANUAL ---
        else:
            self.L_manual.config(font=("Montserrat", 10, "bold"), foreground="#8c85f7")
            self.L_automatico.config(font=("Montserrat", 10), foreground="#474B4E")
            self.manual_tab()

    def _fila_camaras(self):
        # --- FRAME ---
        # Label Frame
        self.LF_segunda_fila = ttk.LabelFrame(self.frame_rob, text="  Visualización Cámaras  ")
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
        self.F_image_1.grid_columnconfigure(0, weight=1)
        self.F_image_1.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.F_image_1,text="CÁMARA SUPERIOR", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        self.L_img_top = ttk.Label(self.F_image_1)
        self.L_img_top.grid(row=1, column=0)

        self.F_image_2 = ttk.Frame(self.F_segunda_fila)
        self.F_image_2.grid_rowconfigure(0, weight=1)
        self.F_image_2.grid_rowconfigure(1, weight=1)
        self.F_image_2.grid_columnconfigure(0, weight=1)
        self.F_image_2.grid(row=0, column=1, sticky="nsew")

        ttk.Label(self.F_image_2,text="CÁMARA LATERAL", 
                  font=("Montserrat SemiBold", 10),
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        self.L_img_front = ttk.Label(self.F_image_2)
        self.L_img_front.grid(row=1, column=0)
        

        self._update_images()
    
    def _fila_geometria(self):
        # --- FRAME: Primera fila ---
        self.LF_tercera_fila = ttk.LabelFrame(self.frame_rob, text="  Visualización Cámaras  ")
        self.LF_tercera_fila.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_tercera_fila.grid_rowconfigure(0, weight=1)
        self.LF_tercera_fila.grid_columnconfigure(0, weight=1)


        self.F_tercera_fila = ttk.Frame(self.LF_tercera_fila)
        self.F_tercera_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_tercera_fila.grid_rowconfigure(0, weight=1)
        self.F_tercera_fila.grid_columnconfigure(0, weight=1)
        self.F_tercera_fila.grid_columnconfigure(1, weight=1)

        # --- ELEMENTS ---
        
        self.geometry1_frame = ttk.Frame(self.F_tercera_fila)
        self.geometry1_frame.grid_rowconfigure(0, weight=1)
        self.geometry1_frame.grid_rowconfigure(1, weight=1)
        self.geometry1_frame.grid_columnconfigure(0, weight=1)
        self.geometry1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.geometry1_frame,text="REPRESENTACIÓN FIGURA", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        fig_3d = self.Geometry3D._paint_matrix(np.array([[[]]]), tkinter=True, figsize=(3,3))

        # Mostrar la figura 3D en el canvas
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.geometry1_frame)
        self.canvas_3d.get_tk_widget().grid(row=1, column=0)


        self.geometry2_frame = ttk.Frame(self.F_tercera_fila)
        self.geometry2_frame.grid_rowconfigure(0, weight=1)
        self.geometry2_frame.grid_rowconfigure(1, weight=1)
        self.geometry2_frame.grid_columnconfigure(0, weight=1)
        self.geometry2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.geometry2_frame,text="REPRESENTACIÓN FIGURA", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
        fig_2d = self.Geometry2D.draw_2d_space([], tkinter=True,figsize=(4,3))

        # Mostrar la figura 3D en el canvas
        self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.geometry2_frame)
        self.canvas_2d.get_tk_widget().grid(row=1, column=0)

    def _file_acciones(self):
        # --- FRAME: Primera fila ---
        self.LF_cuarta_fila = ttk.LabelFrame(self.frame_rob, text="  Acciones  ")
        self.LF_cuarta_fila.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_cuarta_fila.grid_rowconfigure(0, weight=1)
        self.LF_cuarta_fila.grid_columnconfigure(0, weight=1)


        self.F_cuarta_fila = ttk.Frame(self.LF_cuarta_fila)
        self.F_cuarta_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_cuarta_fila.grid_rowconfigure(0, weight=1)
        self.F_cuarta_fila.grid_columnconfigure(0, weight=1)
        self.F_cuarta_fila.grid_columnconfigure(1, weight=1)

        # --- ELEMENTS ---
        self.B_MakeFigure = ttk.Button(self.F_cuarta_fila, bootstyle="primary", text="DETECT FIGURE")
        self.B_MakeFigure.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)

        self.B_RemakeFigure = ttk.Button(self.F_cuarta_fila, bootstyle="primary", text="RECONSTRUCT FIGURE")
        self.B_RemakeFigure.grid(row=0, column=1, sticky="nsew",padx=10, pady=10)

    
    def _rviz_frame(self):
        self.LF_rviz = ttk.LabelFrame(self.frame_rob, text="  Visualización RViz  ")
        self.LF_rviz.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=5)
        self.LF_rviz.grid_rowconfigure(0, weight=1)
        self.LF_rviz.grid_columnconfigure(0, weight=1)

        self.F_Rviz = ttk.Frame(self.LF_rviz)
        self.F_Rviz.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.B_Rviz_start = ttk.Button(self.F_Rviz, 
                                       bootstyle="primary", 
                                       text="START RVIZ",  
                                       command=self._rviz_launch)
        
        self.B_Rviz_start.grid(row=0, column=1, sticky="nsew",padx=10, pady=10)
        
        self.LF_terminal = ttk.LabelFrame(self.frame_rob, text="  Terminal  ")
        self.LF_terminal.grid(row=3, column=1, sticky="nsew", padx=10, pady=5)
        self.LF_terminal.grid_rowconfigure(0, weight=1)
        self.LF_terminal.grid_columnconfigure(0, weight=1)



        self.F_terminal = ttk.Frame(self.LF_terminal)
        self.F_terminal.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.F_terminal.grid_rowconfigure(0, weight=1)
        self.F_terminal.grid_columnconfigure(0, weight=1)

        self.terminal = ttk.ScrolledText(self.F_terminal, 
                                    wrap=ttk.WORD, 
                                    font=("Courier", 12),
                                    height=1,
                                    state=ttk.NORMAL)
        self.terminal.configure(
            bg="#1e1e1e",  # Fondo negro
            fg="white",  # Texto blanco
            insertbackground="white",  # Cursor blanco
        )
        self.terminal.vbar.pack_forget() 
        #self.terminal.config(yscrollcommand=self.terminal_scroll.set)
        self.terminal.grid(row=0, column=0, sticky="nsew")
        self.terminal.tag_configure("ERROR", foreground="red")  # Estilo para errores
        self.terminal.tag_configure("WARN", foreground="yellow")  # Estilo para advertencias
        self.terminal.tag_configure("INFO", foreground="green")
        self.terminal.insert(ttk.END, f"Mensaje 1\n", "ERROR")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        
    def _rviz_launch(self):
        try:
            # Lanza RViz en un proceso separado
            self.rviz_process = subprocess.Popen(['rviz'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sleep(0.5)  # Da tiempo para que la ventana de RViz aparezca
            
            # Usa xwininfo para obtener la ventana de RViz
            try:
                self.win_info = subprocess.check_output(['xdotool', 'search', '--name', 'default.rviz - RViz']).decode('utf-8').strip()
                print(self.win_info)
            except subprocess.CalledProcessError as e:
                print(f"Error al buscar ventana: {e.output.decode('utf-8')}")


            self.root.after(1000, self.reparent_rviz, self.win_info)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo incrustar RViz: {e}")

        self.B_Rviz_start.destroy()


    def reparent_rviz(self, rviz_window_id):
        try:
            self.F_Rviz.update_idletasks()
            # Asegurarse de que el Frame tiene dimensiones
            width = self.F_Rviz.winfo_width()
            height = self.F_Rviz.winfo_height()

            print(f"Tamaño del frame: {width}x{height}")  # Debugging line


            print(str(self.F_Rviz.winfo_id()))
            subprocess.run(['xdotool', 'windowsize', rviz_window_id, str(width), str(height)])
            #self.win_info = subprocess.check_output(['xdotool', 'search', '--name', 'default.rviz - RViz']).decode('utf-8').strip()
            subprocess.run(['xdotool', 'windowreparent', rviz_window_id, str(self.F_Rviz.winfo_id())])
            


        except Exception as e:
            messagebox.showerror("Error", f"Error al ajustar la ventana: {e}")

    def close_rviz(self):
        try:
           
            # Envía la señal de cierre a la ventana de RViz
            subprocess.call(['xdotool', 'windowclose', self.win_info])
            
            print("Ventana RViz cerrada")
        except subprocess.CalledProcessError as e:
            print(f"Error al cerrar la ventana: {e}")
    

    def _update_images(self):
        img1 = self._create_image_with_text(f"/cam_top\nNO PUBLICADO")
        img2 = self._create_image_with_text(f"/cam_front\nNO PUBLICADO")
        

        # Actualizar las etiquetas en la interfaz
        self.L_img_top.config(image=img1)
        self.L_img_top.image = img1

        self.L_img_front.config(image=img2)
        self.L_img_front.image = img2


    def _create_image_with_text(self, text:str, size=(320, 240)):
        # Crear una imagen negra de tamaño 320x240
        image = Image.new('RGB', size, color='black')
        
        # Crear un objeto para dibujar en la imagen
        draw = ImageDraw.Draw(image)
        
        # Establecer el color del texto
        text_color = (255, 255, 255)  # Blanco
        
        # Intentar cargar una fuente del sistema o usar una por defecto
        try:
            font = ImageFont.truetype("C:/Users/itsas/AppData/Local/Microsoft/Windows/Fonts/Montserrat-Regular.ttf", 20)  # Usa una fuente si está disponible
        except IOError:
            font = ImageFont.load_default()  # Si no se encuentra, usa la fuente predeterminada
        
        # Dividir el texto en líneas
        lines = text.split("\n")
        
        # Calcular la altura total del texto (sumando las alturas de las líneas y los márgenes)
        total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
        line_height = draw.textbbox((0, 0), lines[0], font=font)[3] - draw.textbbox((0, 0), lines[0], font=font)[1]  # Altura de una línea

        # Calcular la posición inicial para centrar las líneas
        y_offset = (size[1] - total_text_height) // 2

        # Dibujar cada línea en la imagen
        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=font)  # Obtiene las dimensiones del texto
            text_width = text_bbox[2] - text_bbox[0]
            position = ((size[0] - text_width) // 2, y_offset)  # Centrar horizontalmente y ajustar verticalmente
            draw.text(position, line, font=font, fill=text_color)
            
            # Aumentar el desplazamiento vertical para la siguiente línea
            y_offset += line_height

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
        self.stop_robot_tab()
        
        # Cerrar la ventana de Tkinter
        self.root.destroy()
        exit()
        
if __name__ == "__main__":
    RoboticaTkinter()