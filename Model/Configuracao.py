from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from Model.CadastroUser import TelaCadastroUser
from Model.CriaReceita import TelaCriaReceita
from View.tela_configuracao import Ui_TelaConfiguracao
from Model.ViewRotina import TelaViewRotina

class TelaConfiguracao(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()
        self.io = io
        self.dado = dado
        self.database = db
        self.rotina = rotina
        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaConfiguracao()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btCadastro.clicked.connect(self.tela_cadastro)
        self.ui.btCriarReceita.clicked.connect(self.tela_cria_receita)
        self.ui.btCarregarDados.clicked.connect(self.carregar_dados)

    def tela_cadastro(self):
        self.dado.set_telas(self.dado.TELA_CADASTRO_USER)
        cadastro = TelaCadastroUser(dado=self.dado, io=self.io, db=self.database)
        cadastro.exec_()

    def tela_cria_receita(self):
        self.dado.set_telas(self.dado.TELA_CRIAR_RECEITA)
        cria_receita = TelaCriaReceita(dado=self.dado,io=self.io, db=self.database, rotina=self.rotina)
        cria_receita.exec_()

    def carregar_dados(self):
        view_rotina = TelaViewRotina(dado=self.dado, io=self.io,db=self.database,rotina=self.rotina, target=self.dado.TELA_CONFIG)
        view_rotina.exec_()

    def voltar(self):
        self.dado.set_telas(self.dado.TELA_INICIAL)
        self.close()

    def closeEvent(self, event):
        event.accept()