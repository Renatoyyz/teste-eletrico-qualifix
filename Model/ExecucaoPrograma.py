from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, QThread
import time
from datetime import datetime
from typing import Any

from Controller.Message import MessageBox, SimpleMessageBox

from Controller.OpenFile import OpenFile
from View.tela_execucao_programa import Ui_TelaExecucao

class Atualizador(QObject):
    sinal_atualizar = pyqtSignal(str)# Inicializa com a quantidade de variáveis que se deseja

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self._ofset_temo = 0

    def thread_atualizar_valor(self):
        while self._running == True:
            # Obtém o valor atualizado do dado (ou qualquer outra lógica necessária)
            # Obtém a data e hora atuais
            data_hora = datetime.now()
            data_formatada = data_hora.strftime("%d/%m/%Y %H:%M:%S")
            # print(valor_atualizado)

            # Emite o sinal para atualizar a interface do usuário
            self.sinal_atualizar.emit(data_formatada)

            # Aguarda 1 segundo antes de atualizar novamente
            QApplication.processEvents()
            time.sleep(0.5)

    def parar(self):
        self._running = False

class ExecutaRotinaThread(QObject):
    sinal_execucao = pyqtSignal(list,list,list,list)# Inicializa com a quantidade de variáveis que se deseja

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True
        self.esquerda_ok =False
        self.direita_ok =False

    def atualizar_execucao(self):
        while self._running == True:
            # Emite o sinal para atualizar a interface do usuário
            result_condu_e = []
            result_condu_d = []
            result_iso_e = []
            result_iso_d = []
            
            if self.operacao.em_execucao == True:
                # Limpa todas as saídas
                self.operacao.rotina.limpa_saidas_esquerda_direita()
                if self.operacao.rotina.abaixa_pistao() == True:
                    if self.operacao.habili_desbilita_esquerdo == True:
                        self.operacao.qual_teste = self.operacao.TESTE_COND_E
                        result_condu_e = self.operacao.rotina.esquerdo_direito_condutividade(0)# Testa O lado esquerdo
                        self.operacao.qual_teste = self.operacao.TESTE_ISO_E
                        result_iso_e = self.operacao.rotina.esquerdo_direito_isolacao(0)# Testa O lado esquerdo

                        # Verifica condutividade
                        cond = all(c[2] != 0 for c in result_condu_e)                    
                        # Verifica isolação
                        iso = all(i[2] != 1 for i in result_iso_e)  
                        # Se teste de condutividade e de isolação passaram
                        if cond == True and iso == True:
                            self.operacao.rotina.marca_peca_esquerda()
                            self.esquerda_ok = True
                        else:
                            self.esquerda_ok = False
                            
                        
                        # if result_condu_e[2] == 1 and result_iso_e[2] == 0: # Se tste de condutividade e de isolação passaram
                        #     self.operacao.io.wp_8027(self.io.ADR_3, 2, 1) # Aciona pistão de marcação esquerdo
                        #     time.sleep(0.5)
                        #     self.operacao.io.wp_8027(self.io.ADR_3, 2, 0) # Desliga pistão de marcação esquerdo


                    if self.operacao.habili_desbilita_direito == True:
                        self.operacao.qual_teste = self.operacao.TESTE_COND_D
                        result_condu_d = self.operacao.rotina.esquerdo_direito_condutividade(1)# Testa O lado direito
                        self.operacao.qual_teste = self.operacao.TESTE_ISO_D
                        result_iso_d = self.operacao.rotina.esquerdo_direito_isolacao(1)# Testa O lado direito

                        # Verifica condutividade
                        cond = all(c[2] != 0 for c in result_condu_d)                    
                        # Verifica isolação
                        iso = all(i[2] != 1 for i in result_iso_d)  
                        # Se teste de condutividade e de isolação passaram
                        if cond == True and iso ==  True:
                            self.operacao.rotina.marca_peca_direita()
                            self.direita_ok = True
                        else:
                            self.direita_ok = False
                        
                        # if result_condu_d[2] == 1 and result_iso_d[2] == 0: # Se tste de condutividade e de isolação passaram
                        #     self.operacao.io.wp_8027(self.io.ADR_3, 3, 1) # Aciona pistão de marcação esquerdo
                        #     time.sleep(0.5)
                        #     self.operacao.io.wp_8027(self.io.ADR_3, 3, 0) # Desliga pistão de marcação esquerdo
                            
                if self.esquerda_ok == True and self.direita_ok == True:
                    self.operacao.rotina.acende_verde()
                    self.operacao.rotina.sobe_pistao()
                else:
                    self.operacao.rotina.acende_vermelho()# Se acender vermelho, continua com pistão em baixo
                
                
                self.operacao.qual_teste = self.operacao.SEM_TESTE
                self.operacao.muda_cor_obj("lbContinuIndicaE",self.operacao.CINZA)
                self.operacao.muda_cor_obj("lbContinuIndicaD",self.operacao.CINZA)
                self.operacao.muda_cor_obj("lbIsolaIndicaE",self.operacao.CINZA)
                self.operacao.muda_cor_obj("lbIsolaIndicaD",self.operacao.CINZA)

                # Emite o evento para conclusão so processo
                self.sinal_execucao.emit(result_condu_e,result_iso_e,result_condu_d,result_iso_d)
            QApplication.processEvents()
            # Aguarda 1 segundo antes de atualizar novamente
            time.sleep(0.5)

    def parar(self):
        self._running = False

class TelaExecucao(QDialog):
    def __init__(self,  dado=None, io=None, db=None, rotina=None, nome_prog = None, continuacao = None, db_rotina = None):
        super().__init__()

        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina
        self.nome_prog = nome_prog
        self.id = 0
        self.continuacao = continuacao
        self.db_rotina = db_rotina

        self.tempo_ciclo = 0

        self._translate = QCoreApplication.translate

        self.habili_desbilita_esquerdo = True
        self.habili_desbilita_direito = True
        self.habili_desbilita_esquerdo_old = True
        self.habili_desbilita_direito_old = True
        self.execucao_habilita_desabilita = False
        self.em_execucao = False
        self._nao_passsou_peca = False

        # Flags para estado de execução
        self.SEM_TESTE = 0
        self.TESTE_COND_E = 1
        self.TESTE_COND_D = 2
        self.TESTE_ISO_E = 3
        self.TESTE_ISO_D = 4

        # Cores para indicações
        # background-color: rgb(170, 255, 127);
        # background-color: rgb(171, 171, 171);
        # background-color: rgb(170, 0, 0);
        self.VERDE = "170, 255, 127"
        self.CINZA = "171, 171, 171"
        self.VERMELHO = "255, 0, 0"
        self.AZUL = "0,255,255"
        self.LILAZ = "192, 82, 206"

        self.qual_teste = self.SEM_TESTE
        self._ofset_temo = 0

        self._cnt_ciclos = 1
        self._cnt_peca_passou_e = 0
        self._cnt_peca_passou_d = 0
        self._cnt_peca_reprovou_e = 0
        self._cnt_peca_reprovou_d = 0
        self._cnt_peca_retrabalho_e = 0
        self._cnt_peca_retrabalho_d = 0

        # Variáveis que armazena estado dos testes
        self.cond_e = []
        self.iso_e = []
        self.cond_d = []
        self.iso_d = []

        #Usado para mostrar cada erro a medida que toca na imagem
        self._cnt_pagina_erro = 0

        self._cnt_acionamento_botao = 0# Para garantir que não se acione o botão mais que uma vez

        self._retrabalho = False
        self.rotina_iniciada = False
        self._nome_rotina_execucao = ""

        self._visualiza_condu_e = False
        self._visualiza_condu_d = False
        self._visualiza_iso_e = False
        self._visualiza_iso_d = False

        self.oscila_cor = False

        self.msg = SimpleMessageBox()
        self.msg_box = MessageBox()

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaExecucao()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

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

        self.load_config()

        # Inicializar o atualizador em uma nova thread
        self.atualizador = Atualizador(self)
        self.atualizador.sinal_atualizar.connect(self.thread_atualizar_valor)
        self.atualizador_thread = QThread()
        self.atualizador.moveToThread(self.atualizador_thread)
        self.atualizador_thread.started.connect(self.atualizador.thread_atualizar_valor)
        self.atualizador_thread.start()

        # Inicia Thread de execução de rotina
        self.execucao = ExecutaRotinaThread(self)
        self.execucao.sinal_execucao.connect(self.thread_execucao)
        self.execucao_thread = QThread()
        self.execucao.moveToThread(self.execucao_thread)
        self.execucao_thread.started.connect(self.execucao.atualizar_execucao)
        self.execucao_thread.start()

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
        self.ui.lbDataHora.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">{data_hora}</p></body></html>"))

        # if self.execucao_habilita_desabilita == True :
        if self.execucao_habilita_desabilita == True and  self.io.io_rpi.bot_acio_e == 0 and self.io.io_rpi.bot_acio_d == 0 and self._nao_passsou_peca == False:
            while(self.io.io_rpi.bot_acio_e == 0 or self.io.io_rpi.bot_acio_d == 0):
                pass
            # self.rotina.sobe_pistao()
            #escrever aqui o desliga verde e vermelho da torre
            self.rotina.apaga_torre()

            if self._cnt_acionamento_botao < 1:
                # time.sleep(0.1)
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
            

        if self.em_execucao == True and self._nao_passsou_peca == False:

            if self.qual_teste == self.SEM_TESTE:
                self.muda_cor_obj("lbContinuIndicaE",self.CINZA)
                self.muda_cor_obj("lbContinuIndicaD",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaE",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaD",self.CINZA)
            elif self.qual_teste == self.TESTE_COND_E:
                self.muda_cor_obj("lbContinuIndicaE",self.VERDE)
                self.muda_cor_obj("lbContinuIndicaD",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaE",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaD",self.CINZA)
            elif self.qual_teste == self.TESTE_COND_D:
                self.muda_cor_obj("lbContinuIndicaE",self.CINZA)
                self.muda_cor_obj("lbContinuIndicaD",self.VERDE)
                self.muda_cor_obj("lbIsolaIndicaE",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaD",self.CINZA)
            elif self.qual_teste == self.TESTE_ISO_E:
                self.muda_cor_obj("lbContinuIndicaE",self.CINZA)
                self.muda_cor_obj("lbContinuIndicaD",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaE",self.VERDE)
                self.muda_cor_obj("lbIsolaIndicaD",self.CINZA)
            elif self.qual_teste == self.TESTE_ISO_D:
                self.muda_cor_obj("lbContinuIndicaE",self.CINZA)
                self.muda_cor_obj("lbContinuIndicaD",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaE",self.CINZA)
                self.muda_cor_obj("lbIsolaIndicaD",self.VERDE)
            
            self.cor_eletrodo_teste()

            self._ofset_temo+=1
            if (self._ofset_temo % 2) == 0:
                self.tempo_ciclo+=1
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
                        self._carrega_eletrodos_esquerdo(self.rotina.coord_eletrodo_esquerdo,self.cond_e[self._cnt_pagina_erro][0], -1)
                        self.muda_cor_obj(f"lbEletrodo{self.cond_e[self._cnt_pagina_erro][0]}_E",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.cond_e[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de condutividade nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")


                if self._visualiza_condu_d == True:
                    if self._cnt_pagina_erro > len(self.cond_d)-1:
                        self._cnt_pagina_erro=0
                    

                    if self.habili_desbilita_direito == True and self.cond_d != []:
                        self._carrega_eletrodos_direito(self.rotina.coord_eletrodo_direito,self.cond_d[self._cnt_pagina_erro][0], -1)
                        self.muda_cor_obj(f"lbEletrodo{self.cond_d[self._cnt_pagina_erro][0]}_D",self.VERMELHO)
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Condutor: {self.cond_d[self._cnt_pagina_erro][1]}</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
                    else:
                        self.ui.lbAvisos.setText(self._translate("TelaExecucao", f"<html><head/><body><p align=\"center\">Não há erros de condutividade nessa peça</p></body></html>"))
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

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
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")


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
                        self.ui.lbAvisos.setStyleSheet(f"background-color: rgb({self.VERMELHO});")

            except:
                print("ultrapassou indice de lista")

            self._ofset_temo=0
        else:
            self._ofset_temo=0

    
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
        if self.em_execucao == True:
            self.cond_e.clear()
            self.cond_d.clear()
            self.iso_e.clear()
            self.iso_d.clear()
            print(f"Condutividade esquerdo: {cond_e}")
            print(f"Isolação esquerdo: {iso_e}")
            print(f"Condutividade direito: {cond_d}")
            print(f"Isolação direito: {iso_d}")
            self.em_execucao = False
            
            # Verifica se peças passaram
            if self.habili_desbilita_direito == True and self.habili_desbilita_esquerdo == True:# Se ambos os lados estiverem habilitados
                if cond_e != [] and iso_e != [] and cond_d != [] and iso_d != 0:
                    if self._verifica_condutividade_isolacao(cond_e, iso_e) == (True,True) and self._verifica_condutividade_isolacao(cond_d, iso_d) == (True,True):
                        self._carrega_peca_passou(0)
                        #escrever aqui o liga verde da torre

                    else:# Verifica qual dos dois não passaram

                        if self._verifica_condutividade_isolacao(cond_e, iso_e) == (True,True):
                            self._carrega_peca_passou(1)# passou a esquerda habilitada
                        else:
                            # passa para as variáveis somente o que não passou 
                            for i in cond_e:
                                if i[2] == 0:
                                    self.cond_e.append(i)
                            for i in iso_e:
                                if i[2] == 1:
                                    self.iso_e.append(i)
                        if self._verifica_condutividade_isolacao(cond_d, iso_d) == (True,True):
                            self._carrega_peca_passou(2)# passou a direita habilitada
                        else:
                            # passa para as variáveis somente o que não passou 
                            for i in cond_d:
                                if i[2] == 0:
                                    self.cond_d.append(i)
                            for i in iso_d:
                                if i[2] == 1:
                                    self.iso_d.append(i)
                        self.pausa_execucao()
                        self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")

                        self._nao_passsou_peca = True

                        #escrever aqui o liga Vermelho da torre

            elif self.habili_desbilita_direito == False and self.habili_desbilita_esquerdo == True:# Se só esquerdo estiver habilitado
                if cond_e != [] and iso_e != []:
                    if self._verifica_condutividade_isolacao(cond_e, iso_e) == (True,True):
                        self._carrega_peca_passou(1)
                        #escrever aqui o liga verde da torre
                    else:
                        # passa para as variáveis somente o que não passou 
                        for i in cond_e:
                            if i[2] == 0:
                                self.cond_e.append(i)
                        for i in iso_e:
                            if i[2] == 1:
                                self.iso_e.append(i)
                        self._nao_passsou_peca = True
                        self.pausa_execucao()
                        self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")
                        #escrever aqui o liga vermelha da torre

            elif self.habili_desbilita_direito == True and self.habili_desbilita_esquerdo == False:# Se só direito estiver habilitado
                if cond_d != [] and iso_d != []:
                    if self._verifica_condutividade_isolacao(cond_d, iso_d) == (True,True):
                        self._carrega_peca_passou(2)
                        #escrever aqui o liga verde da torre
                    else:
                        # passa para as variáveis somente o que não passou
                        for i in cond_d:
                            if i[2] == 0:
                                self.cond_d.append(i)
                        for i in iso_d:
                            if i[2] == 1:
                                self.iso_d.append(i)
                        self._nao_passsou_peca = True
                        self.pausa_execucao()
                        self.msg.exec(msg="Favor apertar iniciar para ter acesso a peça.")
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
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")

    def select_visu_iso_e(self, event):
        if self.habili_desbilita_esquerdo == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = False
            self._visualiza_iso_e = True
            self._visualiza_iso_d = False
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")

    def select_visu_cond_d(self, event):
        if self.habili_desbilita_direito == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = True
            self._visualiza_iso_e = False
            self._visualiza_iso_d = False
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.VERMELHO});")
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")

    def select_visu_iso_d(self, event):
        if self.habili_desbilita_direito == True and self._nao_passsou_peca == True:
            self._visualiza_condu_e = False
            self._visualiza_condu_d = False
            self._visualiza_iso_e = False
            self._visualiza_iso_d = True
            self.ui.lbContinuIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbContinuIndicaD.setStyleSheet(f"background-color: rgb({self.CINZA});")
            self.ui.lbIsolaIndicaE.setStyleSheet(f"background-color: rgb({self.CINZA});")
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
        event.accept()
        self.atualizador.parar()  # Parar a thread do atualizador
        self.atualizador_thread.quit()
        self.atualizador_thread.wait()

        self.execucao.parar()  # Parar a thread do atualizador
        self.execucao_thread.quit()
        self.execucao_thread.wait()
