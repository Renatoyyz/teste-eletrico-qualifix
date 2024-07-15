from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, QThread
from datetime import datetime
from Controller.Message import MessageBox, SimpleMessageBox
from Controller.OpenFile import OpenFile
from View.tela_execucao_programa import Ui_TelaExecucao

from datetime import datetime

class Atualizador(QThread):
    sinal_atualizar = pyqtSignal(str)

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True

    def run(self):
        while self._running:
            try:
                data_hora = datetime.now()
                data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
                self.sinal_atualizar.emit(data_formatada)
                self.msleep(100)
            except Exception as e:
                print(f"Erro na Thread Atualizador: {e}")
                self._running = False

    def parar(self):
        self._running = False

class ExecutaRotinaThread(QThread):
    sinal_execucao = pyqtSignal(list,list,list,list)# Inicializa com a quantidade de variáveis que se deseja

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self.esquerda_ok =False
        self.direita_ok =False

    def run(self):
        while self._running == True:
            try:
                # Emite o sinal para atualizar a interface do usuário
                result_condu_e = []
                result_condu_d = []
                result_iso_e = []
                result_iso_d = []
                
                if self.operacao.em_execucao == True:
                    # Limpa todas as saídas
                    if self.operacao.rotina.abaixa_pistao() == True:
                        # self.operacao.rotina.limpa_saidas_esquerda_direita()# Desativa todos os relés por segurança
                        if self.operacao.habili_desbilita_esquerdo == True:
                            self.operacao.qual_teste = self.operacao.TESTE_COND_E
                            result_condu_e = self.operacao.rotina.esquerdo_direito_condutividade(0)# Testa O lado esquerdo
                            # Verifica condutividade
                            cond = all(c[2] != 0 for c in result_condu_e)   
                            if cond == True:
                                self.operacao.esquerda_condu_ok = 2 # Sinaliza para execução, que passou
                                # Se condutividade passou continua testando isolação
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_E
                                result_iso_e = self.operacao.rotina.esquerdo_direito_isolacao(0)# Testa O lado esquerdo
                                # Verifica isolação
                                iso = all(i[2] != 1 for i in result_iso_e) 
                                if iso == True:
                                    self.operacao.esquerda_iso_ok = 2 # Sinaliza para execução, que passou
                                else:
                                    self.operacao.esquerda_iso_ok = 1 # Sinaliza para execução, que não passou
                                    self.operacao._visualiza_iso_e = True
                            else:
                                iso = False
                                result_iso_e = self.operacao.rotina.fake_isolacao_esquerdo()# Popula lista com valores falsos
                                self.operacao.esquerda_condu_ok = 1 # Sinaliza para execução, que não passou
                                self.operacao._visualiza_condu_e = True
                                self.operacao.esquerda_iso_ok = 1 # Sinaliza para execução, que não passou
                                self.operacao._visualiza_iso_e = True

                            # Se teste de condutividade e de isolação passaram
                            if cond == True and iso ==  True:
                                self.operacao.rotina.marca_peca_esquerda()
                                self.esquerda_ok = True
                            else:
                                self.esquerda_ok = False

                            # garante que todas os eletrodos fiquem verdes para ser tocados depois
                            self.operacao._carrega_eletrodos(self.operacao.rotina.coord_eletrodo_esquerdo, "E")# O 'E' é para formar o texto que criará o objeto lbEletrodo1_E   
                        else:
                            self.esquerda_ok = True # Se Lado esquerdo não foi escolhido, sinaliza como ok para poder 
                                                    # continuar com o lado direito

                        if self.operacao.habili_desbilita_direito == True:
                            self.operacao.qual_teste = self.operacao.TESTE_COND_D
                            result_condu_d = self.operacao.rotina.esquerdo_direito_condutividade(1)# Testa O lado direito
                            # Verifica condutividade
                            cond = all(c[2] != 0 for c in result_condu_d)  
                            if cond == True:
                                self.operacao.direita_condu_ok = 2 # Sinaliza para execução, que passou
                                # Se condutividade passou continua testando isolação
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_D
                                result_iso_d = self.operacao.rotina.esquerdo_direito_isolacao(1)# Testa O lado direito
                                # Verifica isolação
                                iso = all(i[2] != 1 for i in result_iso_d)
                                if iso == True:
                                    self.operacao.direita_iso_ok = 2 # Sinaliza para execução, que passou
                                else:
                                    self.operacao.direita_iso_ok = 1 # Sinaliza para execução, que não passou
                                    self.operacao._visualiza_iso_d = True
                            else:
                                iso = False
                                result_iso_d = self.operacao.rotina.fake_isolacao_direito()# Popula lista com valores falsos
                                self.operacao.direita_condu_ok = 1 # Sinaliza para execução, que não passou
                                self.operacao._visualiza_condu_d = True
                                self.operacao.direita_iso_ok = 1 # Sinaliza para execução, que não passou
                                self.operacao._visualiza_iso_d = True

                            # Se teste de condutividade e de isolação passaram
                            if cond == True and iso ==  True:
                                self.operacao.rotina.marca_peca_direita()
                                self.direita_ok = True
                            else:
                                self.direita_ok = False
                            # garante que todas os eletrodos fiquem verdes para ser tocados depois
                            self.operacao._carrega_eletrodos(self.operacao.rotina.coord_eletrodo_direito, "D")# O 'D' é para formar o texto que criará o objeto lbEletrodo1_D
                        else:
                            self.direita_ok = True # Se Lado direito não foi escolhido, sinaliza como ok para poder 
                                                    # continuar com o lado esquerdo    
                            
                    if self.esquerda_ok == True and self.direita_ok == True:
                        self.operacao.rotina.acende_verde()
                        self.operacao.rotina.sobe_pistao()
                    else:
                        self.operacao.rotina.acende_vermelho()# Se acender vermelho, continua com pistão em baixo
                    
                    
                    self.operacao.qual_teste = self.operacao.SEM_TESTE
                    self.operacao.indica_cor_teste_condu("lbContinuIndicaE",self.operacao.CINZA, 0)
                    self.operacao.indica_cor_teste_condu("lbContinuIndicaD",self.operacao.CINZA, 1)
                    self.operacao.indica_cor_teste_iso("lbIsolaIndicaE",self.operacao.CINZA, 0)
                    self.operacao.indica_cor_teste_iso("lbIsolaIndicaD",self.operacao.CINZA, 1)

                    # Emite o evento para conclusão so processo
                    self.sinal_execucao.emit(result_condu_e,result_iso_e,result_condu_d,result_iso_d)
                self.msleep(100)  # Cria um atraso de 100 mili segundo
                # QApplication.processEvents()
                # Aguarda 1 segundo antes de atualizar novamente
                # self.sleep_ms(0.5)
                # QTimer.singleShot(500, lambda: None)  # Substitui sleep_ms com QTimer diretamente
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
        self._ofset_temo = 0
        self._retrabalho = False
        self.rotina_iniciada = False
        self._nome_rotina_execucao = ""
        self._visualiza_condu_e = False
        self._visualiza_condu_d = False
        self._visualiza_iso_e = False
        self._visualiza_iso_d = False
        self.oscila_cor = False
        self.cond_e = []
        self.iso_e = []
        self.cond_d = []
        self.iso_d = []

    def inicializa_ui(self):
        self.msg = SimpleMessageBox()
        self.msg_box = MessageBox()
        self.ui = Ui_TelaExecucao()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        if self.dado.full_scream:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

    def inicializa_conexoes(self):
        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btDesHabEsquerdo.clicked.connect(self.desabilita_esquerdo)
        self.ui.btDesHabDireito.clicked.connect(self.desabilita_direito)
        self.ui.btIniciar.clicked.connect(self.inicia_execucao)
        self.ui.btPausar.clicked.connect(self.pausa_execucao)
        self.ui.btFinalizar.clicked.connect(self.para_execucao)
        self.ui.btRetrabalhar.clicked.connect(self.botao_retrabalho)
        self.ui.btDescartar.clicked.connect(self.botao_descarte)
        self.ui.lbImgEsquerdo.mousePressEvent = self.img_esquerda_clicada
        self.ui.lbImgDireito.mousePressEvent = self.img_direita_clicada
        self.ui.lbContinuIndicaE.mousePressEvent = self.select_visu_cond_e
        self.ui.lbContinuIndicaD.mousePressEvent = self.select_visu_cond_d
        self.ui.lbIsolaIndicaE.mousePressEvent = self.select_visu_iso_e
        self.ui.lbIsolaIndicaD.mousePressEvent = self.select_visu_iso_d

    def carregar_configuracoes(self):
        self.load_config()

    def inicializa_threads(self):
        # Atualizador Thread
        self.atualizador = Atualizador(self)
        self.atualizador.sinal_atualizar.connect(self.thread_atualizar_valor)
        self.atualizador.start()

        # ExecutaRotinaThread
        self.execucao = ExecutaRotinaThread(self)
        self.execucao.sinal_execucao.connect(self.thread_execucao)
        self.execucao.start()


    def muda_texto_obj(self, obj_str, text):
        # Restante do código
        pass
    def muda_cor_obj(self, obj_str, cor):
        # Restante do código
        pass

    def thread_atualizar_valor(self, data_hora):
        # Restante do código
        pass

    def indica_cor_teste_condu(self, obj, cor, lado):
        # Restante do código
        pass
    def indica_cor_teste_iso(self, obj, cor, lado):
        # Restante do código
        pass
    
    def cor_eletrodo_teste(self):

        # Restante do código
        pass

    # Método chamado quando finaliza a thread de execução
    def thread_execucao(self, cond_e, iso_e, cond_d, iso_d):
        # Restante do código
        pass
    def _carrega_peca_passou(self, qual_passou):
            # Restante do código
        pass


    def _verifica_condutividade_isolacao(self, condu, iso):
        # Restante do código
        pass

    def load_config(self):
        # Restante do código
        pass

    def _carrega_eletrodos(self, coord, lado):
       # Restante do código
        pass

    def _carrega_eletrodos_esquerdo(self, coord, exceto, exceto2):
        # Restante do código
        pass

    def _carrega_eletrodos_direito(self, coord, exceto, exceto2):
        # Restante do código
        pass
    
    def limpaeletrodo(self):
        # Restante do código
        pass
        
    def desabilita_esquerdo(self):
        # Restante do código
        pass
    def desabilita_direito(self):
        # Restante do código
        pass
    def inicia_execucao(self):
        # Restante do código
        pass

    def pausa_execucao(self):
        # Restante do código
        pass

    def para_execucao(self):
        # Restante do código
        pass

    def botao_retrabalho(self):
        # Restante do código
        pass


    def botao_descarte(self):
        # Restante do código
        pass

    def img_esquerda_clicada(self, event):
        self._cnt_pagina_erro+=1
    
    def img_direita_clicada(self, event):
        self._cnt_pagina_erro+=1

    def select_visu_cond_e(self, event):
        if self.habili_desbilita_esquerdo == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = True
            self._visualiza_condu_d = False
            self._visualiza_iso_e = False
            self._visualiza_iso_d = False
            self.selecao_visualisacao()


    def select_visu_iso_e(self, event):
        if self.habili_desbilita_esquerdo == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = False
            self._visualiza_iso_e = True
            self._visualiza_iso_d = False
            self.selecao_visualisacao()

    def select_visu_cond_d(self, event):
        if self.habili_desbilita_direito == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = True
            self._visualiza_iso_e = False
            self._visualiza_iso_d = False
            self.selecao_visualisacao()

    def select_visu_iso_d(self, event):
        if self.habili_desbilita_direito == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = False
            self._visualiza_iso_e = False
            self._visualiza_iso_d = True
            self.selecao_visualisacao()
    def selecao_visualisacao(self):
        if self.esquerda_condu_ok == 2: # Se condutividade está ok
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.VERDE});")
        elif self.esquerda_condu_ok == 1: # Se condutividade não está ok
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

        if self.direita_condu_ok == 2: # Se condutividade está ok
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.VERDE});")
        elif self.direita_condu_ok == 1: # Se condutividade não está ok
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

        if self.esquerda_iso_ok == 2: # Se isolação estiver ok
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.VERDE});")
        elif self.esquerda_iso_ok == 1: # Se isolação não estiver ok
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                
        if self.direita_iso_ok == 2: # Se isolação está ok
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.VERDE});")
        elif self.direita_iso_ok == 1: # Se isolação não estiver ok
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

    def _desabilita_botoes(self, hab_dasab):
        # Desabilita ou habilita botões que não podem ser acionados durante programa
        self.ui.btDesHabEsquerdo.setEnabled(hab_dasab)
        self.ui.btDesHabDireito.setEnabled(hab_dasab)
        self.ui.btVoltar.setEnabled(hab_dasab)
        self.ui.btContato.setEnabled(hab_dasab)

    def salva_rotina(self, finalizado=False):
        try:
            if finalizado == False:

                if self.rotina_iniciada == False:# Se for a primeira vez
                    self.rotina_iniciada = True # Sinaliza variável que indica que já foi gravado
                    self.database.create_record_rotina(self._nome_rotina_execucao,
                                                    int(self.ui.txAprovadoE.text()),
                                                    int(self.ui.txAprovadoD.text()),
                                                    int(self.ui.txReprovadoE.text()),
                                                    int(self.ui.txReprovadoD.text()),
                                                    int(self.ui.txRetrabalhoE.text()),
                                                    int(self.ui.txRetrabalhoD.text()),
                                                    datetime.now(),
                                                    datetime.now(),
                                                    self.dado.nome_login,
                                                    0,# Zero indica que não terminou rotina
                                                    int(self.ui.txNumerosCiclos.text())
                                                    )
                else:
                    self.database.update_record_rotina_by_name_sem_data(self._nome_rotina_execucao,
                                                                        self._nome_rotina_execucao,
                                                                        int(self.ui.txAprovadoE.text()),
                                                                        int(self.ui.txAprovadoD.text()),
                                                                        int(self.ui.txReprovadoE.text()),
                                                                        int(self.ui.txReprovadoD.text()),
                                                                        int(self.ui.txRetrabalhoE.text()),
                                                                        int(self.ui.txRetrabalhoD.text()),
                                                                        self.dado.nome_login,
                                                                        0,# Zero indica que não terminou rotina
                                                                        int(self.ui.txNumerosCiclos.text())
                                                                    )
            else:
                self.database.update_record_rotina_by_name_finalizado(self._nome_rotina_execucao,
                                                                        self._nome_rotina_execucao,
                                                                        int(self.ui.txAprovadoE.text()),
                                                                        int(self.ui.txAprovadoD.text()),
                                                                        int(self.ui.txReprovadoE.text()),
                                                                        int(self.ui.txReprovadoD.text()),
                                                                        int(self.ui.txRetrabalhoE.text()),
                                                                        int(self.ui.txRetrabalhoD.text()),
                                                                        datetime.now(),#Data de finalização
                                                                        self.dado.nome_login,
                                                                        1,# Um indica terminou rotina
                                                                        int(self.ui.txNumerosCiclos.text())
                                                                    )
        except:
            print("Erro em salvar_rotina(), banco de dados")


    def voltar(self):
        self.dado.set_telas(self.dado.TELA_INICIAL)
        self.close()
    def closeEvent(self, event):
        self.atualizador.parar()
        self.atualizador.wait()  # Aguarde a thread finalizar

        self.execucao.parar()
        self.execucao.wait()  # Aguarde a thread finalizar
        event.accept()
