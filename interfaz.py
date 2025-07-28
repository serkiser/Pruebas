from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox
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

        # Entrada de ELO 
        self.elo_input = QLineEdit()
        self.elo_input.setPlaceholderText("Introduce tu ELO")
        self.elo_input.setEnabled(False)
        
        # Entrada de Lugar donde vives 
        self.vives_input = QLineEdit()
        self.vives_input.setPlaceholderText("Introduce tu donde vives")
        self.vives_input.setEnabled(False)

        # Mensaje
        self.mensaje_label = QLabel("")

        # Botón para validar nombre
        self.boton_nombre = QPushButton("Validar nombre")
        self.boton_nombre.clicked.connect(self.enviar_nombre)
        self.entrada.returnPressed.connect(self.enviar_nombre)

        # Botón invisible para ELO (Enter lo valida)
        self.elo_input.returnPressed.connect(self.enviar_elo)
        
        # Botón invisible para donde vives (Enter lo valida)
        self.vives_input.returnPressed.connect(self.enviar_vives)

        # Switch para modo nocturno
        self.switch_noche = QCheckBox("Modo nocturno")
        self.switch_noche.stateChanged.connect(self.toggle_noche)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.entrada)
        layout.addWidget(self.elo_input)
        layout.addWidget(self.mensaje_label)
        layout.addWidget(self.boton_nombre)
        layout.addWidget(self.switch_noche)  
        self.setLayout(layout)

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
    def enviar_vives(self):
        donde_vives = self.vives_input.text().strip()
        resultado = variable_donde_vives(donde_vives)



# Ejecutar la app
app = QApplication([])
ventana = Ventana()
ventana.show()
app.exec()
