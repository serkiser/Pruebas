from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
import sys

# Crear una clase para la ventana principal
class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi primera GUI con PySide6")
        self.setGeometry(100, 100, 300, 200)

        # Crear un layout vertical
        layout = QVBoxLayout()

        # Crear un label y un botón
        self.etiqueta = QLabel("¡Hola desde PySide6!")
        boton = QPushButton("Haz clic")

        # Conectar el botón a una función
        boton.clicked.connect(self.cambiar_texto)

        # Agregar widgets al layout
        layout.addWidget(self.etiqueta)
        layout.addWidget(boton)

        # Establecer el layout en la ventana
        self.setLayout(layout)

    def cambiar_texto(self):
        self.etiqueta.setText("¡Botón presionado!")

# Crear la aplicación y mostrar la ventana
app = QApplication(sys.argv)
ventana = VentanaPrincipal()
ventana.show()
sys.exit(app.exec())
