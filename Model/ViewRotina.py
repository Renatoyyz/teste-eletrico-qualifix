import json
from PyQt5.QtWidgets import QDialog,QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from View.tela_view_rotina import Ui_TelaViewRotina

from Model.ExecucaoPrograma import TelaExecucao

from Controller.Teclados import AlphanumericKeyboard, NumericKeyboard
from Controller.Message import SimpleMessageBox, MessageBox
import csv
import os
import subprocess
import time

class TelaViewRotina(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina = None, target=None):
        super().__init__()
        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina
        self.target = target
        self.nome_programa = ""

        self.msg = SimpleMessageBox()

        # Configuração da interface do usuário gerada pelo Qt Designer
        self.ui = Ui_TelaViewRotina()
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
        self.model.setHorizontalHeaderLabels(['Nome Rotina','Data', 'Login'])

        # Obtenha todos os registros do banco de dados
        records = self.database.get_all_records_rotina()

        # Preencha o QStandardItemModel com os registros
        for row_data in records:
            # Obtém os valores da coluna 1 e 3 (índices 0 e 2 na lista row_data)
            nome_prog = row_data[1]# Nome do programa
            data_hora = row_data[8]# Data de início da rotina
            login = row_data[10]# Login

            col1_item = QStandardItem(str(nome_prog))
            col2_item = QStandardItem(str(data_hora))
            col3_item = QStandardItem(str(login))

            # Adiciona os itens à linha do modelo (ignorando a coluna "id")
            self.model.appendRow([col1_item, col2_item, col3_item])

        # Conecte o QStandardItemModel à QTableView
        self.ui.tblViewRotina.setModel(self.model)

        # Defina as colunas para que preencham toda a largura da tabela
        header = self.ui.tblViewRotina.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Crie o layout para a janela
        layout = QVBoxLayout()
        layout.addWidget(self.ui.tblViewRotina)
        self.setLayout(layout)

        self.ui.btVoltar.clicked.connect(self.sair)
        # Conecte o sinal clicked da QTableView à função on_table_view_clicked
        self.ui.tblViewRotina.clicked.connect(self.on_table_view_clicked)

    def on_table_view_clicked(self, index):
        # Aqui você pode obter a linha e coluna do índice clicado
        row = index.row()
        # column = index.column()

        # Obtém o texto do item da célula clicada sempre na primeira coluna da linha clicada, que é o nome do programa
        item = self.model.item(row, 0)
        if item is not None:
            cell_text = item.text()
            # print(f"Célula clicada: Linha {row}, Coluna {column}, Texto: {cell_text}")
            self.nome_programa = cell_text.split("$") # Retira caracter especial para separar nome de rotina do nome de programa
            self.nome_programa = self.nome_programa[0]
            if self.target == self.dado.TELA_CONFIG:
                self.dado.set_telas(self.dado.TELA_CONFIG)
                if self.salvar_registros_csv_por_programa(cell_text) == True:
                    self.msg.exec(msg="Registro salvo com sucesso!")
                else:
                    self.msg.exec(msg="Erro ao carregar dados.\nVerificar se há um dispositivo de armazenamento.")

            elif self.target == self.dado.TELA_EXECUCAO:
                self.dado.set_telas(self.dado.TELA_EXECUCAO)
                execucao = TelaExecucao(dado=self.dado, io=self.io, db=self.database, rotina=self.rotina, nome_prog = self.nome_programa)
                execucao.exec_()
            self.close()

    def salvar_registros_csv_por_programa(self, programa):
        try:
            # Obter registros por programa
            registros = self.database.search_name_rotina(programa)

            # Verificar se o diretório de destino existe, se não, devolve falso
            # diretorio_destino = "/media/desenvolvimento"
            diretorio_destino = self.encontrar_pendrive()
            if os.path.exists(diretorio_destino):

                # Nome do arquivo CSV
                nome_arquivo = os.path.normpath(os.path.join(diretorio_destino, f"{programa}.csv"))
                # nome_arquivo = os.path.normpath(os.path.join(diretorio_destino, f"{limpar_nome_arquivo(programa)}.csv"))
                subprocess.run(['sudo', 'chmod', '777', nome_arquivo])

                with open(nome_arquivo, 'w', newline='') as csvfile:
                    escritor_csv = csv.writer(csvfile)
                    
                    # Escrever cabeçalho
                    escritor_csv.writerow(['ID', 'Programa', 'Peca Esquerda Aprovada', 'Peca Direita Aprovada',
                                        'Peca Esquerda Reprovada', 'Peca Direita Reprovada',
                                        'Peca Esquerda Retrabalhada', 'Peca Direita Retrabalhada',
                                        'Iniciado', 'Finalizado', 'Login'])

                    # Escrever registros
                    for registro in registros:
                        escritor_csv.writerow(registro)  
                    csvfile.close()
                    self.desmontar_pendrive() 

                return True     
            else:
                return False 
        except:
            return False
        
    
    def encontrar_pendrive(self):
        diretorio_media = '/media/desenvolvimento'
        pendrives = [d for d in os.listdir(diretorio_media) if os.path.isdir(os.path.join(diretorio_media, d))]
        for pendrive in pendrives:
            # Verifique se o diretório parece ser um pendrive (por exemplo, começa com 'usb' ou 'disk')
            # if 'usb' in pendrive.lower() or 'disk' in pendrive.lower():
            return os.path.join(diretorio_media, pendrive)
        return None
    
    def desmontar_pendrive(self):
        diretorio_pendrive = self.encontrar_pendrive()
        if diretorio_pendrive:
            try:
                subprocess.run(['sudo', 'umount', diretorio_pendrive])
                print("Pendrive desmontado com sucesso:", diretorio_pendrive)
            except Exception as e:
                print("Erro ao desmontar o pendrive:", e)
                print("Tentando novamente após 1 segundo...")
                time.sleep(1)
                try:
                    subprocess.run(['sudo', 'umount', diretorio_pendrive])
                    print("Pendrive desmontado com sucesso:", diretorio_pendrive)
                except Exception as e:
                    print("Erro ao desmontar o pendrive após a segunda tentativa:", e)
        else:
            print("Pendrive não encontrado em /media.")


    def sair(self):
        if self.target == self.dado.TELA_CRIAR_RECEITA:
            self.dado.set_telas(self.dado.TELA_CRIAR_RECEITA)
        elif self.target == self.dado.TELA_EXECUCAO:
            self.dado.set_telas(self.dado.TELA_INICIAL)
        self.close()
    def closeEvent(self, event):
        event.accept()