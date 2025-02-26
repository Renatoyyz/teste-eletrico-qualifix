from PyQt5.QtWidgets import QDialog,QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from View.tela_view_login import Ui_TelaViewLogin

from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox

class TelaViewLogin(QDialog):
    def __init__(self, dado=None, io=None, db=None):
        super().__init__()
        self.dado = dado
        self.io = io
        self.database = db
        self.nome_login = ""

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaViewLogin()
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
        self.model.setHorizontalHeaderLabels(['Nome Login','Tipo de permissão'])

        # Obtenha todos os registros do banco de dados
        records = self.database.get_all_records_login()

        # Preencha o QStandardItemModel com os registros
        for row_data in records:
            # Obtém os valores da coluna 1 e 3 (índices 0 e 2 na lista row_data)
            col1_value = row_data[1]
            col3_value = row_data[3]

            # Substitui o valor da coluna 3 por "usuário" ou "administrador"
            if col3_value == 0:
                col3_display = "usuário"
            elif col3_value == 1:
                col3_display = "administrador"
            else:
                col3_display = str(col3_value)  # Se não for 0 nem 1, mantém o valor original

            # Cria QStandardItems para os valores das colunas 1 e 3
            col1_item = QStandardItem(str(col1_value))
            col3_item = QStandardItem(col3_display)

            # Adiciona os itens à linha do modelo (ignorando a coluna "id")
            self.model.appendRow([col1_item, col3_item])

        # Conecte o QStandardItemModel à QTableView
        self.ui.tblViewLogin.setModel(self.model)

        # Defina as colunas para que preencham toda a largura da tabela
        header = self.ui.tblViewLogin.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Crie o layout para a janela
        layout = QVBoxLayout()
        layout.addWidget(self.ui.tblViewLogin)
        self.setLayout(layout)

        self.ui.btVoltar.clicked.connect(self.sair)
        # Conecte o sinal clicked da QTableView à função on_table_view_clicked
        self.ui.tblViewLogin.clicked.connect(self.on_table_view_clicked)

    def on_table_view_clicked(self, index):
        # Aqui você pode obter a linha e coluna do índice clicado
        row = index.row()
        # column = index.column()

        # Obtém o texto do item da célula clicada sempre na primeira coluna da linha clicada, que é o nome do programa
        item = self.model.item(row, 0)
        if item is not None:
            cell_text = item.text()
            # print(f"Célula clicada: Linha {row}, Coluna {column}, Texto: {cell_text}")
            self.nome_login = cell_text
            self.close()

    def sair(self):
        self.dado.set_telas(self.dado.TELA_CADASTRO_USER)
        self.close()
    def closeEvent(self, event):
        event.accept()