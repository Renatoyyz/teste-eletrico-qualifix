import os
import shutil

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

from Controller.OpenFile import OpenFile
from Model.ReceitaEsquerda import TelaReceitaEsquerda
from Model.ReceitaDireita import TelaReceitaDireita
from Model.ViewReceita import TelaViewReceita

from View.tela_cria_receita import Ui_TelaCriaReceita

from Controller.Message import MessageBox, SimpleMessageBox
from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard

class TelaCriaReceita(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None):
        super().__init__()
        self.dado=dado
        self.io=io
        self.database = db
        self.url_imagem_esquerda = None
        self.url_imagem_direita = None
        self.rotina = rotina

        self.msg = SimpleMessageBox()
        self.msg_box = MessageBox()

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaCriaReceita()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.limpaeletrodo()

        self.ui.btVoltar.clicked.connect(self.voltar)
        self.ui.btSlavar.clicked.connect(self.salvar)
        self.ui.btApagar.clicked.connect(self.deletar)
        self.ui.btAtualizar.clicked.connect(self.atualizar)
        self.ui.btLocalizar.clicked.connect(self.localizar)

        self.ui.lbImgEsquerdo.mousePressEvent = self.clique_image_esquerdo
        self.ui.lbImgDireito.mousePressEvent = self.clique_image_direito
    
        self.ui.txNomePrograma.mousePressEvent = self.completa_nome

        self.ui.txNomePrograma.setText("")
    
    def limpaeletrodo(self):
        self.ui.lbEletrodo1_Dir.setVisible(False)
        self.ui.lbEletrodo1_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo2_Dir.setVisible(False)
        self.ui.lbEletrodo2_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo3_Dir.setVisible(False)
        self.ui.lbEletrodo3_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo4_Dir.setVisible(False)
        self.ui.lbEletrodo4_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo5_Dir.setVisible(False)
        self.ui.lbEletrodo5_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo6_Dir.setVisible(False)
        self.ui.lbEletrodo6_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo7_Dir.setVisible(False)
        self.ui.lbEletrodo7_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo8_Dir.setVisible(False)
        self.ui.lbEletrodo8_Dir.setParent(self.ui.lbImgDireito) # Seta label para acertar coordenadas

        self.ui.lbEletrodo1_Esque.setVisible(False)
        self.ui.lbEletrodo1_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo2_Esque.setVisible(False)
        self.ui.lbEletrodo2_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo3_Esque.setVisible(False)
        self.ui.lbEletrodo3_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo4_Esque.setVisible(False)
        self.ui.lbEletrodo4_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo5_Esque.setVisible(False)
        self.ui.lbEletrodo5_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo6_Esque.setVisible(False)
        self.ui.lbEletrodo6_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo7_Esque.setVisible(False)
        self.ui.lbEletrodo7_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

        self.ui.lbEletrodo8_Esque.setVisible(False)
        self.ui.lbEletrodo8_Esque.setParent(self.ui.lbImgEsquerdo) # Seta label para acertar coordenadas

    def completa_nome(self, event):
        teclado = AlphanumericKeyboard(dado=self.dado)
        teclado.exec_()
        self.ui.txNomePrograma.setText(teclado.line_edit.text())
        self.rotina.nome_programa = self.ui.txNomePrograma.text()

    def clique_image_esquerdo(self, event):
        if self.ui.txNomePrograma.text() != "":
            receita_esquerda = TelaReceitaEsquerda(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina)
            self.dado.set_telas(self.dado.TELA_RECEITA_ESQUERDA)
            receita_esquerda.exec_()
            self.load_config(receita_esquerda.rotina.coord_eletrodo_esquerdo, 0) # 0 Representa o lado esquerdo
        else:
            msg = SimpleMessageBox()
            msg.exec(f"Por favor especifique um nome de programa.")
        
    def load_config(self, coord, lado):
        if self.rotina.url_img_esquerdo != "" or self.rotina.url_img_direito != "":
            dir_open = OpenFile(dado=self.dado, io=self.io, db=self.database)
            if lado == 0:# Se for lado esquerdo
                dir_open.load_image_url(image_path=self.rotina.url_img_esquerdo , size_x=self.ui.lbImgEsquerdo.width() , size_y=self.ui.lbImgEsquerdo.height())
            elif lado == 1:# Se for lado direito
                dir_open.load_image_url(image_path=self.rotina.url_img_direito , size_x=self.ui.lbImgDireito.width() , size_y=self.ui.lbImgDireito.height())
            if dir_open.image != None and lado == 0:# Lado direito
                self.ui.lbImgEsquerdo.setPixmap(dir_open.image)
            elif dir_open.image != None and lado == 1:# Lado esquerdo
                self.ui.lbImgDireito.setPixmap(dir_open.image)

            for index in range(len(coord)):
                if index == 1 and coord[1]!=None:
                    self.posiciona_eletrodos(1,lado,coord[index])

                elif index == 2 and coord[2]!=None:
                    self.posiciona_eletrodos(2,lado,coord[index])

                elif index == 3 and coord[3]!=None:
                    self.posiciona_eletrodos(3,lado,coord[index])

                elif index == 4 and coord[4]!=None:
                    self.posiciona_eletrodos(4,lado,coord[index])

                elif index == 5 and coord[5]!=None:
                    self.posiciona_eletrodos(5,lado,coord[index])

                elif index == 6 and coord[6]!=None:
                    self.posiciona_eletrodos(6,lado,coord[index])

                elif index == 7 and coord[7]!=None:
                    self.posiciona_eletrodos(7,lado,coord[index])

                elif index == 8 and coord[8]!=None:
                    self.posiciona_eletrodos(8,lado,coord[index])

    def posiciona_eletrodos(self, eletrodo, lado, coord):
        if lado == 0:
            # Construa o nome do objeto dinamicamente com o dígito atual (i)
            object_name = f"lbEletrodo{eletrodo}_Esque"
            # Acesse o objeto usando o nome dinâmico dentro do loop
            current_object = getattr(self.ui, object_name)
        elif lado == 1:
            # Construa o nome do objeto dinamicamente com o dígito atual (i)
            object_name = f"lbEletrodo{eletrodo}_Dir"
            # Acesse o objeto usando o nome dinâmico dentro do loop
            current_object = getattr(self.ui, object_name)
            
        current_object.move( coord[0] - current_object.width() // 2,coord[1] - current_object.height() // 2)
        current_object.setVisible(True)

    def clique_image_direito(self, event):
        if self.ui.txNomePrograma.text() != "":
            receita_esquerda = TelaReceitaDireita(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina)
            self.dado.set_telas(self.dado.TELA_RECEITA_DIREITA)
            receita_esquerda.exec_()
            self.load_config(receita_esquerda.rotina.coord_eletrodo_direito, 1) # 1 Representa o lado direito
        else:
            msg = SimpleMessageBox()
            msg.exec(f"Por favor especifique um nome de programa.")

# nome_programa, url_img_esquerdo, url_img_direito,
# coord_eletrodo_esquerdo, coord_eletrodo_direito,
# condutividade_esquerdo, condutividade_direito,
# isolacao_esquerdo, isolacao_direito

    def salvar(self):
        
        if self.valida_dados() == True:
            self.rotina.url_img_esquerdo,self.rotina.url_img_direito = self.armazena_img_local(self.rotina.url_img_esquerdo,self.rotina.url_img_direito, self.rotina.nome_programa) 
            self.database.create_record_receita(self.rotina.nome_programa,self.rotina.url_img_esquerdo,
                                                self.rotina.url_img_direito,
                                                self.rotina.coord_eletrodo_esquerdo, self.rotina.coord_eletrodo_direito,
                                                self.rotina.condutividade_esquerdo, self.rotina.condutividade_direito,
                                                self.rotina.isolacao_esquerdo, self.rotina.isolacao_direito
                                                )
            self.msg.exec(msg="Programa Salvo com sucesso.")
            self.ui.txNomePrograma.clear()
            self.rotina.nome_programa = ""
            self.rotina.clear_dados_esquerdo()
            self.rotina.clear_dados_direito()
            self.limpaeletrodo()
        else:
            self.msg.exec(msg="Os dados não estão completos\nOu esse programa já existe.")
    
    def deletar(self):
        try:
            id ,_ ,_ ,_ ,_ ,_ ,_ ,_ ,_ ,_ = self.database.search_name_receita(self.ui.txNomePrograma.text())
            self.msg_box.exec(msg="Tem certeza que dezeja excluir esse programa?")
            if self.msg_box.yes_no == True:
                self.database.delete_receita_id(id)
                self.msg.exec(msg="Programa excluído com sucesso.")
                self.ui.txNomePrograma.clear()
                self.rotina.nome_programa = ""
                self.rotina.clear_dados_esquerdo()
                self.rotina.clear_dados_direito()
                self.limpaeletrodo()
        except:
            self.msg.exec(msg="Esse programa não existe e não pode ser deletado.")

    def atualizar(self):

        try:
            id ,_ ,_ ,_ ,_ ,_ ,_ ,_ ,_ ,_ = self.database.search_name_receita(self.ui.txNomePrograma.text())
            self.rotina.url_img_esquerdo,self.rotina.url_img_direito = self.armazena_img_local(self.rotina.url_img_esquerdo,self.rotina.url_img_direito, self.rotina.nome_programa) 
            self.msg_box.exec(msg="Tem certeza que dezeja atualizar esse programa?")
            if self.msg_box.yes_no == True:
                self.database.update_record_receita(id, self.rotina.nome_programa, self.rotina.url_img_esquerdo, self.rotina.url_img_direito,
                        self.rotina.coord_eletrodo_esquerdo, self.rotina.coord_eletrodo_direito,
                        self.rotina.condutividade_esquerdo, self.rotina.condutividade_direito,
                        self.rotina.isolacao_esquerdo, self.rotina.isolacao_direito)
                self.msg.exec(msg="Programa atualizado com sucesso.")
                self.ui.txNomePrograma.clear()
                self.rotina.nome_programa = ""
                self.rotina.clear_dados_esquerdo()
                self.rotina.clear_dados_direito()
                self.limpaeletrodo()
        except:
            self.msg.exec(msg="Esse programa não existe e não pode ser atualizado.")


    def localizar(self):
        self.dado.set_telas(self.dado.TELA_RECEITA_VIEW)
        view = TelaViewReceita(dado = self.dado, io=self.io, db=self.database, target=self.dado.TELA_CRIAR_RECEITA)
        view.exec_()
        try:
            _, self.rotina.nome_programa, self.rotina.url_img_esquerdo,self.rotina.url_img_direito, self.rotina.coord_eletrodo_esquerdo,self.rotina.coord_eletrodo_direito, self.rotina.condutividade_esquerdo, self.rotina.condutividade_direito, self.rotina.isolacao_esquerdo, self.rotina.isolacao_direito = self.database.search_name_receita(view.nome_programa)
            self.ui.txNomePrograma.setText(self.rotina.nome_programa)
            self.load_config(self.rotina.coord_eletrodo_esquerdo, 0) # 0 Representa o lado esquerdo
            self.load_config(self.rotina.coord_eletrodo_direito, 1) # 1 Representa o lado direito
        except:
            print("Erro de ao tentar localizar programa.")

    def valida_dados(self):
        result = False
        if self.ui.txNomePrograma.text() != "":
            try:
                ret = self.database.search_name_receita(self.ui.txNomePrograma.text())
                if ret != None:
                    result = False
                elif self.rotina.url_img_esquerdo != "" and self.rotina.url_img_direito != "" and any(coord is not None for coord in self.rotina.coord_eletrodo_esquerdo) == True and any(coord is not None for coord in self.rotina.coord_eletrodo_direito) == True:
                    result = True
                else:
                    result = False
            except:
                result = False

        return result
    def armazena_img_local(self, url_esquerdo, url_direito, nome_prog):
        pasta_destino = "url_img"
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        nome_esquerdo = os.path.splitext(os.path.basename(url_esquerdo))[0]
        nome_direito = os.path.splitext(os.path.basename(url_direito))[0]

        novo_nome_esquerdo = f"{nome_esquerdo}_{nome_prog}"
        novo_nome_direito = f"{nome_direito}_{nome_prog}"

        novo_caminho_esquerdo = os.path.join(pasta_destino, f"{novo_nome_esquerdo}.jpg")
        novo_caminho_direito = os.path.join(pasta_destino, f"{novo_nome_direito}.jpg")

        shutil.copy(url_esquerdo, novo_caminho_esquerdo)
        shutil.copy(url_direito, novo_caminho_direito)

        return novo_caminho_esquerdo, novo_caminho_direito

    def voltar(self):
        self.ui.txNomePrograma.clear()
        self.rotina.nome_programa = ""
        self.rotina.clear_dados_esquerdo()
        self.rotina.clear_dados_direito()
        self.limpaeletrodo()
        self.dado.set_telas(self.dado.TELA_CONFIG)
        self.close()
    def closeEvent(self, event):
        event.accept()