from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from llorens import variable_nombre, variable_elo, variable_donde_vives

class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llorens - PySide6")
        self.setGeometry(600, 300, 500, 400)

        # --- Botón hamburguesa (≡) ---
        self.boton_menu = QPushButton("≡")
        self.boton_menu.setFixedSize(30, 30)
        self.boton_menu.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """)
        self.boton_menu.clicked.connect(self.abrir_menu)  # Puedes definir qué hace

        barra_superior = QHBoxLayout()
        barra_superior.addStretch()  # Empuja el botón a la derecha
        barra_superior.addWidget(self.boton_menu)

        # Entrada de nombre
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("Escribe tu nombre")

        # Entrada de ELO 
        self.elo_input = QLineEdit()
        self.elo_input.setPlaceholderText("Introduce tu ELO")
        self.elo_input.setEnabled(False)
        
        # Entrada de Lugar donde vives 
        self.vives_input = QLineEdit()
        self.vives_input.setPlaceholderText("Introduce dónde vives")
        self.vives_input.setEnabled(False)

        # Mensaje
        self.mensaje_label = QLabel("")

        # Eventos de validación
        self.entrada.returnPressed.connect(self.enviar_nombre)
        self.elo_input.returnPressed.connect(self.enviar_elo)
        self.vives_input.returnPressed.connect(self.enviar_vives)

        # Switch para modo nocturno
        self.switch_noche = QCheckBox("Modo nocturno")
        self.switch_noche.stateChanged.connect(self.toggle_noche)

        # Layout principal
        layout = QVBoxLayout()
        layout.addLayout(barra_superior)  # Añadimos la barra arriba del todo
        layout.addWidget(self.entrada)
        layout.addWidget(self.elo_input)
        layout.addWidget(self.vives_input)
        layout.addWidget(self.mensaje_label)
        layout.addWidget(self.switch_noche)
        self.setLayout(layout)

    def abrir_menu(self):
        self.mensaje_label.setText("Botón de menú pulsado (puedes añadir funciones aquí)")

    def toggle_noche(self):
        if self.switch_noche.isChecked():
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #f0f0f0;
                }
                QLineEdit, QPushButton {
                    background-color: #3c3f41;
                    color: #f0f0f0;
                    border: 1px solid #555;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #505354;
                }
                QCheckBox {
                    color: #f0f0f0;
                }
            """)
        else:
            self.setStyleSheet("")  # Estilo por defecto (modo claro)

    def enviar_nombre(self):
        nombre = self.entrada.text().strip()
        if not nombre:
            self.mensaje_label.setText("Por favor, escribe un nombre.")
            self.elo_input.setEnabled(False)
            return

        resultado = variable_nombre(nombre)
        self.mensaje_label.setText(resultado)

        if resultado.lower().startswith("nombre válido"):
            self.elo_input.setEnabled(True)
        else:
            self.elo_input.setEnabled(False)

    def enviar_elo(self):
        elo = self.elo_input.text().strip()
        resultado = variable_elo(elo)
        self.mensaje_label.setText(resultado)
        if "elo válido" in resultado.lower():
            self.vives_input.setEnabled(True)
        else:
            self.vives_input.setEnabled(False)

    def enviar_vives(self):
        donde_vives = self.vives_input.text().strip()
        resultado = variable_donde_vives(donde_vives)
        self.mensaje_label.setText(resultado)

# Ejecutar la app
app = QApplication([])
ventana = Ventana()
ventana.show()
app.exec()

