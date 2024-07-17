# Solução de "Falha de Segmentação" com PyQt5 no Raspberry Pi 4 usando QRunnable e QThreadPool

## Introdução

Este documento descreve a solução para problemas de "Falha de Segmentação" ao utilizar PyQt5 no Raspberry Pi 4. A solução envolve o uso de `QRunnable` e `QThreadPool` para gerenciar threads de forma segura e eficiente.

## Abordagem

### Utilização de QRunnable e QThreadPool

O `QRunnable` permite a execução de tarefas em paralelo sem precisar gerenciar diretamente a criação e destruição de threads. O `QThreadPool` gerencia um conjunto de threads reutilizáveis, o que melhora a eficiência do uso de recursos do sistema.

### Exemplo de Código

Aqui está um exemplo de como implementar a atualização da interface do usuário e a execução de rotinas usando `QRunnable` e `QThreadPool`.

#### Código Completo

```python
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, QThreadPool, QRunnable, pyqtSlot, QMetaObject, Q_ARG
from datetime import datetime
from Controller.Message import MessageBox, SimpleMessageBox
from Controller.OpenFile import OpenFile
from View.tela_execucao_programa import Ui_TelaExecucao

class Atualizador(QRunnable):
    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self.sinal_atualizar = operacao.sinal_atualizar

    def run(self):
        while self._running:
            try:
                data_hora = datetime.now()
                data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
                self.sinal_atualizar.emit(data_formatada)
                QThread.msleep(100)
            except Exception as e:
                print(f"Erro na Atualizador: {e}")
                self._running = False

    def parar(self):
        self._running = False

class ExecutaRotinaRunnable(QRunnable):
    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self.sinal_execucao = operacao.sinal_execucao

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

                    self.sinal_execucao.emit(result_condu_e, result_iso_e, result_condu_d, result_iso_d)
                QThread.msleep(100)
            except Exception as e:
                print(f"Erro na ExecutaRotinaRunnable: {e}")
                self._running = False

    def parar(self):
        self._running = False

class TelaExecucao(QDialog):
    sinal_atualizar = pyqtSignal(str)
    sinal_execucao = pyqtSignal(list, list, list, list)

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
        self._cnt_ciclo = 0

    def inicializa_testes(self):
        self.TESTE_COND_E = 0
        self.TESTE_COND_D = 1
        self.TESTE_ISO_E = 2
        self.TESTE_ISO_D = 3
        self.SEM_TESTE = 4

    def inicializa_ui(self):
        self.ui = Ui_TelaExecucao()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(800, 480)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.exec()

    def inicializa_conexoes(self):
        self.ui.btIniciar.clicked.connect(self.iniciar)
        self.ui.btIniciar.setAutoDefault(True)
        self.ui.btIniciar.setDefault(True)
        self.ui.btIniciar.setFocus()
        self.ui.btEncerrar.clicked.connect(self.encerrar)
        self.sinal_atualizar.connect(self.atualizar_tela)
        self.sinal_execucao.connect(self.resultados_teste)

    def carregar_configuracoes(self):
        nome = self.dado['cabecalho'][0]
        bitola = self.dado['cabecalho'][1]
        self.ui.lbNomePrograma.setText(self._translate("Dialog", nome))
        self.ui.lbBitola.setText(self._translate("Dialog", bitola))

    def inicializa_threads(self):
        self.atualizador = Atualizador(self)
        self.thread_pool = QThreadPool()
        self.thread_pool.start(self.atualizador)

    def iniciar(self):
        self.em_execucao = True
        self.executa_rotina_thread = ExecutaRotinaRunnable(self)
        self.thread_pool.start(self.executa_rotina_thread)

    def encerrar(self):
        self.em_execucao = False
        self.atualizador.parar()
        self.executa_rotina_thread.parar()
        self.accept()

    @pyqtSlot(str)
    def atualizar_tela(self, data_hora):
        self.ui.lbDataHora.setText(self._translate("Dialog", data_hora))

    @pyqtSlot(list, list, list, list)
    def resultados_teste(self, cond_e, iso_e, cond_d, iso_d):
        self._result_conducao_esquerdo = cond_e
        self._result_isolacao_esquerdo = iso_e
        self._result_conducao_direito = cond_d
        self._result_isolacao_direito = iso_d
        self.atualiza_resultados_teste(cond_e, iso_e, cond_d, iso_d)

    def atualiza_resultados_teste(self, cond_e, iso_e, cond_d, iso_d):
        # Implementar a lógica de atualização dos resultados dos testes
        pass

    def closeEvent(self, event):
        self.atualizador.parar()
        self.executa_rotina_thread.parar()
        super().closeEvent(event)
