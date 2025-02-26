import json
from PyQt5.QtWidgets import QDialog,QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from View.tela_view_receita import Ui_TelaViewReceita

from Model.ExecucaoPrograma import TelaExecucao

from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

class TelaViewReceita(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina = None, target=None):
        super().__init__()
        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina
        self.target = target
        self.nome_programa = ""

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaViewReceita()
        self.ui.setupUi(self)

        # Remover a barra de título e ocultar os botões de maximizar e minimizar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)
        
        # Maximizar a janela
        # self.showMaximized()
        if self.dado.full_scream == True:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Crie o modelo de dados para a QTableView
        self.model = QStandardItemModel(self)

        # Defina os cabeçalhos da tabela
        self.model.setHorizontalHeaderLabels(['Nome Programa','Programa testado?'])

        # Obtenha todos os registros do banco de dados
        records = self.database.get_all_records_receita()

        # Preencha o QStandardItemModel com os registros
        for row_data in records:
            # Obtém os valores da coluna 1 e 3 (índices 0 e 2 na lista row_data)
            nome_prog = row_data[1]# Nome do programa
            condutividade_esquerdo = json.loads(row_data[6])["foi_testado"] # Condutividade esquerdo
            condutividade_direito = json.loads(row_data[7])["foi_testado"] # Condutividade esquerdo
            isolacao_esquerdo = json.loads(row_data[8])["foi_testado"] # Condutividade esquerdo
            isolacao_direito = json.loads(row_data[9])["foi_testado"] # Condutividade esquerdo

            # json.loads(registro[6])["foi_testado"]

            # Analiza se foi testado ou não
            if condutividade_esquerdo == False or condutividade_direito == False or isolacao_esquerdo == False or isolacao_direito == False:
                testado = "Não"
            else:
                testado = "Sim"

            # Se for para tela execução só poderão os progamas testados
            if self.target == self.dado.TELA_EXECUCAO and testado == "Sim":
                # Cria QStandardItems para os valores das colunas 1 e 3
                col1_item = QStandardItem(str(nome_prog))
                col3_item = QStandardItem(str(testado))

                # Adiciona os itens à linha do modelo (ignorando a coluna "id")
                self.model.appendRow([col1_item, col3_item])
            elif self.target == self.dado.TELA_CRIAR_RECEITA:
                # Cria QStandardItems para os valores das colunas 1 e 3
                col1_item = QStandardItem(str(nome_prog))
                col3_item = QStandardItem(str(testado))

                # Adiciona os itens à linha do modelo (ignorando a coluna "id")
                self.model.appendRow([col1_item, col3_item])

        # Conecte o QStandardItemModel à QTableView
        self.ui.tblViewReceita.setModel(self.model)

        # Defina as colunas para que preencham toda a largura da tabela
        header = self.ui.tblViewReceita.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Crie o layout para a janela
        layout = QVBoxLayout()
        layout.addWidget(self.ui.tblViewReceita)
        self.setLayout(layout)

        self.ui.btVoltar.clicked.connect(self.sair)
        # Conecte o sinal clicked da QTableView à função on_table_view_clicked
        self.ui.tblViewReceita.clicked.connect(self.on_table_view_clicked)

    def on_table_view_clicked(self, index):
        # Aqui você pode obter a linha e coluna do índice clicado
        row = index.row()
        # column = index.column()

        # Obtém o texto do item da célula clicada sempre na primeira coluna da linha clicada, que é o nome do programa
        item = self.model.item(row, 0)
        if item is not None:
            cell_text = item.text()
            # print(f"Célula clicada: Linha {row}, Coluna {column}, Texto: {cell_text}")
            self.nome_programa = cell_text
            if self.target == self.dado.TELA_CRIAR_RECEITA:
                self.dado.set_telas(self.dado.TELA_CRIAR_RECEITA)
            elif self.target == self.dado.TELA_EXECUCAO:
                self.dado.set_telas(self.dado.TELA_EXECUCAO)
                execucao = TelaExecucao(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina, nome_prog = self.nome_programa)
                execucao.exec_()
            self.close()

    def sair(self):
        if self.target == self.dado.TELA_CRIAR_RECEITA:
            self.dado.set_telas(self.dado.TELA_CRIAR_RECEITA)
        elif self.target == self.dado.TELA_EXECUCAO:
            self.dado.set_telas(self.dado.TELA_INICIAL)
        self.close()
    def closeEvent(self, event):
        event.accept()