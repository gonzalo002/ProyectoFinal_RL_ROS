import tkinter as tk
from tkinter import Frame
import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from rviz import bindings as rviz
from PyQt5.QtCore import QTimer

class RVizWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Crear el marco de visualización de RViz
        self.frame = rviz.VisualizationFrame()
        self.frame.initialize()

        # Cargar una configuración predeterminada de RViz
        self.frame.loadDisplayConfig("")

        # Crear un diseño en el widget
        layout = QVBoxLayout()
        layout.addWidget(self.frame)
        self.setLayout(layout)

class RVizTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RViz in Tkinter")

        # Crear un marco de Tkinter para contener RViz
        self.rviz_frame = Frame(root, width=800, height=600, bg="black")
        self.rviz_frame.pack(fill=tk.BOTH, expand=True)

        # Botones para control adicional
        self.start_button = tk.Button(root, text="Start RViz", command=self.start_rviz)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop RViz", command=self.stop_rviz)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Crear el contenedor para RViz
        self.rviz_widget = None
        self.app = QApplication(sys.argv)

    def start_rviz(self):
        if self.rviz_widget is None:
            self.embed_rviz()

    def stop_rviz(self):
        if self.rviz_widget:
            self.rviz_widget.setParent(None)
            self.rviz_widget = None

    def embed_rviz(self):
        window_id = self.rviz_frame.winfo_id()

        # Crear e inicializar RVizWidget
        self.rviz_widget = RVizWidget()
        self.rviz_widget.winId()  # Forzar la creación de la ventana para asignarla

        # Embebido en el contenedor Tkinter
        QTimer.singleShot(0, lambda: self.rviz_widget.winId())
        QTimer.singleShot(0, lambda: self.rviz_widget.createWindowContainer(window_id))

        print("RViz embebido en Tkinter.")

    def on_closing(self):
        self.stop_rviz()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RVizTkinterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
