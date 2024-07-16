from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QCoreApplication, QThread, QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QMetaObject, Q_ARG
from datetime import datetime
from Controller.Message import MessageBox, SimpleMessageBox
from Controller.OpenFile import OpenFile
from View.tela_execucao_programa import Ui_TelaExecucao

class AtualizadorRunnable(QRunnable):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._running = True

    def run(self):
        while self._running:
            try:
                data_hora = datetime.now()
                data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
                QMetaObject.invokeMethod(self.callback, "atualiza_valor", Qt.QueuedConnection, Q_ARG(str, data_formatada))
                QThread.msleep(100)
            except Exception as e:
                print(f"Erro na Thread Atualizador: {e}")
                self._running = False

    def parar(self):
        self._running = False

class ExecutaRotinaRunnable(QRunnable):
    def __init__(self, operacao, callback):
        super().__init__()
        self.operacao = operacao
        self.callback = callback
        self._running = True
        self.esquerda_ok = False
        self.direita_ok = False

    def run(self):
        while self._running:
            try:
                result_condu_e = []
                result_condu_d = []
                result_iso_e = []
                result_iso_d = []

                if self.operacao.em_execucao:
                    if self.operacao.rotina.abaixa_pistao():
                        if self.operacao.habili_desbilita_esquerdo:
                            self.operacao.qual_teste = self.operacao.TESTE_COND_E
                            result_condu_e = self.operacao.rotina.esquerdo_direito_condutividade(0)
                            cond = all(c[2] != 0 for c in result_condu_e)
                            if cond:
                                self.operacao.esquerda_condu_ok = 2
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_E
                                result_iso_e = self.operacao.rotina.esquerdo_direito_isolacao(0)
                                iso = all(i[2] != 1 for i in result_iso_e)
                                if iso:
                                    self.operacao.esquerda_iso_ok = 2
                                else:
                                    self.operacao.esquerda_iso_ok = 1
                                    self.operacao._visualiza_iso_e = True
                            else:
                                iso = False
                                result_iso_e = self.operacao.rotina.fake_isolacao_esquerdo()
                                self.operacao.esquerda_condu_ok = 1
                                self.operacao._visualiza_condu_e = True
                                self.operacao.esquerda_iso_ok = 1
                                self.operacao._visualiza_iso_e = True

                            if cond and iso:
                                self.operacao.rotina.marca_peca_esquerda()
                                self.esquerda_ok = True
                            else:
                                self.esquerda_ok = False
                            self.operacao._carrega_eletrodos(self.operacao.rotina.coord_eletrodo_esquerdo, "E")
                        else:
                            self.esquerda_ok = True

                        if self.operacao.habili_desbilita_direito:
                            self.operacao.qual_teste = self.operacao.TESTE_COND_D
                            result_condu_d = self.operacao.rotina.esquerdo_direito_condutividade(1)
                            cond = all(c[2] != 0 for c in result_condu_d)
                            if cond:
                                self.operacao.direita_condu_ok = 2
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_D
                                result_iso_d = self.operacao.rotina.esquerdo_direito_isolacao(1)
                                iso = all(i[2] != 1 for i in result_iso_d)
                                if iso:
                                    self.operacao.direita_iso_ok = 2
                                else:
                                    self.operacao.direita_iso_ok = 1
                                    self.operacao._visualiza_iso_d = True
                            else:
                                iso = False
                                result_iso_d = self.operacao.rotina.fake_isolacao_direito()
                                self.operacao.direita_condu_ok = 1
                                self.operacao._visualiza_condu_d = True
                                self.operacao.direita_iso_ok = 1
                                self.operacao._visualiza_iso_d = True

                            if cond and iso:
                                self.operacao.rotina.marca_peca_direita()
                                self.direita_ok = True
                            else:
                                self.direita_ok = False
                            self.operacao._carrega_eletrodos(self.operacao.rotina.coord_eletrodo_direito, "D")
                        else:
                            self.direita_ok = True

                    if self.esquerda_ok and self.direita_ok:
                        self.operacao.rotina.acende_verde()
                        self.operacao.rotina.sobe_pistao()
                    else:
                        self.operacao.rotina.acende_vermelho()

                    self.operacao.qual_teste = self.operacao.SEM_TESTE
                    self.operacao.indica_cor_teste_condu("lbContinuIndicaE", self.operacao.CINZA, 0)
                    self.operacao.indica_cor_teste_condu("lbContinuIndicaD", self.operacao.CINZA, 1)
                    self.operacao.indica_cor_teste_iso("lbIsolaIndicaE", self.operacao.CINZA, 0)
                    self.operacao.indica_cor_teste_iso("lbIsolaIndicaD", self.operacao.CINZA, 1)

                    QMetaObject.invokeMethod(self.callback, "execucao", Qt.QueuedConnection, 
                                             Q_ARG(list, result_condu_e), Q_ARG(list, result_iso_e), 
                                             Q_ARG(list, result_condu_d), Q_ARG(list, result_iso_d))
                QThread.msleep(100)
            except Exception as e:
                print(f"Erro na Thread ExecutaRotina: {e}")
                self._running = False

    def parar(self):
        self._running = False

class TelaExecucao(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None, nome_prog=None, continuacao=None, db_rotina=None):
        super().__init__()

        self.inicializa_variaveis(dado, io, db, rotina, nome_prog, continuacao, db_rotina)
        self.inicializa_estados()
        self.inicializa_cores()
        self.inicializa_contadores()
        self.inicializa_testes()
        self.inicializa_ui()
        self.inicializa_conexoes()
        self.carregar_configuracoes()
        self.inicializa_threads()

    def inicializa_variaveis(self, dado, io, db, rotina, nome_prog, continuacao, db_rotina):
        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina
        self.nome_prog = nome_prog
        self.continuacao = continuacao
        self.db_rotina = db_rotina
        self.tempo_ciclo = 0
        self._translate = QCoreApplication.translate

    def inicializa_estados(self):
        self.habili_desbilita_esquerdo = True
        self.habili_desbilita_direito = True
        self.habili_desbilita_esquerdo_old = True
        self.habili_desbilita_direito_old = True
        self.execucao_habilita_desabilita = False
        self.em_execucao = False
        self._nao_passsou_peca = False
        self.esquerda_condu_ok = 0
        self.esquerda_iso_ok = 0
        self.direita_condu_ok = 0
        self.direita_iso_ok = 0

    def inicializa_cores(self):
        self.VERDE = "170, 255, 127"
        self.CINZA = "171, 171, 171"
        self.VERMELHO = "255, 0, 0"
        self.AZUL = "0,255,255"
        self.LILAZ = "192, 82, 206"

    def inicializa_contadores(self):
        self._cnt_ciclos = 1
        self._cnt_peca_passou_e = 0
        self._cnt_peca_passou_d = 0
        self._cnt_peca_reprovou_e = 0
        self._cnt_peca_reprovou_d = 0
        self._cnt_peca_retrabalho_e = 0
        self._cnt_peca_retrabalho_d = 0
        self._cnt_pagina_erro = 0
        self._cnt_acionamento_botao = 0

    def inicializa_testes(self):
        self.SEM_TESTE = 0
        self.TESTE_COND_E = 1
        self.TESTE_COND_D = 2
        self.TESTE_ISO_E = 3
        self.TESTE_ISO_D = 4
        self.qual_teste = self.SEM_TESTE
        self._of = OpenFile()

    def inicializa_ui(self):
        self.ui = Ui_TelaExecucao()
        self.ui.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

    def inicializa_conexoes(self):
        self.ui.btEncerra.clicked.connect(self.botao_encerrar)
        self.ui.btCancela.clicked.connect(self.botao_cancelar)
        self.ui.btCancela.setEnabled(False)
        self.ui.btCancela.setStyleSheet(f"background-color: rgb({self.CINZA});")

    def carregar_configuracoes(self):
        self._dados_opcao_parcial = self.database.select_all()
        self._dados_cabecalho = self.database.select_cabecalho()
        self.ui.lbProg.setText(self._translate("MainWindow", f"{self._dados_cabecalho[0][1]}"))
        self.ui.lbNomeProg.setText(self._translate("MainWindow", f"{self._dados_cabecalho[0][2]}"))

    def inicializa_threads(self):
        self.thread_pool = QThreadPool()

        self.atualizador = AtualizadorRunnable(self)
        self.thread_pool.start(self.atualizador)

        self.executa_rotina = ExecutaRotinaRunnable(self, self)
        self.thread_pool.start(self.executa_rotina)

    def atualiza_valor(self, data_hora):
        self.ui.lbDataHora.setText(data_hora)

    def execucao(self, cond_e, iso_e, cond_d, iso_d):
        self.atualiza_contadores(cond_e, iso_e, cond_d, iso_d)

    def atualiza_contadores(self, cond_e, iso_e, cond_d, iso_d):
        if self.habili_desbilita_esquerdo:
            if all(c[2] != 0 for c in cond_e) and all(i[2] != 1 for i in iso_e):
                self._cnt_peca_passou_e += 1
            else:
                self._cnt_peca_reprovou_e += 1

        if self.habili_desbilita_direito:
            if all(c[2] != 0 for c in cond_d) and all(i[2] != 1 for i in iso_d):
                self._cnt_peca_passou_d += 1
            else:
                self._cnt_peca_reprovou_d += 1

        self.ui.lbCntPecaPassouE.setText(str(self._cnt_peca_passou_e))
        self.ui.lbCntPecaPassouD.setText(str(self._cnt_peca_passou_d))
        self.ui.lbCntPecaReprovouE.setText(str(self._cnt_peca_reprovou_e))
        self.ui.lbCntPecaReprovouD.setText(str(self._cnt_peca_reprovou_d))

    def botao_encerrar(self):
        self.atualizador.parar()
        self.executa_rotina.parar()
        self.accept()

    def botao_cancelar(self):
        self.atualizador.parar()
        self.executa_rotina.parar()
        self.reject()

    def closeEvent(self, event):
        self.atualizador.parar()
        self.executa_rotina.parar()
        event.accept()
