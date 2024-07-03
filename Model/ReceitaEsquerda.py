from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QCoreApplication

from View.tela_receita_esquerdo import Ui_TelaReceitaEsquerda
from View.tela_receita_esquerdo_dieletrico import Ui_TelaReceitaEsquerdaDieletrico

from Controller.OpenFile import OpenFile
from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

"""1 - Carregue a imagem da peça esquerda
2 - Posicione todos os eletrodos na imagem carregada
3 - Selecione o conector da peça em \"Tomada dos conectores da peça\"
4 - Selecione o eletrodo em \"Escolher eletrodo esquerdo\"
5 - Selecione onde o eletrodo cerresponde em \"Tomada dos eletrodos da peça\""""
class TelaReceitaEsquerda(QDialog):
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
        self.ui = Ui_TelaReceitaEsquerda()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.load_configuracoes()

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btCarregarImgEsque.clicked.connect(self.carregar_img)
        self.ui.btDieletrico.clicked.connect(self.dieletrico)
        self.ui.btSetaEsq.clicked.connect(self.seta_esquerda)
        self.ui.btSetaDir.clicked.connect(self.seta_direita)
        self.ui.btLimparEletrodo.clicked.connect(self.limpar_eletrodo_escolhido)
        self.ui.btAdicionar.clicked.connect(self.adiciona_ligacao)
        self.ui.btTestarConexao.clicked.connect(self.testa_conexao)

        self.ui.rbtConecEsquerdo_1.clicked.connect(self.conector_esquerdo1)
        self.ui.rbtConecEsquerdo_2.clicked.connect(self.conector_esquerdo2)
        self.ui.rbtConecEsquerdo_3.clicked.connect(self.conector_esquerdo3)
        self.ui.rbtConecEsquerdo_4.clicked.connect(self.conector_esquerdo4)
        self.ui.rbtConecEsquerdo_5.clicked.connect(self.conector_esquerdo5)
        self.ui.rbtConecEsquerdo_6.clicked.connect(self.conector_esquerdo6)
        self.ui.rbtConecEsquerdo_7.clicked.connect(self.conector_esquerdo7)
        self.ui.rbtConecEsquerdo_8.clicked.connect(self.conector_esquerdo8)

        self.ui.rbtEletrodoEsquerdo_1.clicked.connect(self.pino_tomada_eletrodo1)
        self.ui.rbtEletrodoEsquerdo_2.clicked.connect(self.pino_tomada_eletrodo2)
        self.ui.rbtEletrodoEsquerdo_3.clicked.connect(self.pino_tomada_eletrodo3)
        self.ui.rbtEletrodoEsquerdo_4.clicked.connect(self.pino_tomada_eletrodo4)
        self.ui.rbtEletrodoEsquerdo_5.clicked.connect(self.pino_tomada_eletrodo5)
        self.ui.rbtEletrodoEsquerdo_6.clicked.connect(self.pino_tomada_eletrodo6)
        self.ui.rbtEletrodoEsquerdo_7.clicked.connect(self.pino_tomada_eletrodo7)
        self.ui.rbtEletrodoEsquerdo_8.clicked.connect(self.pino_tomada_eletrodo8)

        self.ui.rbtEletrodo1_E.clicked.connect(self.eletrodo1_clicado)
        self.ui.rbtEletrodo2_E.clicked.connect(self.eletrodo2_clicado)
        self.ui.rbtEletrodo3_E.clicked.connect(self.eletrodo3_clicado)
        self.ui.rbtEletrodo4_E.clicked.connect(self.eletrodo4_clicado)
        self.ui.rbtEletrodo5_E.clicked.connect(self.eletrodo5_clicado)
        self.ui.rbtEletrodo6_E.clicked.connect(self.eletrodo6_clicado)
        self.ui.rbtEletrodo7_E.clicked.connect(self.eletrodo7_clicado)
        self.ui.rbtEletrodo8_E.clicked.connect(self.eletrodo8_clicado)

        self.ui.lbImgEsquerdo.mousePressEvent = self.img_esquerdo_clicado

        self.ui.txNomeConexao.mousePressEvent = self.nome_conexao_clicado

        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)

        self.mousePressEvent = self.atualiza_info
    
    def atualiza_info(self, event):
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)

   
    def load_configuracoes(self):
        self.limpaeletrodo()
        if self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][3] != "":
            self.muda_num_ligacao(self.num_ligacao)
            self.check_conectores(self.num_ligacao)

        if self.rotina.url_img_esquerdo != "":
            self.load_img(self.rotina.url_img_esquerdo)
            # self.carregar_img()

        for index in range(len(self.rotina.coord_eletrodo_esquerdo)):
            # current_object.move(x_pos - current_object .width() // 2, y_pos - current_object.height() // 2)
            # current_object.setVisible(True)  # Tornar self.lbEletrodo1 visível
            if index == 1 and self.rotina.coord_eletrodo_esquerdo[1]!=None:
                self.ui.lbEletrodo1_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo1_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo1_E.height() // 2)
                self.ui.lbEletrodo1_E.setVisible(True)
            elif index == 2 and self.rotina.coord_eletrodo_esquerdo[2]!=None:
                self.ui.lbEletrodo2_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo2_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo2_E.height() // 2)
                self.ui.lbEletrodo2_E.setVisible(True)
            elif index == 3 and self.rotina.coord_eletrodo_esquerdo[3]!=None:
                self.ui.lbEletrodo3_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo3_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo3_E.height() // 2)
                self.ui.lbEletrodo3_E.setVisible(True)

            elif index == 4 and self.rotina.coord_eletrodo_esquerdo[4]!=None:
                self.ui.lbEletrodo4_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo4_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo4_E.height() // 2)
                self.ui.lbEletrodo4_E.setVisible(True)

            elif index == 5 and self.rotina.coord_eletrodo_esquerdo[5]!=None:
                self.ui.lbEletrodo5_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo5_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo5_E.height() // 2)
                self.ui.lbEletrodo5_E.setVisible(True)

            elif index == 6 and self.rotina.coord_eletrodo_esquerdo[6]!=None:
                self.ui.lbEletrodo6_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo6_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo6_E.height() // 2)
                self.ui.lbEletrodo6_E.setVisible(True)

            elif index == 7 and self.rotina.coord_eletrodo_esquerdo[7]!=None:
                self.ui.lbEletrodo7_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo7_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo7_E.height() // 2)
                self.ui.lbEletrodo7_E.setVisible(True)

            elif index == 8 and self.rotina.coord_eletrodo_esquerdo[8]!=None:
                self.ui.lbEletrodo8_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo8_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo8_E.height() // 2)
                self.ui.lbEletrodo8_E.setVisible(True)


    def limpaeletrodo(self):
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

    def limpar_eletrodo_escolhido(self):
        index = 0
        if self.ui.rbtEletrodo1_E.isChecked() == True:
            self.ui.lbEletrodo1_E.setVisible(False)
            index = 1

        elif self.ui.rbtEletrodo2_E.isChecked() == True:
            self.ui.lbEletrodo2_E.setVisible(False)
            index = 2

        elif self.ui.rbtEletrodo3_E.isChecked() == True:
            self.ui.lbEletrodo3_E.setVisible(False)
            index = 3

        elif self.ui.rbtEletrodo4_E.isChecked() == True:
            self.ui.lbEletrodo4_E.setVisible(False)
            index = 4

        elif self.ui.rbtEletrodo5_E.isChecked() == True:
            self.ui.lbEletrodo5_E.setVisible(False)
            index = 5

        elif self.ui.rbtEletrodo6_E.isChecked() == True:
            self.ui.lbEletrodo6_E.setVisible(False)
            index = 6

        elif self.ui.rbtEletrodo7_E.isChecked() == True:
            self.ui.lbEletrodo7_E.setVisible(False)
            index = 7

        elif self.ui.rbtEletrodo8_E.isChecked() == True:
            self.ui.lbEletrodo8_E.setVisible(False)
            index = 8

        self.limpa_buffer_coordenadas(index)
        print(self.rotina.coord_eletrodo_esquerdo)
    
    def limpa_buffer_coordenadas(self, index):
        self.rotina.coord_eletrodo_esquerdo[index]= None

    def load_img(self, url=""):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        if url == "":
            dir_open.load_image_dialog(None,self.ui.lbImgEsquerdo.width(), self.ui.lbImgEsquerdo.height())
            if dir_open.image != None:
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
                # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
                self.rotina.url_img_esquerdo = dir_open.fileName
        else:
            dir_open.load_image_url(image_path=self.rotina.url_img_esquerdo , size_x=self.ui.lbImgEsquerdo.width() , size_y=self.ui.lbImgEsquerdo.height())
            if dir_open.image != None:
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
                # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
                # self.rotina.url_img_esquerdo = dir_open.fileName
    
    def carregar_img(self):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        # if self.rotina.url_img_esquerdo == "":
        dir_open.load_image_dialog(None,self.ui.lbImgEsquerdo.width(), self.ui.lbImgEsquerdo.height())
        if dir_open.image != None:
            self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
            # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
            self.rotina.url_img_esquerdo = dir_open.fileName
        # else:
        #     dir_open.load_image_url(image_path=self.rotina.url_img_esquerdo , size_x=self.ui.lbImgEsquerdo.width() , size_y=self.ui.lbImgEsquerdo.height())
        #     if dir_open.image != None:
        #         self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
        #         # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
        #         # self.rotina.url_img_esquerdo = dir_open.fileName

    def img_esquerdo_clicado(self, event):
        if self.ui.rbtEletrodo1_E.isChecked() == True:
            self.posiciona_eletrodo(event, 1)
        elif self.ui.rbtEletrodo2_E.isChecked() == True:
            self.posiciona_eletrodo(event, 2)
        elif self.ui.rbtEletrodo3_E.isChecked() == True:
            self.posiciona_eletrodo(event, 3)
        elif self.ui.rbtEletrodo4_E.isChecked() == True:
            self.posiciona_eletrodo(event, 4)
        elif self.ui.rbtEletrodo5_E.isChecked() == True:
            self.posiciona_eletrodo(event, 5)
        elif self.ui.rbtEletrodo6_E.isChecked() == True:
            self.posiciona_eletrodo(event, 6)
        elif self.ui.rbtEletrodo7_E.isChecked() == True:
            self.posiciona_eletrodo(event, 7)
        elif self.ui.rbtEletrodo8_E.isChecked() == True:
            self.posiciona_eletrodo(event, 8)


    def posiciona_eletrodo(self, event, indice):
        # Obter posição do clique dentro de self.lbImgEsquerdo
        x_pos = event.pos().x()
        y_pos = event.pos().y()
        # Construa o nome do objeto dinamicamente com o dígito atual (i)
        object_name = f"lbEletrodo{indice}_E"
        # obj_eletrodo = f"rbtEletrodo{indice}_E"
    
        # Acesse o objeto usando o nome dinâmico dentro do loop
        current_object = getattr(self.ui, object_name)

        current_object.move(x_pos - current_object .width() // 2, y_pos - current_object.height() // 2)
        current_object.setVisible(True)  # Tornar self.lbEletrodo1 visível

        # self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0]=indice
        self.rotina.coord_eletrodo_esquerdo[indice]=[x_pos, y_pos]
        # self.rotina.condutividade_esquerdo[f"ligacao{indice}"][1][1]=x_pos
        # self.rotina.condutividade_esquerdo[f"ligacao{indice}"][1][2]=y_pos
        print(f"Eletrodo: {indice} coordenadas: {self.rotina.coord_eletrodo_esquerdo[indice]}")

    def retorna_eletrodo(self):
        # rbtEletrodo1_E
        if self.ui.rbtEletrodo1_E.isChecked() == True:
            return 1
        elif self.ui.rbtEletrodo2_E.isChecked() == True:
            return 2
        elif self.ui.rbtEletrodo3_E.isChecked() == True:
            return 3
        elif self.ui.rbtEletrodo4_E.isChecked() == True:
            return 4
        elif self.ui.rbtEletrodo5_E.isChecked() == True:
            return 5
        elif self.ui.rbtEletrodo6_E.isChecked() == True:
            return 6
        elif self.ui.rbtEletrodo7_E.isChecked() == True:
            return 7
        elif self.ui.rbtEletrodo8_E.isChecked() == True:
            return 8
        else:
            return 0


    def muda_num_ligacao(self, num):
        _translate = QCoreApplication.translate
        self.ui.lbNumLigacao.setText(_translate("TelaReceitaEsquerda", f"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">{str(num)}</span></p></body></html>"))
        self.ui.txNomeConexao.setText(self.rotina.condutividade_esquerdo[f"ligacao{num}"][3])

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
            obj_tom_conec = f"rbtConecEsquerdo_{self.rotina.condutividade_esquerdo[f'ligacao{num}'][0]}"
            obj_eletrodos = f"rbtEletrodo{self.rotina.condutividade_esquerdo[f'ligacao{num}'][1][0]}_E"
            obj_tom_eletrodos = f"rbtEletrodoEsquerdo_{self.rotina.condutividade_esquerdo[f'ligacao{num}'][2]}"

            cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
            cur_obj_eletrodos = getattr(self.ui, obj_eletrodos)
            cur_obj_tom_eletrodos = getattr(self.ui, obj_tom_eletrodos)
            
            # self.ui.rbtEletrodoEsquerdo_1.setChecked(True)
            cur_obj_tom_conec.setChecked(True)
            cur_obj_eletrodos.setChecked(True)
            cur_obj_tom_eletrodos.setChecked(True)
        except:
            print("Erro de objeto em check_conectores")

    def conector_esquerdo1(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 1 # Atribui pino correspondente
    def conector_esquerdo2(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 2 # Atribui pino correspondente
    def conector_esquerdo3(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 3 # Atribui pino correspondente
    def conector_esquerdo4(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 4 # Atribui pino correspondente
    def conector_esquerdo5(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 5 # Atribui pino correspondente
    def conector_esquerdo6(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 6 # Atribui pino correspondente
    def conector_esquerdo7(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 7 # Atribui pino correspondente
    def conector_esquerdo8(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][0] = 8 # Atribui pino correspondente

    def pino_tomada_eletrodo1(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 1 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo2(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 2 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo3(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 3 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo4(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 4 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo5(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 5 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo6(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 6 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo7(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 7 # Atribui pino da tomada dos eletrodos
    def pino_tomada_eletrodo8(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][2] = 8 # Atribui pino da tomada dos eletrodos

    def eletrodo1_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 1        
    def eletrodo2_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 2
    def eletrodo3_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 3        
    def eletrodo4_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 4        
    def eletrodo5_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 5        
    def eletrodo6_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 6        
    def eletrodo7_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 7        
    def eletrodo8_clicado(self):
        self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][0] = 8        

    def dieletrico(self):
        if self.rotina.url_img_esquerdo != "" and ( self.check_uma_ligacao()==True):
            dieletrico = TelaReceitaEsquerdaDieletrico(dado=self.dado, io=self.io,db=self.database, rotina=self.rotina)
            self.dado.set_telas(self.dado.TELA_RECEITA_ESQUERDA_DIELETRICO)
            dieletrico.exec_()
        else:
            self.ui.txaInformacoes.setText(self.MSG_CONFIG_IMCOMPLETO)
    def check_uma_ligacao(self):
        cnt_ligacao=0
        for index in range(len(self.rotina.condutividade_esquerdo)+1):
            if index >= 8:
                return False
            if self.rotina.condutividade_esquerdo[f"ligacao{index+1}"][3] != "":
                cnt_ligacao +=1
                if cnt_ligacao > 2:
                    return True
                
        return False

    def adiciona_ligacao(self):
        if self.ui.txNomeConexao.text() != "":
            try:
                self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][3] = self.ui.txNomeConexao.text()
                # self.rotina.coord_eletrodo_esquerdo[indice]=[x_pos, y_pos]
                self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][1] = self.rotina.coord_eletrodo_esquerdo[self.retorna_eletrodo()][0]# x
                self.rotina.condutividade_esquerdo[f"ligacao{self.num_ligacao}"][1][2] = self.rotina.coord_eletrodo_esquerdo[self.retorna_eletrodo()][1]# y
                print(f"Caminho da imagem: {self.rotina.url_img_esquerdo}")
                print(f"Ligação 1: {self.rotina.condutividade_esquerdo['ligacao1']}")
                print(f"Ligação 2: {self.rotina.condutividade_esquerdo['ligacao2']}")
                print(f"Ligação 3: {self.rotina.condutividade_esquerdo['ligacao3']}")
                print(f"Ligação 4: {self.rotina.condutividade_esquerdo['ligacao4']}")
                print(f"Ligação 5: {self.rotina.condutividade_esquerdo['ligacao5']}")
                print(f"Ligação 6: {self.rotina.condutividade_esquerdo['ligacao6']}")
                print(f"Ligação 7: {self.rotina.condutividade_esquerdo['ligacao7']}")
                print(f"Ligação 8: {self.rotina.condutividade_esquerdo['ligacao8']}")
                # ms = "Sim" if self.rotina.condutividade_esquerdo["foi_testado"] == True else "Não"
                print(f"Foi testado?: {'Sim' if self.rotina.condutividade_esquerdo['foi_testado'] == True else 'Não'}")
                self.num_ligacao+=1
                if self.num_ligacao > 8:
                    self.num_ligacao = 8
                self.muda_num_ligacao(self.num_ligacao)
            except:
                self.ui.txaInformacoes.setText(self.MSG_CONFIG_IMCOMPLETO)
        else:
            self.ui.txaInformacoes.setText(self.MSG_NOME_LIGACAO_WARNING)

    def testa_conexao(self):
        self.ui.txaInformacoes.setText(self.MSG_INFO_TESTANDO)
        result = self.rotina.teste_esquerdo_direito_condutividade(0)
        check = False
        for i in range(0,len(result)):
            if result[i][2] == 1 and result[i][1] != "":
                check = True
            else:
                check = False
                break
        if check == True:
            self.rotina.condutividade_esquerdo["foi_testado"] = True
            self.ui.txaInformacoes.setText(f"Teste de condutividade do lado esquerdo em conformidade.")
            # time.sleep(2)
            #self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        else:
            self.rotina.condutividade_esquerdo["foi_testado"] = False
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

class TelaReceitaEsquerdaDieletrico(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()
        self.dado=dado
        self.io=io
        self.database=db
        self.rotina = rotina
        self.MSG_INFORMACAO = """1 - Dê um nome para a ligação
        2 - Escolha o par de eletrodos para ser para o teste
        3 - Salve a ligação
        """
        self.MSG_FALTA_NOME = "Favor digitar um nome para a ligação."

        self.cnt_ligacoes = 0

        self.num_ligacao = 1

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaReceitaEsquerdaDieletrico()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.ui.cbxEletrodo1_E.clicked.connect(self.cbx_clicado_1)
        self.ui.cbxEletrodo2_E.clicked.connect(self.cbx_clicado_2)
        self.ui.cbxEletrodo3_E.clicked.connect(self.cbx_clicado_3)
        self.ui.cbxEletrodo4_E.clicked.connect(self.cbx_clicado_4)
        self.ui.cbxEletrodo5_E.clicked.connect(self.cbx_clicado_5)
        self.ui.cbxEletrodo6_E.clicked.connect(self.cbx_clicado_6)
        self.ui.cbxEletrodo7_E.clicked.connect(self.cbx_clicado_7)
        self.ui.cbxEletrodo8_E.clicked.connect(self.cbx_clicado_8)

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

    def muda_num_ligacao(self, num):
        _translate = QCoreApplication.translate
        self.ui.lbNumLigacao.setText(_translate("TelaReceitaEsquerda", f"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">{str(num)}</span></p></body></html>"))
        self.ui.txNomeConexao.setText(self.rotina.isolacao_esquerdo[f"ligacao{num}"][2])

    # Cada vez que clicado a primeira e segunda vez - pela variável self.cnt_ligacoes - a condição fica:
    # rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][0] = n - Pino da tomada de conectores
    # rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][1] = n - Pino da tomada de eletrodos
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
                if self.rotina.condutividade_esquerdo[f"ligacao{i}"][1][0] == eletrodo_clicado: # se for igual ao eletrodo n
                    valor_pino = self.rotina.condutividade_esquerdo[f"ligacao{i}"][0] # associa conector correspondente
                    self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][posi]= valor_pino
                    self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][3]=eletrodo_clicado # Assicia eletrodo
                    break
        else:
            # Procura o pino da 'tomada de eletrodo' da peça correspondente ao eletrodo n
            for i in range(1,9):
                if self.rotina.condutividade_esquerdo[f"ligacao{i}"][1][0] == eletrodo_clicado:
                    valor_pino = self.rotina.condutividade_esquerdo[f"ligacao{i}"][2]
                    self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][posi]= valor_pino
                    self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][4]=eletrodo_clicado # Assicia eletrodo
                    break
        # self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][posi]= valor_pino
        # self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"]
        if self.cnt_ligacoes >= 2:
            self.desabilita_eletrodos()

    def desabilita_eletrodos(self):

        for i in range(1,9):
            obj_tom_conec = f"cbxEletrodo{i}_E"
            cur_obj_tom_conec = getattr(self.ui, obj_tom_conec)
            # if cur_obj_tom_conec.isChecked() == False:
            cur_obj_tom_conec.setEnabled(False)
            # cur_obj_tom_conec.setChecked(False)

    def habilita_todos_eletrodos(self):
        self.ui.cbxEletrodo1_E.setEnabled(True)
        self.ui.cbxEletrodo1_E.setChecked(False)
        self.ui.cbxEletrodo2_E.setEnabled(True)
        self.ui.cbxEletrodo2_E.setChecked(False)
        self.ui.cbxEletrodo3_E.setEnabled(True)
        self.ui.cbxEletrodo3_E.setChecked(False)
        self.ui.cbxEletrodo4_E.setEnabled(True)
        self.ui.cbxEletrodo4_E.setChecked(False)
        self.ui.cbxEletrodo5_E.setEnabled(True)
        self.ui.cbxEletrodo5_E.setChecked(False)
        self.ui.cbxEletrodo6_E.setEnabled(True)
        self.ui.cbxEletrodo6_E.setChecked(False)
        self.ui.cbxEletrodo7_E.setEnabled(True)
        self.ui.cbxEletrodo7_E.setChecked(False)
        self.ui.cbxEletrodo8_E.setEnabled(True)
        self.ui.cbxEletrodo8_E.setChecked(False)

        self.cnt_ligacoes = 0

    def load_configuracoes(self):
        self.limpaeletrodo()
        self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        self.muda_num_ligacao(self.num_ligacao)

        if self.rotina.url_img_esquerdo != "":
            self.carregar_img()

        for index in range(len(self.rotina.coord_eletrodo_esquerdo)):
            if index == 1 and self.rotina.coord_eletrodo_esquerdo[1]!=None:
                self.ui.lbEletrodo1_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo2_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo2_E.height() // 2)
                self.ui.lbEletrodo1_E.setVisible(True)
            elif index == 2 and self.rotina.coord_eletrodo_esquerdo[2]!=None:
                self.ui.lbEletrodo2_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo2_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo2_E.height() // 2)
                self.ui.lbEletrodo2_E.setVisible(True)
            elif index == 3 and self.rotina.coord_eletrodo_esquerdo[3]!=None:
                self.ui.lbEletrodo3_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo3_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo3_E.height() // 2)
                self.ui.lbEletrodo3_E.setVisible(True)

            elif index == 4 and self.rotina.coord_eletrodo_esquerdo[4]!=None:
                self.ui.lbEletrodo4_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo4_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo4_E.height() // 2)
                self.ui.lbEletrodo4_E.setVisible(True)

            elif index == 5 and self.rotina.coord_eletrodo_esquerdo[5]!=None:
                self.ui.lbEletrodo5_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo5_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo5_E.height() // 2)
                self.ui.lbEletrodo5_E.setVisible(True)

            elif index == 6 and self.rotina.coord_eletrodo_esquerdo[6]!=None:
                self.ui.lbEletrodo6_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo6_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo6_E.height() // 2)
                self.ui.lbEletrodo6_E.setVisible(True)

            elif index == 7 and self.rotina.coord_eletrodo_esquerdo[7]!=None:
                self.ui.lbEletrodo7_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo7_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo7_E.height() // 2)
                self.ui.lbEletrodo7_E.setVisible(True)

            elif index == 8 and self.rotina.coord_eletrodo_esquerdo[8]!=None:
                self.ui.lbEletrodo8_E.move( self.rotina.coord_eletrodo_esquerdo[index][0] - self.ui.lbEletrodo8_E.width() // 2,self.rotina.coord_eletrodo_esquerdo[index][1] - self.ui.lbEletrodo8_E.height() // 2)
                self.ui.lbEletrodo8_E.setVisible(True)

    def carregar_img(self):
        dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
        if self.rotina.url_img_esquerdo == "":
            dir_open.load_image_dialog(None,self.ui.lbImgEsquerdo.width(), self.ui.lbImgEsquerdo.height())
            if dir_open.image != None:
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
                # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
                self.rotina.url_img_esquerdo = dir_open.fileName
        else:
            dir_open.load_image_url(image_path=self.rotina.url_img_esquerdo , size_x=self.ui.lbImgEsquerdo.width() , size_y=self.ui.lbImgEsquerdo.height())
            if dir_open.image != None:
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
                # self.url_imagem_esquerda = dir_open.fileName # Carrega url de onde veio a imagem (Pendrive)
                # self.rotina.url_img_esquerdo = dir_open.fileName

    def completa_nome(self, nome):
        self.ui.txNomeConexao.setText(self.MSG_INFORMACAO)
        teclado = AlphanumericKeyboard(dado=self.dado)
        teclado.exec_()
        self.ui.txNomeConexao.setText(teclado.line_edit.text())

    def adicionar_ligacao_eletrodo(self):
        if self.ui.txNomeConexao.text() != "":
            self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][2] = self.ui.txNomeConexao.text()
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
        obj_eletrodo_1 = f"cbxEletrodo{self.rotina.isolacao_esquerdo[f'ligacao{num}'][3]}_E"
        obj_eletrodo_2 = f"cbxEletrodo{self.rotina.isolacao_esquerdo[f'ligacao{num}'][4]}_E"

        cur_obj_obj_eletrodo_1 = getattr(self.ui, obj_eletrodo_1)
        cur_obj_obj_eletrodo_2 = getattr(self.ui, obj_eletrodo_2)
        
        # self.ui.rbtEletrodoEsquerdo_1.setChecked(True)
        cur_obj_obj_eletrodo_1.setChecked(True)
        cur_obj_obj_eletrodo_2.setChecked(True)
        cur_obj_obj_eletrodo_1.setEnabled(False)
        cur_obj_obj_eletrodo_2.setEnabled(True)
        
        for i in range(1,9):
            if i!= self.rotina.isolacao_esquerdo[f'ligacao{num}'][3] and i!= self.rotina.isolacao_esquerdo[f'ligacao{num}'][4]:
                cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_E")
                cur_obj_obj_eletrodo.setChecked(False)
                cur_obj_obj_eletrodo.setEnabled(False)
            else:
                cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_E")
                cur_obj_obj_eletrodo.setEnabled(False)

    def limpar_eletrodos_refazer(self):
        for i in range(1,9):
            cur_obj_obj_eletrodo = getattr(self.ui, f"cbxEletrodo{i}_E")
            cur_obj_obj_eletrodo.setChecked(False)
            cur_obj_obj_eletrodo.setEnabled(True)
        self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][0] = 0
        self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][1] = 0
        self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][2] = ""
        self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][3] = 0
        self.rotina.isolacao_esquerdo[f"ligacao{self.num_ligacao}"][4] = 0
        self.ui.txNomeConexao.setText("")

    # self.isolacao_esquerdo = {
    #         "ligacao1":[0,0,""],

    def testar_isolacao(self):
        result = []
        result = self.rotina.teste_esquerdo_direito_isolacao(0)
        check = False
        for i in range(0,len(result)):
            if result[i][2] == 0 and result[i][1] != "":
                check = True
            else:
                check = False
                break
        if check == True:
            self.rotina.isolacao_esquerdo["foi_testado"] = True
            self.ui.txaInformacoes.setText(f"Teste de isolação do lado esquerdo em conformidade.")
            # time.sleep(2)
            #self.ui.txaInformacoes.setText(self.MSG_INFORMACAO)
        else:
            self.rotina.isolacao_esquerdo["foi_testado"] = False
            text = ""
            for i in range(len(result)):
                if result[i][2] == 1:
                    text += f"Ligação: {result[i][1]}\n"
            if text != "":
                self.ui.txaInformacoes.setText(f"Erro nas seguintes ligações:\n{text}")
            else:
                self.ui.txaInformacoes.setText(f"Não há ligações...")

    def voltar(self):
        self.dado.set_telas(self.dado.TELA_RECEITA_ESQUERDA)
        self.close()

    def closeEvent(self, event) -> None:
        event.accept()