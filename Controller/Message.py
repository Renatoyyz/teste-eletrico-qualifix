from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5 import QtCore

class SimpleMessageBox:
    def __init__(self, icon=QMessageBox.Information, title="Mensagem"):
        self.message_box = QMessageBox()
        self.message_box.setIcon(icon)
        self.message_box.setWindowTitle(title)

    def exec(self, msg):
        self.message_box.setText(msg)
        return self.message_box.exec_()
    
class MessageBox:
    def __init__(self, title="Mensagem"):
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle(title)
        self.yes_no = False

        # Adiciona botão de Aceitar
        self.accept_button = QPushButton("Aceitar")
        self.accept_button.clicked.connect(self.accept)
        self.message_box.addButton(self.accept_button, QMessageBox.AcceptRole)

        # Adiciona botão de Negar
        self.reject_button = QPushButton("Negar")
        self.reject_button.clicked.connect(self.reject)
        self.message_box.addButton(self.reject_button, QMessageBox.RejectRole)

    def accept(self):
        # Lógica para quando o botão "Aceitar" é clicado
        self.yes_no = True
        self.message_box.done(QMessageBox.Accepted)

    def reject(self):
        # Lógica para quando o botão "Negar" é clicado
        self.yes_no = False
        self.message_box.done(QMessageBox.Rejected)

    def exec(self, msg):
        self.message_box.setText(msg)
        return self.message_box.exec_()
    
# Exemplo de uso:
if __name__ == "__main__":
    pass