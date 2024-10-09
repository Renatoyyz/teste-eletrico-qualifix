import logging

# Configuração básica
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Criando um handler para escrever logs em um arquivo
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.WARNING)  # Apenas logs de WARNING e acima serão escritos no arquivo

# Criando um formatador e adicionando-o ao handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Adicionando o handler ao logger
logger = logging.getLogger()
logger.addHandler(file_handler)

# Exemplos de mensagens de log
logging.debug('Isso é uma mensagem de debug.')
logging.info('Isso é uma mensagem de informação.')
logging.warning('Isso é uma mensagem de aviso.')
logging.error('Isso é uma mensagem de erro.')
logging.critical('Isso é uma mensagem crítica.')

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from View.execucao import Ui_frmExecucao

class Atualizador(QtCore.QThread):
    atualizacao = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False

    def run(self):
        while self.running:
            self.atualizacao.emit()
            self.msleep(100)

    def inicia(self):
        self.running = True

    def stop(self):
        self.running = False

class Execucao(QDialog):
    def __init__(self, dado, io, db, nome_programa):
        super().__init__()
        self.dado = dado
        self.io = io
        self.database = db
        self.nome_programa = nome_programa
        self.programa_salvo = None
        self.iniciado = False

        self.VERDE = "verde"
        self.CINZA = "cinza"

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_frmExecucao()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Maximizar a janela
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btIniciarPausar.clicked.connect(self.iniciar_pausar)

        # Configuração do Atualizador
        self.atualizador = Atualizador()
        self.atualizador.atualizacao.connect(self.atualizar_interface)
        self.atualizador.inicia()
        self.atualizador.start()

        self.config()

        # Variáveis para controle de tempo e estado
        self.tempo_decorrido = 0
        self.estado_cor = self.VERDE

    def config(self):
        self.programa_salvo = self.database.read(self.nome_programa)
        self.ui.lbNomeProg.setText(self.nome_programa)

    @QtCore.pyqtSlot()
    def atualizar_interface(self):
        if not self.programa_salvo:
            return

        pnp_habilita_desabilita = self.programa_salvo[0][14]
        pnp_base_tempo = self.programa_salvo[0][13]
        pnp_canal1_qtd = self.programa_salvo[0][3]

        if pnp_habilita_desabilita == 1:
            if pnp_base_tempo == 0:
                self.tempo_decorrido += 0.1  # Incrementa em 0.1 segundos
            elif pnp_base_tempo == 1:
                self.tempo_decorrido += 0.1 / 60  # Incrementa em 0.1 minutos

            if self.tempo_decorrido >= pnp_canal1_qtd:
                self.tempo_decorrido = 0  # Reseta o tempo decorrido

            # Alterna a cor
            if self.estado_cor == self.VERDE:
                self.mudar_cor_label("lbNpn_canal_1", self.CINZA)
                self.estado_cor = self.CINZA
            else:
                self.mudar_cor_label("lbNpn_canal_1", self.VERDE)
                self.estado_cor = self.VERDE

    def mudar_cor_label(self, label_name, cor):
        label = getattr(self.ui, label_name, None)
        if label:
            if cor == self.VERDE:
                label.setStyleSheet("background-color: rgb(33, 255, 6);")
            elif cor == self.CINZA:
                label.setStyleSheet("background-color: rgb(184, 184, 184);")
            else:
                raise ValueError("Cor inválida. Use 'verde' ou 'cinza'.")

    def exemplo_uso(self):
        self.mudar_cor_label("lbNpn_canal_1", "verde")
        self.mudar_cor_label("lbNpn_canal_2", "cinza")

    def voltar(self):
        self.close()

    def iniciar_pausar(self):
        self.iniciado = not self.iniciado
        if self.iniciado:
            self.ui.btIniciarPausar.setText("Pausar")
        else:
            self.ui.btIniciarPausar.setText("Iniciar")
    
    def closeEvent(self, event):
        self.atualizador.stop()
        self.atualizador.wait()
        event.accept()


