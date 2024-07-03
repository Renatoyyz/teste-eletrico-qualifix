import logging

# Configuração básica
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Criando um handler para escrever logs em um arquivo
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.WARNING)  # Apenas logs de WARNING e acima serão escritos no arquivo

# Criando um formatador e adicionando-o ao handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Adicionando o handler ao logger
logger = logging.getLogger()
logger.addHandler(file_handler)

# Exemplos de mensagens de log
logging.debug('Isso é uma mensagem de debug.')
logging.info('Isso é uma mensagem de informação.')
logging.warning('Isso é uma mensagem de aviso.')
logging.error('Isso é uma mensagem de erro.')
logging.critical('Isso é uma mensagem crítica.')


