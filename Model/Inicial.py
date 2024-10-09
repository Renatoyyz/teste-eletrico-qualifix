from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QThread
import os

from View.tela_inicial import Ui_TelaInicial

from Model.Login import TelaLogin

class TelaInicial(QMainWindow):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()

        self.io = io
        self.dado = dado
        self.database = db
        self.dado.set_telas(self.dado.TELA_INICIAL)
        self.rotina = rotina

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaInicial()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Mover a janela para o canto superior esquerdo
        # self.move_to_corner()

        self.mouseReleaseEvent = self.setfoccus
        self.ui.btConfigurar.clicked.connect(self.tela_configurar)
        self.ui.btIniciar.clicked.connect(self.tela_execucao)
        self.ui.btDesligarSistema.clicked.connect(self.desligar_sistema)

    def move_to_corner(self):
        # Obter a geometria do monitor primário
        desktop = QApplication.desktop()
        rect = desktop.availableGeometry()

        # Configurar a geometria da janela para preencher a tela
        self.setGeometry(rect)
        self.move(rect.topLeft())

    def tela_configurar(self):
        self.dado.set_telas(self.dado.TELA_LOGIN)
        configuracao = TelaLogin(dado=self.dado, io=self.io, target=self.dado.TELA_CONFIG, db=self.database, rotina=self.rotina)
        configuracao.setModal(True)
        configuracao.exec_()

    def tela_execucao(self):
        self.dado.set_telas(self.dado.TELA_LOGIN)
        execucao = TelaLogin(dado=self.dado, io=self.io, target=self.dado.TELA_EXECUCAO, db=self.database, rotina=self.rotina)
        execucao.setModal(True)
        execucao.exec_()
    
    def desligar_sistema(self):
        self.shutdown_pi()
        self.close()

    def shutdown_pi(self):
        print("Desligando o Raspberry Pi com segurança...")
        QThread.sleep(10)
        os.system("sudo shutdown now")


    def closeEvent(self, event):
        event.accept()

    def setfoccus(self, event):
        if self.io.io_rpi.bot_acio_d == 1:
            self.close()