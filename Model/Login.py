from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from Model.Configuracao import TelaConfiguracao
from Model.ViewReceita import TelaViewReceita
from Model.ExecucaoPrograma import TelaExecucao

from View.tela_login import Ui_TelaLogin

from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

class TelaLogin(QDialog):
    def __init__(self, dado=None, io=None, target=None, db=None, rotina=None):
        super().__init__()

        self.io = io
        self.dado = dado
        self.target = target
        self.database = db
        self.rotina = rotina

        self.msg = SimpleMessageBox()

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaLogin()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # # Maximizar a janela
        # # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.btEntrar.clicked.connect(self.entrar_login)
        self.ui.txLogin.mousePressEvent = self.preenche_login
        self.ui.txSenha.mousePressEvent = self.preenche_senha
        self.ui.txLogin.setText("QUALIFIX")
        self.ui.txSenha.setText("1420")

    def preenche_login(self, event):
        keyboard = AlphanumericKeyboard(dado=self.dado)
        keyboard.exec_()# Rode em modal
        self.ui.txLogin.setText(keyboard.line_edit.text())

    def preenche_senha(self, event):
        keyboard = NumericKeyboard(dado=self.dado)
        keyboard.exec_()
        self.ui.txSenha.setText(keyboard.line_edit.text())

    # Verificar aqui o banco de dados para login
    def entrar_login(self):
        msg = SimpleMessageBox()
        user_loc = self.database.search_name_login(name=self.ui.txLogin.text())
        if user_loc != None:
            #Confere a senha e se tem permissão de administrador
            if user_loc[2] == self.ui.txSenha.text():

                # Se for para tela de configuração, só é permitido administrador
                if self.target == self.dado.TELA_CONFIG and user_loc[3] == 1:
                    self.dado.set_telas(self.dado.TELA_CONFIG)
                    self.dado.set_nome_login(user_loc[1])
                    self.dado.set_senha_login(user_loc[2])
                    self.dado.set_permissao_login(user_loc[3])
                    config = TelaConfiguracao(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina)
                    config.exec_()
                #se for tela execução todos podem
                elif self.target == self.dado.TELA_EXECUCAO:
                    try:
                        rotina_db = self.database.search_fim_rotina()
                        if rotina_db != []:
                            nome_rotina = ""
                            for nome in rotina_db:
                                nome_rotina = nome[1]
                                break
                            nome_prog = nome_rotina.split('$')[0]
                            self.msg.exec(msg="Existe trabalho pendente.\nFavor finalizar ou continuar.")
                            self.dado.set_telas(self.dado.TELA_EXECUCAO)
                            self.dado.set_nome_login(user_loc[1])
                            self.dado.set_senha_login(user_loc[2])
                            self.dado.set_permissao_login(user_loc[3])
                            rotina_db = self.database.search_name_rotina(nome_rotina)
                            execucao = TelaExecucao(dado=self.dado, io=self.io,db=self.database,rotina=self.rotina, nome_prog=str(nome_prog), continuacao=True, db_rotina=rotina_db[0])
                            execucao.exec_()
                            self.close()
                            return 0
                    except:
                        print("Erro ao carregar rotina")

                    self.dado.set_telas(self.dado.TELA_RECEITA_VIEW)
                    self.dado.set_nome_login(user_loc[1])
                    self.dado.set_senha_login(user_loc[2])
                    self.dado.set_permissao_login(user_loc[3])
                    receita = TelaViewReceita(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina, target=self.dado.TELA_EXECUCAO)
                    receita.exec_()
                else:
                    self.dado.set_telas(self.dado.TELA_INICIAL)
                    msg.exec(msg="Esse login não tem permissão de admistrador")
            else:
                self.dado.set_telas(self.dado.TELA_INICIAL)
                msg.exec("Erro na senha.")
        else:  
            self.dado.set_telas(self.dado.TELA_INICIAL)
            msg.exec("Login inexistente.")
        
        self.close()

    def closeEvent(self, event):
        event.accept()