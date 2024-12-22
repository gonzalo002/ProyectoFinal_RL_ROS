import tkinter as tk
from tkinter import messagebox
import subprocess
import time

class RVizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter con RViz")

        # Crear un Toplevel para incrustar la ventana de RViz
        self.top = tk.Toplevel(root)
        self.top.title("Ventana de RViz incrustada")
        self.top.geometry("800x600")  # Tamaño inicial del Toplevel

        # Botón para iniciar RViz
        self.B_Rviz_start = tk.Button(root, text="Iniciar RViz", command=self._rviz_launch)
        self.B_Rviz_start.pack()

    def _rviz_launch(self):
        try:
            # Lanza RViz en un proceso separado
            self.rviz_process = subprocess.Popen(['rviz'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Espera activa para asegurarse de que la ventana de RViz esté disponible
            rviz_window_id = None
            for _ in range(10):  # Espera un máximo de 10 intentos
                rviz_window_id = self._get_rviz_window_id()
                if rviz_window_id:
                    break
                time.sleep(1)  # Espera 1 segundo entre intentos

            if rviz_window_id:
                # Obtiene el window id del Toplevel de Tkinter
                top_window_id = self.top.winfo_id()

                # Realiza el reparenting usando wmctrl
                self._reparent_window(rviz_window_id, top_window_id)

                # Ajusta la posición y el tamaño de la ventana de RViz
                self._resize_rviz_window(rviz_window_id)
                
                messagebox.showinfo("Éxito", "RViz se ha lanzado y se ha incrustado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo encontrar la ventana de RViz.")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo lanzar o ajustar RViz: {e}")

        self.B_Rviz_start.destroy()

    def _get_rviz_window_id(self):
        try:
            # Usa wmctrl para obtener el ID de la ventana de RViz
            rviz_window_id = subprocess.check_output(
                ['wmctrl', '-l', '-x'], stderr=subprocess.PIPE
            ).decode('utf-8')

            # Busca la ventana de RViz con el nombre
            for line in rviz_window_id.splitlines():
                if 'rviz' in line.lower():  # Verifica que sea la ventana de RViz
                    window_id = line.split()[0]
                    return window_id

            return None
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener el ID de la ventana de RViz: {e.output.decode('utf-8')}")
            return None

    def _reparent_window(self, rviz_window_id, top_window_id):
        try:
            # Mueve la ventana de RViz al Toplevel de Tkinter usando wmctrl
            subprocess.run(['wmctrl', '-i', '-r', rviz_window_id, '-e', f'0,0,0,{self.top.winfo_width()},{self.top.winfo_height()}'])
            subprocess.run(['wmctrl', '-i', '-r', rviz_window_id, '-t', str(top_window_id)])
            print(f"Ventana RViz {rviz_window_id} reparented a {top_window_id}")
        except Exception as e:
            print(f"Error al intentar reparentar la ventana: {e}")

    def _resize_rviz_window(self, rviz_window_id):
        try:
            # Ajusta el tamaño de la ventana de RViz
            width = self.top.winfo_width()
            height = self.top.winfo_height()

            # Redimensiona la ventana de RViz
            subprocess.run(['wmctrl', '-i', '-r', rviz_window_id, '-e', f'0,0,0,{width},{height}'])
            print(f"Ventana RViz {rviz_window_id} redimensionada a {width}x{height}")
        except Exception as e:
            print(f"Error al intentar redimensionar la ventana: {e}")

# Crear la ventana raíz de Tkinter
root = tk.Tk()
app = RVizApp(root)
root.mainloop()
