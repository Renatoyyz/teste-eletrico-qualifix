from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from Model.ViewLogin import TelaViewLogin
from View.tela_cadastro import Ui_TelaCadastroUser

from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

class TelaCadastroUser(QDialog):
    def __init__(self, dado=None, io=None, db=None):
        super().__init__()
        self.dado = dado
        self.io = io
        self.database = db
        self.login_temp = ""
        self.id_temp = None

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaCadastroUser()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.txLogin.mousePressEvent = self.preencher_login
        self.ui.txSenha.mousePressEvent = self.preencher_senha

        self.ui.btSair.clicked.connect(self.sair)
        self.ui.btLocalizar.clicked.connect(self.login_view)
        self.ui.btCadastrar.clicked.connect(self.cadastrar)
        self.ui.btDeletar.clicked.connect(self.deletar)
        self.ui.btAtualizar.clicked.connect(self.atualizar)

    def preencher_login(self, event):
        keyboard = AlphanumericKeyboard(dado=self.dado)
        keyboard.exec_()# Rode em modal
        self.ui.txLogin.setText(keyboard.line_edit.text())

    def preencher_senha(self, event):
        keyboard = NumericKeyboard(dado=self.dado)
        keyboard.exec_()# Rode em modal
        self.ui.txSenha.setText(keyboard.line_edit.text())

    def login_view(self):
        msg = SimpleMessageBox()
        self.dado.set_telas(self.dado.TELA_LOGIN_VIEW)
        login_view = TelaViewLogin(dado=self.dado, io=self.io, db=self.database)
        login_view.exec_()
        login_loc = self.database.search_name_login(login_view.nome_login)

        # Se for o login mestre, pode fazer alterações em qualquer um
        if login_loc != None:
            if self.dado.permissao_login == 1 and self.dado.nome_login == self.database._login_default:
                self.ui.txLogin.setText(login_loc[1])
                self.ui.txSenha.setText(login_loc[2])
                if login_loc[3] == 1:
                    self.ui.rbtAdm.setChecked(True)
                else:
                    self.ui.rbtOperador.setChecked(True)
            # Mas se for um adm e o usuário não for adm, pode editar
            elif self.dado.permissao_login == 1 and login_loc[3] == 0:
                self.ui.txLogin.setText(login_loc[1])
                self.ui.txSenha.setText(login_loc[2])
                if login_loc[3] == 1:
                    self.ui.rbtAdm.setChecked(True)
                else:
                    self.ui.rbtOperador.setChecked(True)
            else:
                msg.exec(msg="Administradores só podem ser editados no Administrador mestre.")

            self.login_temp = login_loc[1]
            self.id_temp = login_loc[0]

    def cadastrar(self):
        msg = SimpleMessageBox()
        if self.ui.txLogin.text() != "" and self.ui.txSenha.text() != "" and (self.ui.rbtAdm.isChecked() == True or self.ui.rbtOperador.isChecked() == True):
            nome_login = self.database.search_name_login(self.ui.txLogin.text())
            if nome_login == None:# Se retornou None é porque não tem nenhum logim com nome que foi posto
                permissao = 0
                if self.ui.rbtAdm.isChecked() == True:# Se administrador estiver ativado, o valor é um que sgnifica administrador
                    permissao = 1 #
                else:
                    permissao = 0 # se não só pode estar checado o radio button de operador
                data = [self.ui.txLogin.text(), self.ui.txSenha.text(), permissao]
                self.database.create_record_login(data)
                msg.exec(msg="Login criado com sucesso.")
                self.limpa_campos()
            else:
                msg.exec(msg="Esse usuário já existe.")
        else:
            msg.exec(msg="Favor preencher os campos.")

    def deletar(self):
        msg = SimpleMessageBox()
        msg_choice = MessageBox()
        if self.ui.txLogin.text() != "" and self.ui.txSenha.text() != "" and (self.ui.rbtAdm.isChecked() == True or self.ui.rbtOperador.isChecked() == True):
            nome_login = self.database.search_name_login(self.ui.txLogin.text())

            if nome_login != None:# Se retornou None é porque não tem nenhum logim com nome que foi posto
                if ( nome_login[1] != self.database._login_default ):
                    msg_choice.exec(msg="Tem certeza que quer excluir esse Login?")
                    if msg_choice.yes_no == True:
                        self.database.delete_login_name(self.ui.txLogin.text())
                        msg.exec(msg=f"Login {self.ui.txLogin.text()} excluído com sucesso.")
                        self.limpa_campos()
                else:
                    msg.exec(msg="O login mestre não pode ser deletado.")
            else:
                msg.exec(msg="Houve um erro para carregar esse login.")
        else:
            msg.exec(msg="Favor selecione o login a ser deletado.")

    def atualizar(self):
        msg = SimpleMessageBox()
        if self.ui.txLogin.text() != "" and self.ui.txSenha.text() != "" and (self.ui.rbtAdm.isChecked() == True or self.ui.rbtOperador.isChecked() == True):
            nome_login = self.database.search_name_login(self.login_temp)
            if nome_login != None or self.id_temp != None:
                if self.login_temp == self.database._login_default and self.ui.txLogin.text() == self.database._login_default and self.get_permissao()==1:
                    data = [self.ui.txLogin.text(), self.ui.txSenha.text(), 1 if self.ui.rbtAdm.isChecked() else 0]
                    self.database.update_record_login(self.id_temp, data)
                    msg.exec(msg="Usuário atualizado com sucesso.")
                    self.limpa_campos()
                elif self.login_temp != self.database._login_default:
                    data = [self.ui.txLogin.text(), self.ui.txSenha.text(), 1 if self.ui.rbtAdm.isChecked() else 0]
                    self.database.update_record_login(self.id_temp, data)
                    msg.exec(msg="Usuário atualizado com sucesso.")
                    self.limpa_campos()
                else:
                    msg.exec(msg="Você só pode mudar a senha do Login mestre.")
            else:
                msg.exec(msg="Não dá para atualizar um login inexistente.\nClique em Atualizar para buscar um Login.")
        else:
            msg.exec(msg="Favor selecione o login a ser Atualizado e verifique todos os campos.")

    def get_permissao(self):
        if self.ui.rbtAdm.isChecked() == True:
            return 1
        else:
            return 0

    def limpa_campos(self):
        self.ui.txLogin.clear()
        self.ui.txSenha.clear()
        # self.ui.rbtAdm.setChecked(False)
        # self.ui.rbtOperador.setChecked(False)
        self.ui.rbtInvisible.setChecked(True)


    def sair(self):
        self.dado.set_telas(self.dado.TELA_CONFIG)
        self.close()

    def closeEvent(self, event):
        event.accept()