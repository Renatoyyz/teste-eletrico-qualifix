import sqlite3
import json

# Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect('dados.db')

# Função para criar a tabela se não existir
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados (
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
    conn.commit()
    conn.close()

# Função para inserir um novo registro
def inserir_registro(nome_programa, url_img_esquerdo, url_img_direito,
                     coord_eletrodo_esquerdo, coord_eletrodo_direito,
                     condutividade_esquerdo, condutividade_direito,
                     isolacao_esquerdo, isolacao_direito):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dados (nome_programa, url_img_esquerdo, url_img_direito,
                          coord_eletrodo_esquerdo, coord_eletrodo_direito,
                          condutividade_esquerdo, condutividade_direito,
                          isolacao_esquerdo, isolacao_direito)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome_programa, url_img_esquerdo, url_img_direito,
          json.dumps(coord_eletrodo_esquerdo), json.dumps(coord_eletrodo_direito),
          json.dumps(condutividade_esquerdo), json.dumps(condutividade_direito),
          json.dumps(isolacao_esquerdo), json.dumps(isolacao_direito)))
    conn.commit()
    conn.close()

# Função para selecionar um registro pelo ID e retornar variáveis separadas
def selecionar_registro_por_id(registro_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dados WHERE id = ?', (registro_id,))
    registro = cursor.fetchone()
    conn.close()
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
# Função para selecionar todos os registros
def selecionar_registros():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dados')
    registros = cursor.fetchall()
    conn.close()
    return registros

# Criar a tabela se não existir
criar_tabela()

nome_programa = "Renato"
url_img_esquerdo="url/img_esquerdo.png"
url_img_direito="url/img_direito.png" 

coord_eletrodo_esquerdo = [ None for _ in range(10) ]
coord_eletrodo_direito = [ None for _ in range(10) ]

coord_eletrodo_esquerdo[0]=[11,450]
coord_eletrodo_esquerdo[1]=[23,134]
coord_eletrodo_esquerdo[2]=[131,232]

coord_eletrodo_direito[0]=[11,450]
coord_eletrodo_direito[1]=[23,134]
coord_eletrodo_direito[2]=[131,232]

condutividade_esquerdo = {
    "ligacao1":[1,[1,34,0],0, "renato"],
    "ligacao2":[2,[1,56,0],0, "oliveira"],
    "ligacao3":[3,[1,23,0],0, "katia"],
    "ligacao4":[4,[765,0,0],0, "leo_rafa"],
    "ligacao5":[0,[0,0,0],0, ""],
    "ligacao6":[0,[0,0,0],0, ""],
    "ligacao7":[0,[0,0,0],0, ""],
    "ligacao8":[0,[0,0,0],0, ""],
    'foi_testado':False
}
isolacao_esquerdo = {
    "ligacao1":[1,2,"renato-oliviera"],
    "ligacao2":[1,3,"renato-katia"],
    "ligacao3":[1,4,"renato-leo_rafa"],
    "ligacao4":[0,0,""],
    "ligacao5":[0,0,""],
    "ligacao6":[0,0,""],
    "ligacao7":[0,0,""],
    "ligacao8":[0,0,""],
    "ligacao9":[0,0,""],
    "ligacao10":[0,0,""],
    "ligacao11":[0,0,""],
    "ligacao12":[0,0,""],
    "ligacao13":[0,0,""],
    "ligacao14":[0,0,""],
    "ligacao15":[0,0,""],
    "ligacao16":[0,0,""],
    "foi_testado": False
}

condutividade_direito = {
    "ligacao1":[1,[1,110,0],0, "terra"],
    "ligacao2":[2,[1,567,12],0, "pisca"],
    "ligacao3":[3,[1,11,10],0, "re"],
    "ligacao4":[4,[2,0,10],0, "posicao"],
    "ligacao5":[0,[0,0,0],0, ""],
    "ligacao6":[0,[0,0,0],0, ""],
    "ligacao7":[0,[0,0,0],0, ""],
    "ligacao8":[0,[0,0,0],0, ""],
    "foi_testado": False
}
isolacao_direito = {
    "ligacao1":[1,2,"terra-pisca"],
    "ligacao2":[1,3,"terra-re"],
    "ligacao3":[1,4,"terra-posicao"],
    "ligacao4":[0,0,""],
    "ligacao5":[0,0,""],
    "ligacao6":[0,0,""],
    "ligacao7":[0,0,""],
    "ligacao8":[0,0,""],
    "ligacao9":[0,0,""],
    "ligacao10":[0,0,""],
    "ligacao11":[0,0,""],
    "ligacao12":[0,0,""],
    "ligacao13":[0,0,""],
    "ligacao14":[0,0,""],
    "ligacao15":[0,0,""],
    "ligacao16":[0,0,""],
    "foi_testado": False
}

# # Exemplo de inserção de um novo registro
# inserir_registro(nome_programa, url_img_esquerdo, url_img_direito,
#                  coord_eletrodo_esquerdo, coord_eletrodo_direito,
#                  condutividade_esquerdo, condutividade_direito,
#                  isolacao_esquerdo, isolacao_direito)

# # Exemplo de seleção de um registro pelo ID
# registro_por_id = selecionar_registro_por_id(1)
# if registro_por_id:
#     (id, nome_programa, url_img_esquerdo, url_img_direito,
#      coord_eletrodo_esquerdo, coord_eletrodo_direito,
#      condutividade_esquerdo, condutividade_direito,
#      isolacao_esquerdo, isolacao_direito) = registro_por_id
#     print("ID:", id)
#     print("Nome do Programa:", nome_programa)
#     print("URL da Imagem Esquerda:", url_img_esquerdo)
#     print("URL da Imagem Direita:", url_img_direito)
#     print("Coordenadas Eletrodo Esquerdo:", coord_eletrodo_esquerdo)
#     print("Coordenadas Eletrodo Direito:", coord_eletrodo_direito)
#     print("Condutividade Esquerda:", condutividade_esquerdo)
#     print("Condutividade Direita:", condutividade_direito)
#     print("Isolacao Esquerda:", isolacao_esquerdo)
#     print("Isolacao Direita:", isolacao_direito)
# else:
#     print("Registro não encontrado.")

# Exemplo de seleção de todos os registros
todos_os_registros = selecionar_registros()
print("Todos os registros:")
for registro in todos_os_registros:
    print(registro[1])
    print( json.loads(registro[6])["foi_testado"])
    print( json.loads(registro[7])["foi_testado"])
    print( json.loads(registro[8])["foi_testado"])
    print( json.loads(registro[9])["foi_testado"])
