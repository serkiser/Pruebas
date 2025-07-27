from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton
from llorens import procesar_nombre  # Importamos la función del otro archivo

class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llorens - PySide6")
        self.setGeometry(600, 300, 500, 400)

        self.setWindowTitle("Enviar nombre a otro archivo")

        # Entrada de texto
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Escribe tu nombre")

        # Botón
        self.boton = QPushButton("Enviar")
        self.boton.clicked.connect(self.enviar_nombre)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.entrada)
        layout.addWidget(self.boton)
        self.setLayout(layout)

    def enviar_nombre(self):
        nombre = self.entrada.text()
        resultado = procesar_nombre(nombre)
        print("Respuesta desde logica.py:", resultado)

# Ejecutar la app
app = QApplication([])
ventana = Ventana()
ventana.show()
app.exec()
