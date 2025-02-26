from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QCoreApplication

from View.tela_receita_direito import Ui_TelaReceitaDireita
from View.tela_receita_direito_dieletrico import Ui_TelaReceitaDireitaDieletrico

from Controller.OpenFile import OpenFile
from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

class TelaReceitaDireita(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()

        self.MSG_INFORMACAO = """1 - Carregue a imagem da peça esquerda
        2 - Posicione todos os eletrodos na imagem carregada
        3 - Dê um nome à conexão em "Ligações entre eletrodos e conectores"
        4 - Selecione o conector da peça em "Tomada dos conectores da peça"
        5 - Selecione o eletrodo em "Escolher eletrodo esquerdo"
        6 - Selecione onde o eletrodo cerresponde em "Tomada dos eletrodos da peça"
        7 - Clique em adicionar para dieletrico a ligação
        """
        self.MSG_NOME_LIGACAO_WARNING = "Favor preencher nome de ligação."
        self.MSG_CONFIG_IMCOMPLETO = "Favor completar pelo menos duas Ligações."
        self.MSG_INFO_TESTANDO = "Testando...\nAguarde..."

        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina

        self.num_ligacao = 1

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaReceitaDireita()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.load_configuracoes()

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btCarregarImgDir.clicked.connect(self.carregar_img)
        self.ui.btDieletrico.clicked.connect(self.dieletrico)
        self.ui.btSetaEsq.clicked.connect(self.seta_esquerda)
        self.ui.btSetaDir.clicked.connect(self.seta_direita)
        self.ui.btLimparEletrodo.clicked.connect(self.limpar_eletrodo_escolhido)
        self.ui.btAdicionar.clicked.connect(self.adiciona_ligacao)
        self.ui.btTestarConexao.clicked.connect(self.testa_conexao)

        self.ui.rbtConecDireito_1.clicked.connect(self.conector_direito1)
        self.ui.rbtConecDireito_2.clicked.connect(self.conector_direito2)
        self.ui.rbtConecDireito_3.clicked.connect(self.conector_direito3)
        self.ui.rbtConecDireito_4.clicked.connect(self.conector_direito4)
        self.ui.rbtConecDireito_5.clicked.connect(self.conector_direito5)
        self.ui.rbtConecDireito_6.clicked.connect(self.conector_direito6)
        self.ui.rbtConecDireito_7.clicked.connect(self.conector_direito7)
        self.ui.rbtConecDireito_8.clicked.connect(self.conector_direito8)

        self.ui.rbtEletrodoDireito_1.clicked.connect(self.pino_tomada_eletrodo1)
        self.ui.rbtEletrodoDireito_2.clicked.connect(self.pino_tomada_eletrodo2)
        self.ui.rbtEletrodoDireito_3.clicked.connect(self.pino_tomada_eletrodo3)
        self.ui.rbtEletrodoDireito_4.clicked.connect(self.pino_tomada_eletrodo4)
        self.ui.rbtEletrodoDireito_5.clicked.connect(self.pino_tomada_eletrodo5)
        self.ui.rbtEletrodoDireito_6.clicked.connect(self.pino_tomada_eletrodo6)
        self.ui.rbtEletrodoDireito_7.clicked.connect(self.pino_tomada_eletrodo7)
        self.ui.rbtEletrodoDireito_8.clicked.connect(self.pino_tomada_eletrodo8)

        self.ui.rbtEletrodo1_D.clicked.connect(self.eletrodo1_clicado)
        self.ui.rbtEletrodo2_D.clicked.connect(self.eletrodo2_clicado)
        self.ui.rbtEletrodo3_D.clicked.connect(self.eletrodo3_clicado)
        self.ui.rbtEletrodo4_D.clicked.connect(self.eletrodo4_clicado)
        self.ui.rbtEletrodo5_D.clicked.connect(self.eletrodo5_clicado)
        self.ui.rbtEletrodo6_D.clicked.connect(self.eletrodo6_clicado)
        self.ui.rbtEletrodo7_D.clicked.connect(self.eletrodo7_clicado)
        self.ui.rbtEletrodo8_D.clicked.connect(self.eletrodo8_clicado)

        self.ui.lbImgDireito.mousePressEvent = self.img_direito_clicado

        self.ui.txNomeConexao.mousePressEvent = self.nome_conexao_clicado

        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)

        self.mousePressEvent = self.atualiza_info

    def atualiza_info(self, event):
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)

    def load_configuracoes(self):
        self.limpaeletrodo()
        if self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][3] != "":
            self.muda_num_ligacao(self.num_ligacao)
            self.check_conectores(self.num_ligacao)

        if self.rotina.url_img_direito != "":
            self.load_img(self.rotina.url_img_direito)
            # self.carregar_img()

        for index in range(len(self.rotina.coord_eletrodo_direito)):
            # current_object.move(x_pos - current_object .width() // 2, y_pos - current_object.height() // 2)
            # current_object.setVisible(True)  # Tornar self.lbEletrodo1 visível
            if index == 1 and self.rotina.coord_eletrodo_direito[1]!=None:
                self.ui.lbEletrodo1_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo1_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo1_D.height() // 2)
                self.ui.lbEletrodo1_D.setVisible(True)
            elif index == 2 and self.rotina.coord_eletrodo_direito[2]!=None:
                self.ui.lbEletrodo2_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo2_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo2_D.height() // 2)
                self.ui.lbEletrodo2_D.setVisible(True)
            elif index == 3 and self.rotina.coord_eletrodo_direito[3]!=None:
                self.ui.lbEletrodo3_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo3_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo3_D.height() // 2)
                self.ui.lbEletrodo3_D.setVisible(True)

            elif index == 4 and self.rotina.coord_eletrodo_direito[4]!=None:
                self.ui.lbEletrodo4_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo4_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo4_D.height() // 2)
                self.ui.lbEletrodo4_D.setVisible(True)

            elif index == 5 and self.rotina.coord_eletrodo_direito[5]!=None:
                self.ui.lbEletrodo5_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo5_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo5_D.height() // 2)
                self.ui.lbEletrodo5_D.setVisible(True)

            elif index == 6 and self.rotina.coord_eletrodo_direito[6]!=None:
                self.ui.lbEletrodo6_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo6_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo6_D.height() // 2)
                self.ui.lbEletrodo6_D.setVisible(True)

            elif index == 7 and self.rotina.coord_eletrodo_direito[7]!=None:
                self.ui.lbEletrodo7_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo7_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo7_D.height() // 2)
                self.ui.lbEletrodo7_D.setVisible(True)

            elif index == 8 and self.rotina.coord_eletrodo_direito[8]!=None:
                self.ui.lbEletrodo8_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo8_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo8_D.height() // 2)
                self.ui.lbEletrodo8_D.setVisible(True)

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

    def limpar_eletrodo_escolhido(self):
        index = 0
        if self.ui.rbtEletrodo1_D.isChecked() == True:
            self.ui.lbEletrodo1_D.setVisible(False)
            index = 1

        elif self.ui.rbtEletrodo2_D.isChecked() == True:
            self.ui.lbEletrodo2_D.setVisible(False)
            index = 2

        elif self.ui.rbtEletrodo3_D.isChecked() == True:
            self.ui.lbEletrodo3_D.setVisible(False)
            index = 3

        elif self.ui.rbtEletrodo4_D.isChecked() == True:
            self.ui.lbEletrodo4_D.setVisible(False)
            index = 4

        elif self.ui.rbtEletrodo5_D.isChecked() == True:
            self.ui.lbEletrodo5_D.setVisible(False)
            index = 5

        elif self.ui.rbtEletrodo6_D.isChecked() == True:
            self.ui.lbEletrodo6_D.setVisible(False)
            index = 6

        elif self.ui.rbtEletrodo7_D.isChecked() == True:
            self.ui.lbEletrodo7_D.setVisible(False)
            index = 7

        elif self.ui.rbtEletrodo8_D.isChecked() == True:
            self.ui.lbEletrodo8_D.setVisible(False)
            index = 8

        self.limpa_buffer_coordenadas(index)
        print(self.rotina.coord_eletrodo_direito)

    def limpa_buffer_coordenadas(self, index):
        self.rotina.coord_eletrodo_direito[index]= None

    def load_img(self, url=""):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        if url == "":
            dir_open.load_image_dialog(None,self.ui.lbImgDireito.width(), self.ui.lbImgDireito.height())
            if dir_open.image != None:
                self.ui.lbImgDireito.setPixmap(dir_open.image)
                # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
                self.rotina.url_img_direito = dir_open.fileName
        else:
            dir_open.load_image_url(image_path=self.rotina.url_img_direito , size_x=self.ui.lbImgDireito.width() , size_y=self.ui.lbImgDireito.height())
            if dir_open.image != None:
                self.ui.lbImgDireito.setPixmap(dir_open.image)
    
    def carregar_img(self):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        # if self.rotina.url_img_direito == "":
        dir_open.load_image_dialog(None,self.ui.lbImgDireito.width(), self.ui.lbImgDireito.height())
        if dir_open.image != None:
            self.ui.lbImgDireito.setPixmap(dir_open.image)
            # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
            self.rotina.url_img_direito = dir_open.fileName

    def img_direito_clicado(self, event):
        if self.ui.rbtEletrodo1_D.isChecked() == True:
            self.posiciona_eletrodo(event, 1)
        elif self.ui.rbtEletrodo2_D.isChecked() == True:
            self.posiciona_eletrodo(event, 2)
        elif self.ui.rbtEletrodo3_D.isChecked() == True:
            self.posiciona_eletrodo(event, 3)
        elif self.ui.rbtEletrodo4_D.isChecked() == True:
            self.posiciona_eletrodo(event, 4)
        elif self.ui.rbtEletrodo5_D.isChecked() == True:
            self.posiciona_eletrodo(event, 5)
        elif self.ui.rbtEletrodo6_D.isChecked() == True:
            self.posiciona_eletrodo(event, 6)
        elif self.ui.rbtEletrodo7_D.isChecked() == True:
            self.posiciona_eletrodo(event, 7)
        elif self.ui.rbtEletrodo8_D.isChecked() == True:
            self.posiciona_eletrodo(event, 8)

    def posiciona_eletrodo(self, event, indice):
        # Obter posição do clique dentro de self.lbImgDireito
        x_pos = event.pos().x()
        y_pos = event.pos().y()
        # Construa o nome do objeto dinamicamente com o dígito atual (i)
        object_name = f"lbEletrodo{indice}_D"
    
        # Acesse o objeto usando o nome dinâmico dentro do loop
        current_object = getattr(self.ui, object_name)

        current_object.move(x_pos - current_object .width() // 2, y_pos - current_object.height() // 2)
        current_object.setVisible(True)  # Tornar self.lbEletrodo1 visível

        # self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0]=indice
        self.rotina.coord_eletrodo_direito[indice]=[x_pos, y_pos]
        print(f"Eletrodo: {indice} coordenadas: {self.rotina.coord_eletrodo_direito[indice]}")

    def retorna_eletrodo(self):
        # rbtEletrodo1_D
        if self.ui.rbtEletrodo1_D.isChecked() == True:
            return 1
        elif self.ui.rbtEletrodo2_D.isChecked() == True:
            return 2
        elif self.ui.rbtEletrodo3_D.isChecked() == True:
            return 3
        elif self.ui.rbtEletrodo4_D.isChecked() == True:
            return 4
        elif self.ui.rbtEletrodo5_D.isChecked() == True:
            return 5
        elif self.ui.rbtEletrodo6_D.isChecked() == True:
            return 6
        elif self.ui.rbtEletrodo7_D.isChecked() == True:
            return 7
        elif self.ui.rbtEletrodo8_D.isChecked() == True:
            return 8
        else:
            return 0
        
    def muda_num_ligacao(self, num):
        _translate = QCoreApplication.translate
        self.ui.lbNumLigacao.setText(_translate("TelaReceitaEsquerda", f"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">{str(num)}</span></p></body></html>"))
        self.ui.txNomeConexao.setText(self.rotina.condutividade_direito[f"ligacao{num}"][3])

    def seta_esquerda(self):
        self.num_ligacao-=1
        if self.num_ligacao <1:
            self.num_ligacao=1
        self.muda_num_ligacao(self.num_ligacao)
        if self.ui.txNomeConexao.text() != "":
            self.check_conectores(self.num_ligacao)
        
    def seta_direita(self):
        self.num_ligacao+=1
        if self.num_ligacao >8:
            self.num_ligacao=1
        self.muda_num_ligacao(self.num_ligacao)
        if self.ui.txNomeConexao.text() != "":
            self.check_conectores(self.num_ligacao)

    def check_conectores(self, num):
        try:
            obj_tom_conec = f"rbtConecDireito_{self.rotina.condutividade_direito[f'ligacao{num}'][0]}"
            obj_eletrodos = f"rbtEletrodo{self.rotina.condutividade_direito[f'ligacao{num}'][1][0]}_D"
            obj_tom_eletrodos = f"rbtEletrodoDireito_{self.rotina.condutividade_direito[f'ligacao{num}'][2]}"

            cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
            cur_obj_eletrodos = getattr(self.ui, obj_eletrodos)
            cur_obj_tom_eletrodos = getattr(self.ui, obj_tom_eletrodos)
            
            cur_obj_tom_conec.setChecked(True)
            cur_obj_eletrodos.setChecked(True)
            cur_obj_tom_eletrodos.setChecked(True)
        except:
            print("Erro de objeto em check_conectores")

    def conector_direito1(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 1 # Atribui pino correspondente
    def conector_direito2(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 2 # Atribui pino correspondente
    def conector_direito3(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 3 # Atribui pino correspondente
    def conector_direito4(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 4 # Atribui pino correspondente
    def conector_direito5(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 5 # Atribui pino correspondente
    def conector_direito6(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 6 # Atribui pino correspondente
    def conector_direito7(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 7 # Atribui pino correspondente
    def conector_direito8(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][0] = 8 # Atribui pino correspondente

    def pino_tomada_eletrodo1(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 1 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo2(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 2 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo3(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 3 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo4(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 4 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo5(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 5 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo6(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 6 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo7(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 7 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo8(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][2] = 8 # Atribui pino da tomada dos eletrodos

    def eletrodo1_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 1        
    def eletrodo2_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 2
    def eletrodo3_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 3        
    def eletrodo4_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 4        
    def eletrodo5_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 5        
    def eletrodo6_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 6        
    def eletrodo7_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 7        
    def eletrodo8_clicado(self):
        self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][0] = 8   

    def dieletrico(self):
        if self.rotina.url_img_direito != "" and ( self.check_uma_ligacao()==True):
            dieletrico = TelaReceitaDireitaDieletrico(dado=self.dado, io=self.io,db=self.database, rotina=self.rotina)
            self.dado.set_telas(self.dado.TELA_RECEITA_DIREITA_DIELETRICO)
            dieletrico.exec_()
        else:
            self.ui.txaInformacoes.setText(self.MSG_CONFIG_IMCOMPLETO)
    def check_uma_ligacao(self):
        cnt_ligacao=0
        for index in range(len(self.rotina.condutividade_direito)+1):
            if index >= 8:
                return False
            if self.rotina.condutividade_direito[f"ligacao{index+1}"][3] != "":
                cnt_ligacao +=1
                if cnt_ligacao > 2:
                    return True
                
        return False
    
    def adiciona_ligacao(self):
        if self.ui.txNomeConexao.text() != "":
            try:
                self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][3] = self.ui.txNomeConexao.text()
                # self.rotina.coord_eletrodo_direito[indice]=[x_pos, y_pos]
                self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][1] = self.rotina.coord_eletrodo_direito[self.retorna_eletrodo()][0]# x
                self.rotina.condutividade_direito[f"ligacao{self.num_ligacao}"][1][2] = self.rotina.coord_eletrodo_direito[self.retorna_eletrodo()][1]# y
                print(f"Caminho da imagem: {self.rotina.url_img_direito}")
                print(f"Ligação 1: {self.rotina.condutividade_direito['ligacao1']}")
                print(f"Ligação 2: {self.rotina.condutividade_direito['ligacao2']}")
                print(f"Ligação 3: {self.rotina.condutividade_direito['ligacao3']}")
                print(f"Ligação 4: {self.rotina.condutividade_direito['ligacao4']}")
                print(f"Ligação 5: {self.rotina.condutividade_direito['ligacao5']}")
                print(f"Ligação 6: {self.rotina.condutividade_direito['ligacao6']}")
                print(f"Ligação 7: {self.rotina.condutividade_direito['ligacao7']}")
                print(f"Ligação 8: {self.rotina.condutividade_direito['ligacao8']}")
                # ms = "Sim" if self.rotina.condutividade_direito["foi_testado"] == True else "Não"
                print(f"Foi testado?: {'Sim' if self.rotina.condutividade_direito['foi_testado'] == True else 'Não'}")
                self.num_ligacao+=1
                if self.num_ligacao > 8:
                    self.num_ligacao = 8
                self.muda_num_ligacao(self.num_ligacao)
            except:
                self.ui.txaInformacoes.setText(self.MSG_CONFIG_IMCOMPLETO)
        else:
            self.ui.txaInformacoes.setText(self.MSG_NOME_LIGACAO_WARNING)

# Parei aqui e falta implementear em self.rotina.teste_esquerdo_direito_condutividade(1) a parte direita do teste
# 
#*****************************************************************************************************************************
    def testa_conexao(self):
        self.ui.txaInformacoes.setText(self.MSG_INFO_TESTANDO)
        result = self.rotina.teste_esquerdo_direito_condutividade(1)# 1 indica teste do lado direito
        check = False
        for i in range(0,len(result)):
            if result[i][2] == 1 and result[i][1] != "":
                check = True
            else:
                check = False
                break
        if check == True:
            self.rotina.condutividade_direito["foi_testado"] = True
            self.ui.txaInformacoes.setText(f"Teste de condutividade do lado direito em conformidade.")
            # time.sleep(2)
            #self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        else:
            self.rotina.condutividade_direito["foi_testado"] = False
            text = ""
            for i in range(len(result)):
                if result[i][2] == 0:
                    text += f"Ligação: {result[i][1]}\n"
            if text != "":
                self.ui.txaInformacoes.setText(f"Erro nas seguintes ligações:\n{text}")
            else:
                self.ui.txaInformacoes.setText(f"Não há ligações...")

    def nome_conexao_clicado(self, event):
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        alpha = AlphanumericKeyboard(dado=self.dado)
        alpha.exec_()
        self.ui.txNomeConexao.setText(alpha.line_edit.text())

    def voltar(self):
        self.dado.set_telas(self.dado.TELA_CRIAR_RECEITA)
        self.close()
    def closeEvent(self, event):
        event.accept()

class TelaReceitaDireitaDieletrico(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()
        self.dado=dado
        self.io=io
        self.database=db
        self.rotina = rotina
        self.MSG_INFORMACAO = """1 - Dê um nome para a ligação
        2 - Escolha o par de eletrodos para o teste
        3 - Salve a ligação
        """
        self.MSG_FALTA_NOME = "Favor digitar um nome para a ligação."

        self.cnt_ligacoes = 0

        self.num_ligacao = 1

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaReceitaDireitaDieletrico()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.cbxEletrodo1_D.clicked.connect(self.cbx_clicado_1)
        self.ui.cbxEletrodo2_D.clicked.connect(self.cbx_clicado_2)
        self.ui.cbxEletrodo3_D.clicked.connect(self.cbx_clicado_3)
        self.ui.cbxEletrodo4_D.clicked.connect(self.cbx_clicado_4)
        self.ui.cbxEletrodo5_D.clicked.connect(self.cbx_clicado_5)
        self.ui.cbxEletrodo6_D.clicked.connect(self.cbx_clicado_6)
        self.ui.cbxEletrodo7_D.clicked.connect(self.cbx_clicado_7)
        self.ui.cbxEletrodo8_D.clicked.connect(self.cbx_clicado_8)

        self.ui.btAdicionar.clicked.connect(self.adicionar_ligacao_eletrodo)
        self.ui.btSetaDir.clicked.connect(self.seta_direita)
        self.ui.btSetaEsq.clicked.connect(self.seta_esquerda)
        self.ui.btLimparEletrodos.clicked.connect(self.limpar_eletrodos_refazer)
        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btTestar.clicked.connect(self.testar_isolacao)

        self.ui.txNomeConexao.mousePressEvent = self.completa_nome

        self.load_configuracoes()

        self.mousePressEvent = self.atualiza_info

    def atualiza_info(self, event):
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)

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

    def muda_num_ligacao(self, num):
        _translate = QCoreApplication.translate
        self.ui.lbNumLigacao.setText(_translate("TelaReceitaDireita", f"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">{str(num)}</span></p></body></html>"))
        self.ui.txNomeConexao.setText(self.rotina.isolacao_direito[f"ligacao{num}"][2])

    # Cada vez que clicado a primeira e segunda vez - pela variável self.cnt_ligacoes - a condição fica:
    # rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][0] = n - Pino da tomada de conectores
    # rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][1] = n - Pino da tomada de eletrodos
    def cbx_clicado_1(self):
        self.carre_eletrodo_clicado(1)
    def cbx_clicado_2(self):
        self.carre_eletrodo_clicado(2)
    def cbx_clicado_3(self):
        self.carre_eletrodo_clicado(3)
    def cbx_clicado_4(self):
        self.carre_eletrodo_clicado(4)
    def cbx_clicado_5(self):
        self.carre_eletrodo_clicado(5)
    def cbx_clicado_6(self):
        self.carre_eletrodo_clicado(6)
    def cbx_clicado_7(self):
        self.carre_eletrodo_clicado(7)
    def cbx_clicado_8(self):
        self.carre_eletrodo_clicado(8)

    def carre_eletrodo_clicado(self, eletrodo):
        self.cnt_ligacoes+=1
        posi = 0 if self.cnt_ligacoes == 1 else 1
        valor_pino = 0
        eletrodo_clicado = eletrodo
        if posi == 0:
            # Procura o pino da 'tomada de conector' da peça correspondente ao eletrodo n
            for i in range(1,9):
                if self.rotina.condutividade_direito[f"ligacao{i}"][1][0] == eletrodo_clicado: # se for igual ao eletrodo n
                    valor_pino = self.rotina.condutividade_direito[f"ligacao{i}"][0] # associa conector correspondente
                    self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][posi]= valor_pino
                    self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][3]=eletrodo_clicado
                    break
        else:
            # Procura o pino da 'tomada de eletrodo' da peça correspondente ao eletrodo n
            for i in range(1,9):
                if self.rotina.condutividade_direito[f"ligacao{i}"][1][0] == eletrodo_clicado:
                    valor_pino = self.rotina.condutividade_direito[f"ligacao{i}"][2]
                    self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][posi]= valor_pino
                    self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][4]=eletrodo_clicado
                    break
        # self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][posi]= valor_pino  
        if self.cnt_ligacoes >= 2:
            self.desabilita_eletrodos()

    def desabilita_eletrodos(self):

        for i in range(1,9):
            obj_tom_conec = f"cbxEletrodo{i}_D"
            cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
            # if cur_obj_tom_conec.isChecked() == False:
            cur_obj_tom_conec.setEnabled(False)
            # cur_obj_tom_conec.setChecked(False)

    def habilita_todos_eletrodos(self):
        self.ui.cbxEletrodo1_D.setEnabled(True)
        self.ui.cbxEletrodo1_D.setChecked(False)
        self.ui.cbxEletrodo2_D.setEnabled(True)
        self.ui.cbxEletrodo2_D.setChecked(False)
        self.ui.cbxEletrodo3_D.setEnabled(True)
        self.ui.cbxEletrodo3_D.setChecked(False)
        self.ui.cbxEletrodo4_D.setEnabled(True)
        self.ui.cbxEletrodo4_D.setChecked(False)
        self.ui.cbxEletrodo5_D.setEnabled(True)
        self.ui.cbxEletrodo5_D.setChecked(False)
        self.ui.cbxEletrodo6_D.setEnabled(True)
        self.ui.cbxEletrodo6_D.setChecked(False)
        self.ui.cbxEletrodo7_D.setEnabled(True)
        self.ui.cbxEletrodo7_D.setChecked(False)
        self.ui.cbxEletrodo8_D.setEnabled(True)
        self.ui.cbxEletrodo8_D.setChecked(False)

        self.cnt_ligacoes = 0

    def load_configuracoes(self):
        self.limpaeletrodo()
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        self.muda_num_ligacao(self.num_ligacao)

        if self.rotina.url_img_direito != "":
            self.carregar_img()

        for index in range(len(self.rotina.coord_eletrodo_direito)):
            # current_object.move(x_pos - current_object .width() // 2, y_pos - current_object.height() // 2)
            # current_object.setVisible(True)  # Tornar self.lbEletrodo1 visível
            if index == 1 and self.rotina.coord_eletrodo_direito[1]!=None:
                self.ui.lbEletrodo1_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo2_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo2_D.height() // 2)
                self.ui.lbEletrodo1_D.setVisible(True)

            elif index == 2 and self.rotina.coord_eletrodo_direito[2]!=None:
                self.ui.lbEletrodo2_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo2_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo2_D.height() // 2)
                self.ui.lbEletrodo2_D.setVisible(True)

            elif index == 3 and self.rotina.coord_eletrodo_direito[3]!=None:
                self.ui.lbEletrodo3_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo3_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo3_D.height() // 2)
                self.ui.lbEletrodo3_D.setVisible(True)

            elif index == 4 and self.rotina.coord_eletrodo_direito[4]!=None:
                self.ui.lbEletrodo4_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo4_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo4_D.height() // 2)
                self.ui.lbEletrodo4_D.setVisible(True)

            elif index == 5 and self.rotina.coord_eletrodo_direito[5]!=None:
                self.ui.lbEletrodo5_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo5_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo5_D.height() // 2)
                self.ui.lbEletrodo5_D.setVisible(True)

            elif index == 6 and self.rotina.coord_eletrodo_direito[6]!=None:
                self.ui.lbEletrodo6_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo6_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo6_D.height() // 2)
                self.ui.lbEletrodo6_D.setVisible(True)

            elif index == 7 and self.rotina.coord_eletrodo_direito[7]!=None:
                self.ui.lbEletrodo7_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo7_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo7_D.height() // 2)
                self.ui.lbEletrodo7_D.setVisible(True)

            elif index == 8 and self.rotina.coord_eletrodo_direito[8]!=None:
                self.ui.lbEletrodo8_D.move( self.rotina.coord_eletrodo_direito[index][0] - self.ui.lbEletrodo8_D.width() // 2,self.rotina.coord_eletrodo_direito[index][1] - self.ui.lbEletrodo8_D.height() // 2)
                self.ui.lbEletrodo8_D.setVisible(True)

    def carregar_img(self):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        if self.rotina.url_img_direito == "":
            dir_open.load_image_dialog(None,self.ui.lbImgDireito.width(), self.ui.lbImgDireito.height())
            if dir_open.image != None:
                self.ui.lbImgDireito.setPixmap(dir_open.image)
                self.rotina.url_img_direito = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
        else:
            dir_open.load_image_url(image_path=self.rotina.url_img_direito , size_x=self.ui.lbImgDireito.width() , size_y=self.ui.lbImgDireito.height())
            if dir_open.image != None:
                self.ui.lbImgDireito.setPixmap(dir_open.image)

    def completa_nome(self, nome):
        self.ui.txNomeConexao.setText(self.MSG_INFORMACAO)
        teclado = AlphanumericKeyboard(dado=self.dado)
        teclado.exec_()
        self.ui.txNomeConexao.setText(teclado.line_edit.text())

    def adicionar_ligacao_eletrodo(self):
        if self.ui.txNomeConexao.text() != "":
            self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][2] = self.ui.txNomeConexao.text()
            self.num_ligacao+=1
            if self.cnt_ligacoes >16:
                self.num_ligacao=1
            self.muda_num_ligacao(self.num_ligacao)
            self.habilita_todos_eletrodos()
        else:
            self.ui.txNomeConexao.setText(self.MSG_FALTA_NOME)

    def seta_esquerda(self):
        self.num_ligacao-=1
        if self.num_ligacao <1:
            self.num_ligacao=1
        self.muda_num_ligacao(self.num_ligacao)
        if self.ui.txNomeConexao.text() != "":
            self.check_combinacao_eletrodos(self.num_ligacao)
        else:
            self.habilita_todos_eletrodos()
        
    def seta_direita(self):
        self.num_ligacao+=1
        if self.num_ligacao >16:
            self.num_ligacao=1
        self.muda_num_ligacao(self.num_ligacao)
        if self.ui.txNomeConexao.text() != "":
            self.check_combinacao_eletrodos(self.num_ligacao)
        else:
            self.habilita_todos_eletrodos()

    def check_combinacao_eletrodos(self,num):
        obj_eletrodo_1 = f"cbxEletrodo{self.rotina.isolacao_direito[f'ligacao{num}'][3]}_D"
        obj_eletrodo_2 = f"cbxEletrodo{self.rotina.isolacao_direito[f'ligacao{num}'][4]}_D"

        cur_obj_obj_eletrodo_1 = getattr(self.ui, obj_eletrodo_1)
        cur_obj_obj_eletrodo_2 = getattr(self.ui, obj_eletrodo_2)
        
        # self.ui.rbtEletrodoEsquerdo_1.setChecked(True)
        cur_obj_obj_eletrodo_1.setChecked(True)
        cur_obj_obj_eletrodo_2.setChecked(True)
        cur_obj_obj_eletrodo_1.setEnabled(False)
        cur_obj_obj_eletrodo_2.setEnabled(True)
        
        for i in range(1,9):
            if i!= self.rotina.isolacao_direito[f'ligacao{num}'][3] and i!= self.rotina.isolacao_direito[f'ligacao{num}'][4]:
                cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_D")
                cur_obj_obj_eletrodo.setChecked(False)
                cur_obj_obj_eletrodo.setEnabled(False)
            else:
                cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_D")
                cur_obj_obj_eletrodo.setEnabled(False)

    def limpar_eletrodos_refazer(self):
        for i in range(1,9):
            cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_D")
            cur_obj_obj_eletrodo.setChecked(False)
            cur_obj_obj_eletrodo.setEnabled(True)
        self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][0] = 0
        self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][1] = 0
        self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][2] = ""
        self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][3] = 0
        self.rotina.isolacao_direito[f"ligacao{self.num_ligacao}"][4] = 0
        self.ui.txNomeConexao.setText("")

    def testar_isolacao(self):
        result = []
        result = self.rotina.teste_esquerdo_direito_isolacao(1)# 1 é o lado direito
        check = False
        for i in range(0,len(result)):
            if result[i][2] == 0 and result[i][1] != "":
                check = True
            else:
                check = False
                break
        if check == True:
            self.rotina.isolacao_direito["foi_testado"] = True
            self.ui.txaInformacoes.setText(f"Teste de isolação do lado direito em conformidade.")
            # time.sleep(2)
            #self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        else:
            self.rotina.isolacao_direito["foi_testado"] = False
            text = ""
            for i in range(len(result)):
                if result[i][2] == 1:
                    text += f"Ligação: {result[i][1]}\n"
            if text != "":
                self.ui.txaInformacoes.setText(f"Erro nas seguintes ligações:\n{text}")
            else:
                self.ui.txaInformacoes.setText(f"Não há ligações...")

    def voltar(self):
        self.dado.set_telas(self.dado.TELA_RECEITA_DIREITA)
        self.close()

    def closeEvent(self, event) -> None:
        event.accept()