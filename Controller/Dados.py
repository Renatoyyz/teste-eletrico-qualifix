import time

class Dado:
    def __init__(self):
        self.TELA_INICIAL = 0
        self.TELA_LOGIN = 1
        self.TELA_CONFIG = 2
        self.TELA_CADASTRO_USER = 3
        self.TELA_LOGIN_VIEW = 4
        self.TELA_CRIAR_RECEITA = 5
        self.TELA_RECEITA_ESQUERDA = 6
        self.TELA_RECEITA_ESQUERDA_DIELETRICO = 7
        self.TELA_RECEITA_DIREITA = 8
        self.TELA_RECEITA_DIREITA_DIELETRICO = 9
        self.TELA_RECEITA_VIEW = 10
        self.TELA_EXECUCAO =11

        self._telas = self.TELA_INICIAL

        self._nome_login = ""
        self._senha_login = ""
        self._permissao_login = 0
        self.full_scream = False
    @property
    def telas(self):
        return self._telas
    @property
    def nome_login(self):
        return self._nome_login
    @property
    def senha_login(self):
        return self._senha_login
    @property
    def permissao_login(self):
        return self._permissao_login
    
    def set_telas(self,tela):
        self.print_status_tela(tela)
        self._telas = tela
    def set_nome_login(self,nome):
        self._nome_login = nome
    def set_senha_login(self, senha):
        self._senha_login = senha
    def set_permissao_login(self, perm):
        self._permissao_login = perm

    def print_status_tela(self, tela):
        if tela == self.TELA_INICIAL:
            print(f"Está na tela: INICIAL")
        elif tela == self.TELA_CONFIG:
            print(f"Está na tela: CONFIGURACAO")
        elif tela == self.TELA_CADASTRO_USER:
            print(f"Está na tela: CADASTRO_USER")
        elif tela == self.TELA_LOGIN:
            print(f"Está na tela: LOGIN")
        elif tela == self.TELA_LOGIN_VIEW:
            print(f"Está na tela: LOGIN_VIEW")
        elif tela == self.TELA_CRIAR_RECEITA:
            print(f"Está na tela: CRIAR_RECEITA")
        elif tela == self.TELA_RECEITA_ESQUERDA:
            print(f"Está na tela: RECEITA_ESQUERDA")
        elif tela == self.TELA_RECEITA_DIREITA:
            print(f"Está na tela: RECEITA_DIREITA")
        elif tela == self.TELA_RECEITA_ESQUERDA_DIELETRICO:
            print(f"Está na tela: RECEITA_ESQUERDA_DIELETRICO")
        elif tela == self.TELA_RECEITA_DIREITA_DIELETRICO:
            print(f"Está na tela: RECEITA_DIREITA_DIELETRICO")
        elif tela == self.TELA_RECEITA_VIEW:
            print(f"Está na tela: RECEITA_VIEW")
        elif tela == self.TELA_EXECUCAO:
            print(f"Está na tela: EXECUCAO")

            