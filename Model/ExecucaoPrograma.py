from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, QThread, pyqtSlot, QMetaObject, Q_ARG
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
            QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
            try:
                data_hora = datetime.now()
                data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
                self.sinal_atualizar.emit(data_formatada)
                self.msleep(100)
            except Exception as e:
                print(f"Erro na Thread Atualizador: {e}")
                self._running = False

    def iniciar(self):
        self._running = True
        self.start()
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

        self.result_condu_e = []
        self.result_condu_d = []
        self.result_iso_e = []
        self.result_iso_d = []

    def run(self):
        while self._running == True:
            # Emite o sinal para atualizar a interface do usuário
            QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
            try:
                if self.operacao.em_execucao == True:
                    # Limpa todas as saídas
                    if self.operacao.rotina.abaixa_pistao() == True:
                        # self.operacao.rotina.limpa_saidas_esquerda_direita()# Desativa todos os relés por segurança
                        if self.operacao.habili_desbilita_esquerdo == True:
                            self.operacao.qual_teste = self.operacao.TESTE_COND_E
                            QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
                            self.result_condu_e = self.operacao.rotina.esquerdo_direito_condutividade(0)# Testa O lado esquerdo
                            # Verifica condutividade
                            cond = all(c[2] != 0 for c in self.result_condu_e)   
                            if cond == True:
                                self.operacao.esquerda_condu_ok = 2 # Sinaliza para execução, que passou
                                # Se condutividade passou continua testando isolação
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_E
                                QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
                                self.result_iso_e = self.operacao.rotina.esquerdo_direito_isolacao(0)# Testa O lado esquerdo
                                # Verifica isolação
                                iso = all(i[2] != 1 for i in self.result_iso_e) 
                                if iso == True:
                                    self.operacao.esquerda_iso_ok = 2 # Sinaliza para execução, que passou
                                else:
                                    self.operacao.esquerda_iso_ok = 1 # Sinaliza para execução, que não passou
                                    self.operacao._visualiza_iso_e = True
                            else:
                                iso = False
                                self.result_iso_e = self.operacao.rotina.fake_isolacao_esquerdo()# Popula lista com valores falsos
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
                            QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
                            self.result_condu_d = self.operacao.rotina.esquerdo_direito_condutividade(1)# Testa O lado direito
                            # Verifica condutividade
                            cond = all(c[2] != 0 for c in self.result_condu_d)  
                            if cond == True:
                                self.operacao.direita_condu_ok = 2 # Sinaliza para execução, que passou
                                # Se condutividade passou continua testando isolação
                                self.operacao.qual_teste = self.operacao.TESTE_ISO_D
                                QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads
                                self.result_iso_d = self.operacao.rotina.esquerdo_direito_isolacao(1)# Testa O lado direito
                                # Verifica isolação
                                iso = all(i[2] != 1 for i in self.result_iso_d)
                                if iso == True:
                                    self.operacao.direita_iso_ok = 2 # Sinaliza para execução, que passou
                                else:
                                    self.operacao.direita_iso_ok = 1 # Sinaliza para execução, que não passou
                                    self.operacao._visualiza_iso_d = True
                            else:
                                iso = False
                                self.result_iso_d = self.operacao.rotina.fake_isolacao_direito()# Popula lista com valores falsos
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
                    
                    
                    # self.operacao.qual_teste = self.operacao.SEM_TESTE
                    # self.operacao.indica_cor_teste_condu("lbContinuIndicaE",self.operacao.CINZA, 0)
                    # self.operacao.indica_cor_teste_condu("lbContinuIndicaD",self.operacao.CINZA, 1)
                    # self.operacao.indica_cor_teste_iso("lbIsolaIndicaE",self.operacao.CINZA, 0)
                    # self.operacao.indica_cor_teste_iso("lbIsolaIndicaD",self.operacao.CINZA, 1)

                    # Emite o evento para conclusão so processo
                    self.sinal_execucao.emit(self.result_condu_e,self.result_iso_e,self.result_condu_d,self.result_iso_d)
                    # self.parar()
                    
                self.msleep(100)  # Cria um atraso de 100 mili segundo
                # print("ExecutaThread")
            except Exception as e:
                    print(f"Erro na Thread ExecutaRotina: {e}")
                    self.parar()

    def iniciar(self):
        self._running = True
        self.start()
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
        # ExecutaRotinaThread
        self.execucao_ = ExecutaRotinaThread(self)
        self.execucao_.sinal_execucao.connect(self.thread_execucao)
        self.execucao_.iniciar()

        # Atualizador Thread
        self.atualizador = Atualizador(self)
        self.atualizador.sinal_atualizar.connect(self.thread_atualizar_valor)
        self.atualizador.iniciar()

        QApplication.processEvents()  # Mantém a UI responsiva após iniciar as threads

    def muda_texto_obj(self, obj_str, text):
        obj_tom_conec = f"{obj_str}"
        cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
        # cur_obj_tom_conec.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">{}</p></body></html>".format(text)))
        cur_obj_tom_conec.setText(str(text))
        # fm = self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">{text}</p></body></html>")
        cur_obj_tom_conec.setText(self._translate("TelaExecucao", f"{text}"))
    def muda_cor_obj(self, obj_str, cor):
    
        obj_tom_conec = f"{obj_str}"
        cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
        cur_obj_tom_conec.setStyleSheet(f"background-color: rgb({cor});")

    def thread_atualizar_valor(self, data_hora):
        QMetaObject.invokeMethod(self, "atualiza_valor", Qt.QueuedConnection, Q_ARG(str, data_hora))


    @pyqtSlot(str)
    def atualiza_valor(self, data_hora):
        self.ui.lbDataHora.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">{data_hora}</p></body></html>"))

        # if self.execucao_habilita_desabilita == True  and self._nao_passsou_peca == False:
        if self.execucao_habilita_desabilita == True and  self.io.io_rpi.bot_acio_e == 0 and self.io.io_rpi.bot_acio_d == 0 and self._nao_passsou_peca == False:
            self.rotina.apaga_torre()
            if self._cnt_acionamento_botao < 1:
                # self.execucao_._running = True
                # self.execucao_.iniciar()
                self.rotina.flag_erro_geral = False
                self._nao_passsou_peca = False
                self.em_execucao = True
                self.tempo_ciclo = 0
                self.muda_texto_obj("txNumerosCiclos",self._cnt_ciclos)
                self.oscila_cor = False
                self._carrega_eletrodos(self.rotina.coord_eletrodo_esquerdo, "E")# O 'E' é para formar o texto que criará o objeto lbEletrodo1_E
                self._carrega_eletrodos(self.rotina.coord_eletrodo_direito, "D")# O 'D' é para formar o texto que criará o objeto lbEletrodo1_D
                self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Testando</p></body></html>"))
                self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
                self._cnt_acionamento_botao+=1# Incrementa para não passar por aqui novamente

                # Variáveis para armazenar condicão de condutividade e isolação dos lados esquerdo e direito colocados em condição de não está sendo avaliado
                # 0 = indica que não está sendo avaliado
                # 1 = indica que não passou
                # 2 = indica que passou
                self.esquerda_condu_ok = 0
                self.esquerda_iso_ok = 0
                self.direita_condu_ok = 0
                self.direita_iso_ok = 0
            
        if self.em_execucao == True and self._nao_passsou_peca == False:# Se está em execução e peça passou

            if self.qual_teste == self.SEM_TESTE:
                self.indica_cor_teste_condu("lbContinuIndicaE",self.CINZA, 0)
                self.indica_cor_teste_condu("lbContinuIndicaD",self.CINZA, 1)
                self.indica_cor_teste_iso("lbIsolaIndicaE",self.CINZA, 0)
                self.indica_cor_teste_iso("lbIsolaIndicaD",self.CINZA, 1)
            elif self.qual_teste == self.TESTE_COND_E:
                self.indica_cor_teste_condu("lbContinuIndicaE",self.VERDE, 0)
                self.indica_cor_teste_condu("lbContinuIndicaD",self.CINZA, 1)
                self.indica_cor_teste_iso("lbIsolaIndicaE",self.CINZA, 0)
                self.indica_cor_teste_iso("lbIsolaIndicaD",self.CINZA, 1)
            elif self.qual_teste == self.TESTE_COND_D:
                self.indica_cor_teste_condu("lbContinuIndicaE",self.CINZA, 0)
                self.indica_cor_teste_condu("lbContinuIndicaD",self.VERDE, 1)
                self.indica_cor_teste_iso("lbIsolaIndicaE",self.CINZA, 0)
                self.indica_cor_teste_iso("lbIsolaIndicaD",self.CINZA, 1)
            elif self.qual_teste == self.TESTE_ISO_E:
                self.indica_cor_teste_condu("lbContinuIndicaE",self.CINZA, 0)
                self.indica_cor_teste_condu("lbContinuIndicaD",self.CINZA, 1)
                self.indica_cor_teste_iso("lbIsolaIndicaE",self.VERDE, 0)
                self.indica_cor_teste_iso("lbIsolaIndicaD",self.CINZA, 1)
            elif self.qual_teste == self.TESTE_ISO_D:
                self.indica_cor_teste_condu("lbContinuIndicaE",self.CINZA, 0)
                self.indica_cor_teste_condu("lbContinuIndicaD",self.CINZA, 1)
                self.indica_cor_teste_iso("lbIsolaIndicaE",self.CINZA, 0)
                self.indica_cor_teste_iso("lbIsolaIndicaD",self.VERDE, 1)
            
            self.cor_eletrodo_teste()

            # A Thread AtualizaValor atualiza de x em x ms
            # para que a indicação de tempo atualiza de 1 em 1 s, aplica-se o algoritimo de resto = 0
            self._ofset_temo += 1
            if (self._ofset_temo % 10) == 0:
                self.tempo_ciclo += 1
                self.ui.txTempoCiclos.setText(f"{self.tempo_ciclo} s")
        elif self.em_execucao == False and self._nao_passsou_peca == True:# Se está em execução e peça não passou
            # Habilita botão de descarte ou retrabalho
            self.ui.btDescartar.setDisabled(False)
            self.ui.btRetrabalhar.setDisabled(False)


            if self._visualiza_condu_e == False and self._visualiza_condu_d == False and self._visualiza_iso_e == False and self._visualiza_iso_d == False:
                self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Erros - Tocar na Tela para visualizar</p></body></html>"))
                self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

            try:
                if self._visualiza_condu_e == True:
                    if self._cnt_pagina_erro > len(self.cond_e)-1:
                        self._cnt_pagina_erro=0


                    if self.habili_desbilita_esquerdo == True and self.cond_e != []:
                        self._carrega_eletrodos_esquerdo(self.rotina.coord_eletrodo_esquerdo, self.rotina.condutividade_esquerdo[f"ligacao{self.cond_e[self._cnt_pagina_erro][0]}"][1][0] , -1)
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.condutividade_esquerdo[f'ligacao{self.cond_e[self._cnt_pagina_erro][0]}'][1][0]}_E",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.cond_e[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de condutividade nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")


                if self._visualiza_condu_d == True:
                    if self._cnt_pagina_erro > len(self.cond_d)-1:
                        self._cnt_pagina_erro=0
                    

                    if self.habili_desbilita_direito == True and self.cond_d != []:
                        self._carrega_eletrodos_direito(self.rotina.coord_eletrodo_direito,self.rotina.condutividade_direito[f"ligacao{self.cond_d[self._cnt_pagina_erro][0]}"][1][0] , -1)
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.condutividade_direito[f'ligacao{self.cond_d[self._cnt_pagina_erro][0]}'][1][0]}_D",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.cond_d[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de condutividade nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")

                if self._visualiza_iso_e == True:
                    if self._cnt_pagina_erro > len(self.iso_e)-1:
                        self._cnt_pagina_erro=0

                    if self.habili_desbilita_esquerdo == True and self.iso_e != []:
                        self._carrega_eletrodos_esquerdo(self.rotina.coord_eletrodo_esquerdo,self.rotina.isolacao_esquerdo[f"ligacao{self.iso_e[self._cnt_pagina_erro][0]}"][3],self.rotina.isolacao_esquerdo[f"ligacao{self.iso_e[self._cnt_pagina_erro][0]}"][4])
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.isolacao_esquerdo[f'ligacao{self.iso_e[self._cnt_pagina_erro][0]}'][3]}_E",self.VERMELHO)
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.isolacao_esquerdo[f'ligacao{self.iso_e[self._cnt_pagina_erro][0]}'][4]}_E",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.iso_e[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de isolação nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")


                if self._visualiza_iso_d == True:
                    if self._cnt_pagina_erro > len(self.iso_d)-1:
                        self._cnt_pagina_erro=0

                    if self.habili_desbilita_direito == True and self.iso_d != []:
                        self._carrega_eletrodos_direito(self.rotina.coord_eletrodo_direito,self.rotina.isolacao_direito[f"ligacao{self.iso_d[self._cnt_pagina_erro][0]}"][3],self.rotina.isolacao_direito[f"ligacao{self.iso_d[self._cnt_pagina_erro][0]}"][4])
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.isolacao_direito[f'ligacao{self.iso_d[self._cnt_pagina_erro][0]}'][3]}_D",self.VERMELHO)
                        self.muda_cor_obj(f"lbEletrodo{self.rotina.isolacao_direito[f'ligacao{self.iso_d[self._cnt_pagina_erro][0]}'][4]}_D",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.iso_d[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de isolação nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")

            except:
                print("ultrapassou indice de lista")

            self._ofset_temo=0
        else:
            self._ofset_temo=0

    def indica_cor_teste_condu(self, obj, cor, lado):
        if lado == 0: # Se for esquerdo
            # Se condições de teste, que é verificado em ExecutaRotinaThread, tiver algum erro, pinta de vermelho
            if self.esquerda_condu_ok == 1:
                self.muda_cor_obj(obj,self.VERMELHO)
            elif self.esquerda_condu_ok == 2:# Se estiver ok, pinta de verde
                self.muda_cor_obj(obj,self.VERDE)
            else:
                self.muda_cor_obj(obj,cor) # caso contrario pinta na cor requerida
        else:
            # Se condições de teste, que é verificado em ExecutaRotinaThread, tiver algum erro, pinta de vermelho
            if self.direita_condu_ok == 1:
                self.muda_cor_obj(obj,self.VERMELHO)
            elif self.direita_condu_ok == 2:# Se estiver ok, pinta de verde
                self.muda_cor_obj(obj,self.VERDE)
            else:
                self.muda_cor_obj(obj,cor) # caso contrario pinta na cor requerida
    def indica_cor_teste_iso(self, obj, cor, lado):
        if lado == 0: # Se for esquerdo
            # Se condições de teste, que é verificado em ExecutaRotinaThread, tiver algum erro, pinta de vermelho
            if self.esquerda_iso_ok == 1:
                self.muda_cor_obj(obj,self.VERMELHO)
            elif self.esquerda_iso_ok == 2:# Se estiver ok, pinta de verde
                self.muda_cor_obj(obj,self.VERDE)
            else:
                self.muda_cor_obj(obj,cor) # caso contrario pinta na cor requerida
        else:
            # Se condições de teste, que é verificado em ExecutaRotinaThread, tiver algum erro, pinta de vermelho
            if self.direita_iso_ok == 1:
                self.muda_cor_obj(obj,self.VERMELHO)
            elif self.direita_iso_ok == 2:# Se estiver ok, pinta de verde
                self.muda_cor_obj(obj,self.VERDE)
            else:
                self.muda_cor_obj(obj,cor) # caso contrario pinta na cor requerida
    
    def cor_eletrodo_teste(self):

        try:
            if self.qual_teste == self.TESTE_COND_E:
                if self.rotina.eletrodo_testando_condu_e[0] != 0:
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_condu_e[0]}_E",self.AZUL)
                    self._carrega_eletrodos_esquerdo(self.rotina.coord_eletrodo_esquerdo, self.rotina.eletrodo_testando_condu_e[0], -1)

            if self.qual_teste == self.TESTE_COND_D:
                if self.rotina.eletrodo_testando_condu_d[0] != 0:
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_condu_d[0]}_D",self.AZUL)
                    self._carrega_eletrodos_direito(self.rotina.coord_eletrodo_direito, self.rotina.eletrodo_testando_condu_d[0], -1)

            if self.qual_teste == self.TESTE_ISO_E:
                if self.rotina.eletrodo_testando_iso_e[0] != 0:
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_iso_e[0]}_E",self.LILAZ)
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_iso_e[1]}_E",self.LILAZ)
                    self._carrega_eletrodos_esquerdo(self.rotina.coord_eletrodo_esquerdo, self.rotina.eletrodo_testando_iso_e[0], self.rotina.eletrodo_testando_iso_e[1])

            if self.qual_teste == self.TESTE_ISO_D:
                if self.rotina.eletrodo_testando_iso_d[0] != 0:
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_iso_d[0]}_D",self.LILAZ)
                    self.muda_cor_obj(f"lbEletrodo{self.rotina.eletrodo_testando_iso_d[1]}_D",self.LILAZ)
                    self._carrega_eletrodos_direito(self.rotina.coord_eletrodo_direito, self.rotina.eletrodo_testando_iso_d[0], self.rotina.eletrodo_testando_iso_d[1])

        except:
            print("Erro de combinação de eletrodos")

    # Método chamado quando finaliza a thread de execução
    def thread_execucao(self, cond_e, iso_e, cond_d, iso_d):
        QMetaObject.invokeMethod(self, "execucao", Qt.QueuedConnection, 
                                 Q_ARG(list, cond_e), Q_ARG(list, iso_e), 
                                 Q_ARG(list, cond_d), Q_ARG(list, iso_d))

    @pyqtSlot(list, list, list, list)
    def execucao(self,  cond_e_, iso_e_, cond_d_, iso_d_):
        if self.em_execucao == True:
            self.qual_teste = self.SEM_TESTE
            self.indica_cor_teste_condu("lbContinuIndicaE",self.CINZA, 0)
            self.indica_cor_teste_condu("lbContinuIndicaD",self.CINZA, 1)
            self.indica_cor_teste_iso("lbIsolaIndicaE",self.CINZA, 0)
            self.indica_cor_teste_iso("lbIsolaIndicaD",self.CINZA, 1)

            self.cond_e.clear()
            self.cond_d.clear()
            self.iso_e.clear()
            self.iso_d.clear()
            print(f"Condutividade esquerdo: {cond_e_}")
            print(f"Isolação esquerdo: {iso_e_}")
            print(f"Condutividade direito: {cond_d_}")
            print(f"Isolação direito: {iso_d_}")
            self.em_execucao = False
            
            # Verifica se peças passaram
            if self.habili_desbilita_direito == True and self.habili_desbilita_esquerdo == True:# Se ambos os lados estiverem habilitados
                if cond_e_ != [] and iso_e_ != [] and cond_d_ != [] and iso_d_ != []:
                    if self._verifica_condutividade_isolacao(cond_e_, iso_e_) == (True,True) and self._verifica_condutividade_isolacao(cond_d_, iso_d_) == (True,True):
                        self._carrega_peca_passou(0)
                        #escrever aqui o liga verde da torre

                    else:# Verifica qual dos dois não passaram

                        if self._verifica_condutividade_isolacao(cond_e_, iso_e_) == (True,True):
                            self._carrega_peca_passou(1)# passou a esquerda habilitada
                        else:
                            # passa para as variáveis somente o que não passou 
                            for i in cond_e_:
                                if i[2] == 0:
                                    self.cond_e.append(i)
                            for i in iso_e_:
                                if i[2] == 1:
                                    self.iso_e.append(i)
                        if self._verifica_condutividade_isolacao(cond_d_, iso_d_) == (True,True):
                            self._carrega_peca_passou(2)# passou a direita habilitada
                        else:
                            # passa para as variáveis somente o que não passou 
                            for i in cond_d_:
                                if i[2] == 0:
                                    self.cond_d.append(i)
                            for i in iso_d_:
                                if i[2] == 1:
                                    self.iso_d.append(i)
                        self.pausa_execucao()
                        # self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")

                        self._nao_passsou_peca = True

                        #escrever aqui o liga Vermelho da torre

            elif self.habili_desbilita_direito == False and self.habili_desbilita_esquerdo == True:# Se só esquerdo estiver habilitado
                if cond_e_ != [] and iso_e_ != []:
                    if self._verifica_condutividade_isolacao(cond_e_, iso_e_) == (True,True):
                        self._carrega_peca_passou(1)
                        #escrever aqui o liga verde da torre
                    else:
                        # passa para as variáveis somente o que não passou 
                        for i in cond_e_:
                            if i[2] == 0:
                                self.cond_e.append(i)
                        for i in iso_e_:
                            if i[2] == 1:
                                self.iso_e.append(i)
                        self._nao_passsou_peca = True
                        self.pausa_execucao()
                        # self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")
                        #escrever aqui o liga vermelha da torre

            elif self.habili_desbilita_direito == True and self.habili_desbilita_esquerdo == False:# Se só direito estiver habilitado
                if cond_d_ != [] and iso_d_ != []:
                    if self._verifica_condutividade_isolacao(cond_d_, iso_d_) == (True,True):
                        self._carrega_peca_passou(2)
                        #escrever aqui o liga verde da torre
                    else:
                        # passa para as variáveis somente o que não passou
                        for i in cond_d_:
                            if i[2] == 0:
                                self.cond_d.append(i)
                        for i in iso_d_:
                            if i[2] == 1:
                                self.iso_d.append(i)
                        self._nao_passsou_peca = True
                        self.pausa_execucao()
                        # self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")
                        #escrever aqui o liga vermelho da torre
        self._cnt_acionamento_botao=0

    # qual_passou = 0 : Passou as duas peças
    #               1 : Passou só a esquerda habilitada
    #               2 : Passou só a direita habilitada
    def _carrega_peca_passou(self, qual_passou):
            if qual_passou == 0:
                self._cnt_ciclos+=1
                if self._retrabalho == False:# Se não for um retrabalho 
                    self._cnt_peca_passou_e += 1
                    self._cnt_peca_passou_d += 1
                    self.ui.txAprovadoE.setText( self._translate("TelaExecucao", f"{self._cnt_peca_passou_e}"))
                    self.ui.txAprovadoD.setText(self._translate("TelaExecucao", f"{self._cnt_peca_passou_d}"))
                    
                else:
                    self._retrabalho = False # Para a próxima vez não ser um retrabalho de novo
                    #recupera valor antigo de direito e esquerdo
                    self.habili_desbilita_esquerdo = self.habili_desbilita_esquerdo_old
                    self.habili_desbilita_direito = self.habili_desbilita_direito_old
                    
                    if self.habili_desbilita_esquerdo == False:
                        self.ui.lbImgEsquerdo.setEnabled(False)
                    else:
                        self.ui.lbImgEsquerdo.setEnabled(True)

                    if self.habili_desbilita_direito == False:
                        self.ui.lbImgDireito.setEnabled(False)
                    else:
                        self.ui.lbImgDireito.setEnabled(True)

                    self._cnt_peca_retrabalho_e+=1
                    self._cnt_peca_retrabalho_d+=1
                    self.ui.txRetrabalhoE.setText( self._translate("TelaExecucao", f"{self._cnt_peca_retrabalho_e}"))
                    self.ui.txRetrabalhoD.setText(self._translate("TelaExecucao", f"{self._cnt_peca_retrabalho_d}"))

                self._carrega_eletrodos(self.rotina.coord_eletrodo_esquerdo, "E")
                self._carrega_eletrodos(self.rotina.coord_eletrodo_direito, "D")
                self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
                self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
                
            elif qual_passou == 1:
                self._cnt_ciclos+=1
                if self._retrabalho == False:# Se não for um retralho 
                    self._cnt_peca_passou_e += 1
                    self.ui.txAprovadoE.setText( self._translate("TelaExecucao", f"{self._cnt_peca_passou_e}"))
                else:
                    self._retrabalho = False # Para a próxima vez não ser um retrabalho de novo
                    #recupera valor antigo de direito e esquerdo
                    self.habili_desbilita_esquerdo = self.habili_desbilita_esquerdo_old
                    self.habili_desbilita_direito = self.habili_desbilita_direito_old
                    
                    if self.habili_desbilita_esquerdo == False:
                        self.ui.lbImgEsquerdo.setEnabled(False)
                    else:
                        self.ui.lbImgEsquerdo.setEnabled(True)

                    if self.habili_desbilita_direito == False:
                        self.ui.lbImgDireito.setEnabled(False)
                    else:
                        self.ui.lbImgDireito.setEnabled(True)
                    

                    self._cnt_peca_retrabalho_e+=1
                    self.ui.txRetrabalhoE.setText( self._translate("TelaExecucao", f"{self._cnt_peca_retrabalho_e}"))

                self._carrega_eletrodos(self.rotina.coord_eletrodo_esquerdo, "E")
                self._carrega_eletrodos(self.rotina.coord_eletrodo_direito, "D")
                self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
                self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
            elif qual_passou == 2:
                self._cnt_ciclos+=1
                if self._retrabalho == False:# Se não for um retralho 
                    self._cnt_peca_passou_d += 1
                    self.ui.txAprovadoD.setText(self._translate("TelaExecucao", f"{self._cnt_peca_passou_d}"))
                else:
                    self._retrabalho = False # Para a próxima vez não ser um retrabalho de novo
                    #recupera valor antigo de direito e esquerdo
                    self.habili_desbilita_esquerdo = self.habili_desbilita_esquerdo_old
                    self.habili_desbilita_direito = self.habili_desbilita_direito_old
                    
                    if self.habili_desbilita_esquerdo == False:
                        self.ui.lbImgEsquerdo.setEnabled(False)
                    else:
                        self.ui.lbImgEsquerdo.setEnabled(True)

                    if self.habili_desbilita_direito == False:
                        self.ui.lbImgDireito.setEnabled(False)
                    else:
                        self.ui.lbImgDireito.setEnabled(True)

                    self._cnt_peca_retrabalho_d+=1
                    self.ui.txRetrabalhoD.setText( self._translate("TelaExecucao", f"{self._cnt_peca_retrabalho_d}"))

                self._carrega_eletrodos(self.rotina.coord_eletrodo_esquerdo, "E")
                self._carrega_eletrodos(self.rotina.coord_eletrodo_direito, "D")
                self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
                self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")

            self.salva_rotina()# Atualiza dados no banco de dados


    def _verifica_condutividade_isolacao(self, condu, iso):
        ret_cond = False
        ret_iso = False
        try:
            for i in range(len(condu)):
                if condu[i][2] == 0:
                    ret_cond = False
                    break
                else:
                    ret_cond = True
            for i in range(len(iso)):
                if iso[i][2] == 1:
                    ret_iso = False
                    break
                else:
                    ret_iso = True
        except:
            print("Erro em _verifica_condutividade_isolacao...")
            ret_cond = False
            ret_iso = False
        return ret_cond, ret_iso

    def load_config(self):
        self.qual_teste = self.SEM_TESTE
        self.muda_cor_obj("lbContinuIndicaE",self.CINZA)
        self.muda_cor_obj("lbContinuIndicaD",self.CINZA)
        self.muda_cor_obj("lbIsolaIndicaE",self.CINZA)
        self.muda_cor_obj("lbIsolaIndicaD",self.CINZA)

        self.ui.btRetrabalhar.setDisabled(True)
        self.ui.btDescartar.setDisabled(True)
        self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina parada</p></body></html>"))
        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
        try:
            self.id, self.rotina.nome_programa, self.rotina.url_img_esquerdo, self.rotina.url_img_direito, self.rotina.coord_eletrodo_esquerdo, self.rotina.coord_eletrodo_direito, self.rotina.condutividade_esquerdo, self.rotina.condutividade_direito, self.rotina.isolacao_esquerdo, self.rotina.isolacao_direito = self.database.search_name_receita(self.nome_prog)

            if self.continuacao == True:# Se for uma continuação de outra rotina
                self.rotina_iniciada = self.continuacao
                self.ui.txAprovadoE.setText(str(self.db_rotina[2]))
                self.ui.txAprovadoD.setText(str(self.db_rotina[3]))
                self.ui.txReprovadoE.setText(str(self.db_rotina[4]))
                self.ui.txReprovadoD.setText(str(self.db_rotina[5]))
                self.ui.txRetrabalhoE.setText(str(self.db_rotina[6]))
                self.ui.txRetrabalhoD.setText(str(self.db_rotina[7]))
                self.ui.txNumerosCiclos.setText(str(self.db_rotina[12]))
                self._cnt_ciclos = self.db_rotina[12]
                self._nome_rotina_execucao = self.db_rotina[1]
            else:
                # formata nome da rotina
                self._nome_rotina_execucao = f"{self.rotina.nome_programa}${datetime.now().strftime('%d%m%Y_%H%M%S')}"

            
            # Carrega as duas imagens
            dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
            dir_open.load_image_url(image_path=self.rotina.url_img_esquerdo , size_x=self.ui.lbImgEsquerdo.width() , size_y=self.ui.lbImgEsquerdo.height())
            if dir_open.image != None:
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
            dir_open.load_image_url(image_path=self.rotina.url_img_direito , size_x=self.ui.lbImgDireito.width() , size_y=self.ui.lbImgDireito.height())
            if dir_open.image != None:
                self.ui.lbImgDireito.setPixmap(dir_open.image)

            #Atribui nome do programa
            self.ui.lbNomePrograma.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">{self.rotina.nome_programa}</p></body></html>"))

            #Limpa os eletrodos
            self.limpaeletrodo()
            self.rotina.limpa_saidas_esquerda_direita()# Desativa todos os relés por segurança

            self._carrega_eletrodos(self.rotina.coord_eletrodo_esquerdo, "E")# O 'E' é para formar o texto que criará o objeto lbEletrodo1_E
            self._carrega_eletrodos(self.rotina.coord_eletrodo_direito, "D")# O 'D' é para formar o texto que criará o objeto lbEletrodo1_D

        except:
            print("Erro de carregamento...")

    def _carrega_eletrodos(self, coord, lado):
        try:
            for index in range(0,len(coord)):
                if coord[index] != None:
                    obj_tom_conec = f"lbEletrodo{index}_{lado}"
                    cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
                    cur_obj_tom_conec.move( coord[index][0] - cur_obj_tom_conec.width() // 2,coord[index][1] - cur_obj_tom_conec.height() // 2)
                    cur_obj_tom_conec.setVisible(True)
                    cur_obj_tom_conec.setStyleSheet(f"background-color: rgb({self.VERDE});")

        except:
            print("Erro de objeto do eletrodo")

    def _carrega_eletrodos_esquerdo(self, coord, exceto, exceto2):
        try:
            for index in range(0,len(coord)):
                if coord[index] != None and index != exceto and index != exceto2:
                    obj_tom_conec = f"lbEletrodo{index}_E"
                    cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
                    cur_obj_tom_conec.move( coord[index][0] - cur_obj_tom_conec.width() // 2,coord[index][1] - cur_obj_tom_conec.height() // 2)
                    cur_obj_tom_conec.setVisible(True)
                    cur_obj_tom_conec.setStyleSheet(f"background-color: rgb({self.VERDE});")

        except:
            print("Erro de objeto do eletrodo esquerdo")

    def _carrega_eletrodos_direito(self, coord, exceto, exceto2):
        try:
            for index in range(0,len(coord)):
                if coord[index] != None and index != exceto and index != exceto2:
                    obj_tom_conec = f"lbEletrodo{index}_D"
                    cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
                    cur_obj_tom_conec.move( coord[index][0] - cur_obj_tom_conec.width() // 2,coord[index][1] - cur_obj_tom_conec.height() // 2)
                    cur_obj_tom_conec.setVisible(True)
                    cur_obj_tom_conec.setStyleSheet(f"background-color: rgb({self.VERDE});")

        except:
            print("Erro de objeto do eletrodo direito")
    
    def limpaeletrodo(self):
        self.ui.lbEletrodo1_D.setVisible(False)
        self.ui.lbEletrodo1_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo2_D.setVisible(False)
        self.ui.lbEletrodo2_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo3_D.setVisible(False)
        self.ui.lbEletrodo3_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo4_D.setVisible(False)
        self.ui.lbEletrodo4_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo5_D.setVisible(False)
        self.ui.lbEletrodo5_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo6_D.setVisible(False)
        self.ui.lbEletrodo6_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo7_D.setVisible(False)
        self.ui.lbEletrodo7_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo8_D.setVisible(False)
        self.ui.lbEletrodo8_D.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo1_E.setVisible(False)
        self.ui.lbEletrodo1_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo2_E.setVisible(False)
        self.ui.lbEletrodo2_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo3_E.setVisible(False)
        self.ui.lbEletrodo3_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo4_E.setVisible(False)
        self.ui.lbEletrodo4_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo5_E.setVisible(False)
        self.ui.lbEletrodo5_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo6_E.setVisible(False)
        self.ui.lbEletrodo6_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo7_E.setVisible(False)
        self.ui.lbEletrodo7_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo8_E.setVisible(False)
        self.ui.lbEletrodo8_E.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas
        
    def desabilita_esquerdo(self):
        if self.habili_desbilita_direito == True:
            self.habili_desbilita_esquerdo = not self.habili_desbilita_esquerdo
            if self.habili_desbilita_esquerdo == False:
                self.ui.lbImgEsquerdo.setEnabled(False)
            else:
                self.ui.lbImgEsquerdo.setEnabled(True)
    def desabilita_direito(self):
        if self.habili_desbilita_esquerdo == True:
            self.habili_desbilita_direito = not self.habili_desbilita_direito
            if self.habili_desbilita_direito == False:
                self.ui.lbImgDireito.setEnabled(False)
            else:
                self.ui.lbImgDireito.setEnabled(True)

    def inicia_execucao(self):
        if self.execucao_habilita_desabilita == False:
            self.rotina.sobe_pistao()
            self.muda_texto_obj("txNumerosCiclos",self._cnt_ciclos)
            self.execucao_habilita_desabilita = True# Habilita para executar programa
            # Desabilita botões que não podem ser acionados durante programa
            self._desabilita_botoes(False)
            self.ui.lbAvisos.setVisible(True)
            self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
            self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
            self._cnt_acionamento_botao=0

    def pausa_execucao(self):
        self.execucao_habilita_desabilita = False# desabilita para executar programa
        self.em_execucao = False
        self.rotina.flag_erro_geral = True
        # Habilita botões que não podem ser acionados durante programa
        self._desabilita_botoes(True)
        self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Parada</p></body></html>"))
        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
        self._cnt_acionamento_botao=0

    def para_execucao(self):
        self.msg_box.exec(msg="Deseja realmente encerar rotina?")
        if self.msg_box.yes_no == True:
            self.salva_rotina(finalizado=True)
            self._nao_passsou_peca = False# Flag de peça não passo habilitada para novo teste
            self._desabilita_botoes(False)
            self.ui.lbAvisos.setVisible(True)
            self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
            self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
            self._cnt_acionamento_botao=0
            self.ui.btDescartar.setDisabled(True)# Volta a desabilitar esse botão
            self.ui.btRetrabalhar.setDisabled(True)# Volta a desabilitar esse botão
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self._visualiza_condu_e = False
            self._visualiza_condu_d = False
            self._visualiza_iso_e = False
            self._visualiza_iso_d = False
            self._retrabalho = True
            self.rotina_iniciada = False
            self.close()
        # self.execucao_habilita_desabilita = False# desabilita para executar programa
        # self.em_execucao = False
        # self.rotina.flag_erro_geral = True
        # # Habilita botões que não podem ser acionados durante programa
        # self._desabilita_botoes(True)

    def botao_retrabalho(self):
        self._nao_passsou_peca = False# Flag de peça não passo habilitada para novo teste
        self._desabilita_botoes(False)
        self.ui.lbAvisos.setVisible(True)
        self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
        self._cnt_acionamento_botao=0
        self.ui.btDescartar.setDisabled(True)# Volta a desabilitar esse botão
        self.ui.btRetrabalhar.setDisabled(True)# Volta a desabilitar esse botão
        self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self._visualiza_condu_e = False
        self._visualiza_condu_d = False
        self._visualiza_iso_e = False
        self._visualiza_iso_d = False
        self._retrabalho = True

        # Variáveis para armazenar condicão de condutividade e isolação dos lados esquerdo e direito colocados em condição de não está sendo avaliado
        # 0 = indica que não está sendo avaliado
        # 1 = indica que não passou
        # 2 = indica que passou
        self.esquerda_condu_ok = 0
        self.esquerda_iso_ok = 0
        self.direita_condu_ok = 0
        self.direita_iso_ok = 0

        # Guarda o valor antigo de direito e esquerdo
        self.habili_desbilita_esquerdo_old = self.habili_desbilita_esquerdo
        self.habili_desbilita_direito_old = self.habili_desbilita_direito

        if (self.cond_e != [] or self.iso_e != []) and (self.cond_d != [] or self.iso_d != []):# se os dois lados estiverem com problemas
            self.habili_desbilita_esquerdo = True
            self.ui.lbImgEsquerdo.setEnabled(True)
            self.habili_desbilita_direito = True
            self.ui.lbImgDireito.setEnabled(True)
        elif self.cond_e != [] or self.iso_e != []:# Se só o lado esquerdo estiver com problemas
            self.habili_desbilita_esquerdo = True
            self.ui.lbImgEsquerdo.setEnabled(True)
            self.habili_desbilita_direito = False
            self.ui.lbImgDireito.setEnabled(False)
        elif self.cond_d != [] or self.iso_d != []:# Se só o lado direito estiver com problemas
            self.habili_desbilita_esquerdo = False
            self.ui.lbImgEsquerdo.setEnabled(False)
            self.habili_desbilita_direito = True
            self.ui.lbImgDireito.setEnabled(True)


    def botao_descarte(self):
        self._nao_passsou_peca = False# Flag de peça não passo habilitada para novo teste
        self._desabilita_botoes(False)
        self.ui.lbAvisos.setVisible(True)
        self.ui.lbAvisos.setText(self._translate("TelaExecucao", "<html><head/><body><p align=\"center\">Máquina pronta</p></body></html>"))
        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERDE});")
        self._cnt_acionamento_botao=0
        self.ui.btDescartar.setDisabled(True)# Volta a desabilitar esse botão
        self.ui.btRetrabalhar.setDisabled(True)# Volta a desabilitar esse botão
        self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
        self._visualiza_condu_e = False
        self._visualiza_condu_d = False
        self._visualiza_iso_e = False
        self._visualiza_iso_d = False

        # Variáveis para armazenar condicão de condutividade e isolação dos lados esquerdo e direito colocados em condição de não está sendo avaliado
        # 0 = indica que não está sendo avaliado
        # 1 = indica que não passou
        # 2 = indica que passou
        self.esquerda_condu_ok = 0
        self.esquerda_iso_ok = 0
        self.direita_condu_ok = 0
        self.direita_iso_ok = 0

        if (self.cond_e != [] or self.iso_e != []) and (self.cond_d != [] or self.iso_d != []):# se os dois lados estiverem com problemas
            self._cnt_peca_reprovou_e+=1
            self._cnt_peca_reprovou_d+=1
            self.ui.txReprovadoE.setText(f"{self._cnt_peca_reprovou_e}")
            self.ui.txReprovadoD.setText(f"{self._cnt_peca_reprovou_d}")
        elif self.cond_e != [] or self.iso_e != []:# Se só o lado esquerdo estiver com problemas
            self._cnt_peca_reprovou_e+=1
            self.ui.txReprovadoE.setText(f"{self._cnt_peca_reprovou_e}")
        elif self.cond_d != [] or self.iso_d != []:# Se só o lado direito estiver com problemas
            self._cnt_peca_reprovou_d+=1
            self.ui.txReprovadoD.setText(f"{self._cnt_peca_reprovou_d}")
        self.salva_rotina()

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
        try:
            self.atualizador.parar()
            self.atualizador.wait()  # Aguarde a thread finalizar

            self.execucao_.parar()
            self.execucao_.wait()  # Aguarde a thread finalizar
        except Exception as e:
            print(f"Erro ao finalizar threads: {e}")
        event.accept()