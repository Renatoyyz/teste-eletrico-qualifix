   def create_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS programas (
                    id INTEGER PRIMARY KEY,
                    nome_programa TEXT,
                    pnp_canal1_ton REAL,
                    pnp_canal1_toff REAL,
                    pnp_canal1_qtd INTEGER,         
                    pnp_canal2_ton REAL,
                    pnp_canal2_toff REAL,
                    pnp_canal2_qtd INTEGER,             
                    pnp_canal3_ton REAL,
                    pnp_canal3_toff REAL,
                    pnp_canal3_qtd INTEGER,         
                    pnp_canal4_pwm REAL,
                    pnp_canal4_periodo_pwm REAL,
                    pnp_canal4_ton REAL,
                    pnp_canal4_toff REAL,
                    pnp_canal4_qtd INTEGER,          
                    pnp_base_tempo REAL,
                    pnp_habilita_desabilita INTEGER, 
                                  
                    npn_canal1_ton REAL,
                    npn_canal1_toff REAL,
                    npn_canal1_qtd INTEGER,
                    npn_canal2_ton REAL,
                    npn_canal2_toff REAL,
                    npn_canal2_qtd INTEGER,
                    npn_canal3_ton REAL,
                    npn_canal3_toff REAL,
                    npn_canal3_qtd INTEGER,
                    npn_canal4_pwm REAL,
                    npn_canal4_periodo_pwm REAL,
                    npn_canal4_ton REAL,
                    npn_canal4_toff REAL,
                    npn_canal4_qtd INTEGER,
                    npn_base_tempo REAL,
                    npn_habilita_desabilita INTEGER,
                                
                    rele_canal1_ton REAL,
                    rele_canal1_toff REAL,
                    rele_canal1_qtd INTEGER,
                    rele_canal2_ton REAL,
                    rele_canal2_toff REAL,
                    rele_canal2_qtd INTEGER,
                    rele_canal3_ton REAL,
                    rele_canal3_toff REAL,
                    rele_canal3_qtd INTEGER,
                    rele_canal4_ton REAL,
                    rele_canal4_toff REAL,
                    rele_canal4_qtd INTEGER,
                    rele_base_tempo REAL,
                    rele_habilita_desabilita INTEGER
                )
            ''')
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar a tabela: {e}")