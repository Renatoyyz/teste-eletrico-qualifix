import sqlite3
from datetime import datetime
import json

class DataBase:
    def __init__(self, database_name='database.db'):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

        self._login_default = "QUALIFIX" # Esse será o login master
        self._senha_default = "1420" # senha poderá ser mudado posteriormente
        self._permissao_default = 1 # 1 significa permissões de administrador

        self._login_user_default = "USUARIO" # Esse será o login master
        self._senha_user_default = "1234" # senha poderá ser mudado posteriormente
        self._permissao_user_default = 0 # 0 significa que não tem permissões de administrador

        self.create_table_login()
        self.create_table_receita()
        self.criar_tabela_rotina()
        admin_temp = self.search_name_login(self._login_default)
        if admin_temp == None:
            data = [self._login_default, self._senha_default, self._permissao_default]
            self.create_record_login(data=data)
        user_temp = self.search_name_login(self._login_user_default)
        if user_temp == None:
            data = [self._login_user_default, self._senha_user_default, self._permissao_user_default]
            self.create_record_login(data=data)

        # Só para testes
        # receita_temp = self.search_name_receita("Receita")
        # if receita_temp ==None:
        #     data = ["Receita", "Qualifix", self._login_default]
        #     self.create_record_receita(data=data)


    def create_table_login(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS login (
                                id INTEGER PRIMARY KEY,
                                usuario TEXT,
                                senha TEXT,
                                permissao INTEGER
                                )''')
        self.conn.commit()

    # Função para criar a tabela se não existir
    def create_table_receita(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receita (
                id INTEGER PRIMARY KEY,
                nome_programa TEXT,
                url_img_esquerdo TEXT,
                url_img_direito TEXT,
                coord_eletrodo_esquerdo TEXT,
                coord_eletrodo_direito TEXT,
                condutividade_esquerdo TEXT,
                condutividade_direito TEXT,
                isolacao_esquerdo TEXT,
                isolacao_direito TEXT
            )
        ''')
        self.conn.commit()

    # Função para criar a tabela de rotina
    def criar_tabela_rotina(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rotina (
                    id INTEGER PRIMARY KEY,
                    programa TEXT,
                    peca_esquerda_aprovada INTEGER,
                    peca_direita_aprovada INTEGER,
                    peca_esquerda_reprovada INTEGER,
                    peca_direita_reprovada INTEGER,
                    peca_esquerda_retrabalhada INTEGER,
                    peca_direita_retrabalhada INTEGER,
                    iniciado TIMESTAMP,
                    finalizado TIMESTAMP,
                    login TEXT,
                    fim_rotina INTEGER,
                    qtd_ciclos INTEGER
                    )''')
        self.conn.commit()
#Para criação
    def create_record_login(self, data):
        self.cursor.execute('''INSERT INTO login 
                               (usuario, senha, permissao) 
                               VALUES (?, ?, ?)''', data)
        self.conn.commit()
    def create_record_receita(self,nome_programa, url_img_esquerdo, url_img_direito,
                        coord_eletrodo_esquerdo, coord_eletrodo_direito,
                        condutividade_esquerdo, condutividade_direito,
                        isolacao_esquerdo, isolacao_direito):
        self.cursor.execute('''
            INSERT INTO receita (nome_programa, url_img_esquerdo, url_img_direito,
                            coord_eletrodo_esquerdo, coord_eletrodo_direito,
                            condutividade_esquerdo, condutividade_direito,
                            isolacao_esquerdo, isolacao_direito)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_programa, url_img_esquerdo, url_img_direito,
            json.dumps(coord_eletrodo_esquerdo), json.dumps(coord_eletrodo_direito),
            json.dumps(condutividade_esquerdo), json.dumps(condutividade_direito),
            json.dumps(isolacao_esquerdo), json.dumps(isolacao_direito)))
        self.conn.commit()
    def create_record_rotina(self,programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                        esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos):
        self.cursor.execute('''INSERT INTO rotina (programa, peca_esquerda_aprovada, peca_direita_aprovada,
                    peca_esquerda_reprovada, peca_direita_reprovada, peca_esquerda_retrabalhada,
                    peca_direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos))
        self.conn.commit()

    # Para atualizar
    def update_record_login(self, record_id, data):
        query = '''UPDATE login SET 
                   usuario=?, senha=?, permissao=?
                   WHERE id=?'''
        self.cursor.execute(query, data + [record_id])
        self.conn.commit()
    def update_record_receita(self, id, nome_programa, url_img_esquerdo, url_img_direito,
                        coord_eletrodo_esquerdo, coord_eletrodo_direito,
                        condutividade_esquerdo, condutividade_direito,
                        isolacao_esquerdo, isolacao_direito):
        self.cursor.execute('''
            UPDATE receita SET nome_programa = ?, url_img_esquerdo = ?, url_img_direito = ?,
                            coord_eletrodo_esquerdo = ?, coord_eletrodo_direito = ?,
                            condutividade_esquerdo = ?, condutividade_direito = ?,
                            isolacao_esquerdo = ?, isolacao_direito = ?
            WHERE id = ?
        ''', (nome_programa, url_img_esquerdo, url_img_direito,
            json.dumps(coord_eletrodo_esquerdo), json.dumps(coord_eletrodo_direito),
            json.dumps(condutividade_esquerdo), json.dumps(condutividade_direito),
            json.dumps(isolacao_esquerdo), json.dumps(isolacao_direito),
            id))
        self.conn.commit()
    def update_record_rotina(self,id, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                        esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos):
        self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                    peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                    peca_direita_retrabalhada=?, iniciado=?, finalizado=?, login=?, fim_rotina=?, qtd_ciclos=?
                    WHERE id=?''',
                (programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos, id))
        self.conn.commit()
    def update_record_rotina_by_name_sem_data(self,nome_atualizado, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                        esquerda_retrabalhada, direita_retrabalhada, login, fim_rotina, qtd_ciclos):
        self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                    peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                    peca_direita_retrabalhada=?, login=?, fim_rotina=?, qtd_ciclos=?
                    WHERE programa=?''',
                (nome_atualizado, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                esquerda_retrabalhada, direita_retrabalhada, login, fim_rotina, qtd_ciclos, programa))
        self.conn.commit()
    def update_record_rotina_by_name_finalizado(self,nome_atualizado, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                        esquerda_retrabalhada, direita_retrabalhada, finalizado, login, fim_rotina, qtd_ciclos):
        self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                    peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                    peca_direita_retrabalhada=?, finalizado=?, login=?, fim_rotina=?, qtd_ciclos=?
                    WHERE programa=?''',
                (nome_atualizado, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                esquerda_retrabalhada, direita_retrabalhada, finalizado, login, fim_rotina, qtd_ciclos, programa))
        self.conn.commit()

    # Para deletar
    def delete_record_login(self, record_id):
        query = 'DELETE FROM login WHERE id=?'
        self.cursor.execute(query, (record_id,))
        self.conn.commit()
    def delete_login_name(self, name):
        query = 'DELETE FROM login WHERE usuario=?'
        self.cursor.execute(query, (name,))
        self.conn.commit()
    def delete_receita_name(self, nome_programa):
        self.cursor.execute('DELETE FROM receita WHERE nome_programa = ?', (nome_programa,))
        self.conn.commit()
    def delete_receita_id(self, id):
        self.cursor.execute('DELETE FROM receita WHERE id = ?', (id,))
        self.conn.commit()
    # Função para excluir um registro
    def delete_rotina_id(self,id):
        self.cursor.execute('''DELETE FROM rotina WHERE id=?''', (id,))
        self.conn.commit()
    
    def search_record_login(self, record_id):
        query = 'SELECT * FROM login WHERE id=?'
        self.cursor.execute(query, (record_id,))
        return self.cursor.fetchone()
    def search_name_login(self, name):
        query = 'SELECT * FROM login WHERE usuario=?'
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone()
    # Função para selecionar um registro pelo ID e retornar variáveis separadas
    def search_name_receita(self, name):
        self.cursor.execute('SELECT * FROM receita WHERE nome_programa = ?', (name,))
        registro = self.cursor.fetchone()
        if registro:
            id, nome_programa, url_img_esquerdo, url_img_direito, \
            coord_eletrodo_esquerdo_json, coord_eletrodo_direito_json, \
            condutividade_esquerdo_json, condutividade_direito_json, \
            isolacao_esquerdo_json, isolacao_direito_json = registro
            
            # Converter JSON para dicionários
            coord_eletrodo_esquerdo = json.loads(coord_eletrodo_esquerdo_json)
            coord_eletrodo_direito = json.loads(coord_eletrodo_direito_json)
            condutividade_esquerdo = json.loads(condutividade_esquerdo_json)
            condutividade_direito = json.loads(condutividade_direito_json)
            isolacao_esquerdo = json.loads(isolacao_esquerdo_json)
            isolacao_direito = json.loads(isolacao_direito_json)
            
            return (id, nome_programa, url_img_esquerdo, url_img_direito,
                    coord_eletrodo_esquerdo, coord_eletrodo_direito,
                    condutividade_esquerdo, condutividade_direito,
                    isolacao_esquerdo, isolacao_direito)
        else:
            return None
    def get_all_records_login(self):
        query = 'SELECT * FROM login'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    # Função para selecionar todos os registros
    def get_all_records_receita(self):
        self.cursor.execute('SELECT * FROM receita')
        registros = self.cursor.fetchall()
        return registros
    
    # Função para obter todos os registros
    def get_all_records_rotina(self):
        self.cursor.execute('''SELECT * FROM rotina''')
        rows = self.cursor.fetchall()
        return rows
    def search_name_rotina(self,nome):
        self.cursor.execute('''SELECT * FROM rotina WHERE programa = ?''', (nome,))
        rows = self.cursor.fetchall()
        return rows
    
    def search_fim_rotina(self):
        self.cursor.execute('''SELECT * FROM rotina WHERE fim_rotina = ?''', (0,))
        rows = self.cursor.fetchall()
        return rows
        
    def stop(self):
        self.conn.close()
        return 0

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    db = DataBase()
