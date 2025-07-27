from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)
from llorens import variable_nombre, variable_elo


class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llorens - PySide6")
        self.setGeometry(600, 300, 500, 400)

        # Entrada de nombre
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Escribe tu nombre")
        self.entrada.returnPressed.connect(self.enviar_nombre)

        # Entrada de ELO
        self.elo_input = QLineEdit()
        self.elo_input.setPlaceholderText("Introduce tu ELO")
        self.elo_input.setEnabled(False)
        self.elo_input.returnPressed.connect(self.enviar_elo)

        # Mensaje informativo
        self.mensaje_label = QLabel("")

        # Botones
        self.boton_nombre = QPushButton("Enviar nombre")
        self.boton_nombre.clicked.connect(self.enviar_nombre)

        self.boton_elo = QPushButton("Enviar ELO")
        self.boton_elo.clicked.connect(self.enviar_elo)
        self.boton_elo.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.entrada)
        layout.addWidget(self.elo_input)
        layout.addWidget(self.mensaje_label)
        layout.addWidget(self.boton_nombre)
        layout.addWidget(self.boton_elo)

        self.setLayout(layout)

    def enviar_nombre(self):
        nombre = self.entrada.text().strip()

        if not nombre:
            self.mensaje_label.setText("Por favor, escribe un nombre.")
            self.elo_input.setEnabled(False)
            self.boton_elo.setEnabled(False)
            return

        resultado = variable_nombre(nombre)
        self.mensaje_label.setText(resultado)

        if resultado.lower().startswith("nombre válido"):
            self.elo_input.setEnabled(True)
            self.boton_elo.setEnabled(True)
        else:
            self.elo_input.setEnabled(False)
            self.boton_elo.setEnabled(False)

    def enviar_elo(self):
        elo = self.elo_input.text().strip()
        if not elo:
            self.mensaje_label.setText("Por favor, introduce tu ELO.")
            return
        resultado = variable_elo(elo)
        self.mensaje_label.setText(resultado)


# Ejecutar la app
app = QApplication([])
ventana = Ventana()
ventana.show()
app.exec()
