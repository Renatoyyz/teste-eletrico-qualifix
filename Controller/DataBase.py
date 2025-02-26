import sqlite3
from datetime import datetime
import json
import logging

# Configuração do logging
logging.basicConfig(filename='database.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class DataBase:
    def __init__(self, database_name='database.db'):
        try:
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

        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ou inicializar o banco de dados: {e}")

    def create_table_login(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS login (
                                    id INTEGER PRIMARY KEY,
                                    usuario TEXT,
                                    senha TEXT,
                                    permissao INTEGER
                                    )''')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar a tabela login: {e}")

    def create_table_receita(self):
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar a tabela receita: {e}")

    def criar_tabela_rotina(self):
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar a tabela rotina: {e}")

    def create_record_login(self, data):
        try:
            self.cursor.execute('''INSERT INTO login 
                                   (usuario, senha, permissao) 
                                   VALUES (?, ?, ?)''', data)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar registro login: {e}")

    def create_record_receita(self, nome_programa, url_img_esquerdo, url_img_direito,
                            coord_eletrodo_esquerdo, coord_eletrodo_direito,
                            condutividade_esquerdo, condutividade_direito,
                            isolacao_esquerdo, isolacao_direito):
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar registro receita: {e}")

    def create_record_rotina(self, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                            esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos):
        try:
            self.cursor.execute('''INSERT INTO rotina (programa, peca_esquerda_aprovada, peca_direita_aprovada,
                        peca_esquerda_reprovada, peca_direita_reprovada, peca_esquerda_retrabalhada,
                        peca_direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                    esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar registro rotina: {e}")

    def update_record_login(self, record_id, data):
        try:
            query = '''UPDATE login SET 
                       usuario=?, senha=?, permissao=?
                       WHERE id=?'''
            self.cursor.execute(query, data + [record_id])
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar registro login: {e}")

    def update_record_receita(self, id, nome_programa, url_img_esquerdo, url_img_direito,
                            coord_eletrodo_esquerdo, coord_eletrodo_direito,
                            condutividade_esquerdo, condutividade_direito,
                            isolacao_esquerdo, isolacao_direito):
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar registro receita: {e}")

    def update_record_rotina(self, id, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                            esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos):
        try:
            self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                        peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                        peca_direita_retrabalhada=?, iniciado=?, finalizado=?, login=?, fim_rotina=?, qtd_ciclos=?
                        WHERE id=?''',
                    (programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                    esquerda_retrabalhada, direita_retrabalhada, iniciado, finalizado, login, fim_rotina, qtd_ciclos, id))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar registro rotina: {e}")

    def update_record_rotina_by_name_sem_data(self, nome_atualizado, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                                            esquerda_retrabalhada, direita_retrabalhada, login, fim_rotina, qtd_ciclos):
        try:
            self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                        peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                        peca_direita_retrabalhada=?, login=?, fim_rotina=?, qtd_ciclos=?
                        WHERE programa=?''',
                    (nome_atualizado, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                    esquerda_retrabalhada, direita_retrabalhada, login, fim_rotina, qtd_ciclos, programa))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar rotina por nome (sem data): {e}")

    def update_record_rotina_by_name_finalizado(self, nome_atualizado, programa, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                                            esquerda_retrabalhada, direita_retrabalhada, finalizado, login, fim_rotina, qtd_ciclos):
        try:
            self.cursor.execute('''UPDATE rotina SET programa=?, peca_esquerda_aprovada=?, peca_direita_aprovada=?,
                        peca_esquerda_reprovada=?, peca_direita_reprovada=?, peca_esquerda_retrabalhada=?,
                        peca_direita_retrabalhada=?, finalizado=?, login=?, fim_rotina=?, qtd_ciclos=?
                        WHERE programa=?''',
                    (nome_atualizado, esquerda_aprovada, direita_aprovada, esquerda_reprovada, direita_reprovada,
                    esquerda_retrabalhada, direita_retrabalhada, finalizado, login, fim_rotina, qtd_ciclos, programa))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar rotina por nome (com data de finalização): {e}")

    def delete_record_login(self, record_id):
        try:
            query = 'DELETE FROM login WHERE id=?'
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar registro login: {e}")

    def delete_login_name(self, name):
        try:
            query = 'DELETE FROM login WHERE usuario=?'
            self.cursor.execute(query, (name,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar login pelo nome: {e}")

    def delete_receita_name(self, nome_programa):
        try:
            self.cursor.execute('DELETE FROM receita WHERE nome_programa = ?', (nome_programa,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar receita pelo nome: {e}")

    def delete_receita_id(self, id):
        try:
            self.cursor.execute('DELETE FROM receita WHERE id = ?', (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar receita pelo ID: {e}")

    def delete_rotina_id(self, id):
        try:
            self.cursor.execute('''DELETE FROM rotina WHERE id=?''', (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar rotina pelo ID: {e}")

    def search_record_login(self, record_id):
        try:
            query = 'SELECT * FROM login WHERE id=?'
            self.cursor.execute(query, (record_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar registro login pelo ID: {e}")
            return None

    def search_name_login(self, name):
        try:
            query = 'SELECT * FROM login WHERE usuario=?'
            self.cursor.execute(query, (name,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar login pelo nome: {e}")
            return None

    def search_name_receita(self, name):
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar receita pelo nome: {e}")
            return None

    def get_all_records_login(self):
        try:
            query = 'SELECT * FROM login'
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar todos os registros de login: {e}")
            return []

    def get_all_records_receita(self):
        try:
            self.cursor.execute('SELECT * FROM receita')
            registros = self.cursor.fetchall()
            return registros
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar todos os registros de receita: {e}")
            return []

    def get_all_records_rotina(self):
        try:
            self.cursor.execute('''SELECT * FROM rotina''')
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar todos os registros de rotina: {e}")
            return []

    def search_name_rotina(self, nome):
        try:
            self.cursor.execute('''SELECT * FROM rotina WHERE programa = ?''', (nome,))
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar rotina pelo nome: {e}")
            return []

    def search_fim_rotina(self):
        try:
            self.cursor.execute('''SELECT * FROM rotina WHERE fim_rotina = ?''', (0,))
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar rotina com fim_rotina igual a 0: {e}")
            return []

    def stop(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logging.error(f"Erro ao fechar a conexão com o banco de dados: {e}")

    def __del__(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logging.error(f"Erro ao fechar a conexão com o banco de dados no __del__: {e}")

if __name__ == "__main__":
    db = DataBase()
