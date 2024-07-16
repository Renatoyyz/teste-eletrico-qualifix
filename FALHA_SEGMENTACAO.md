
# Solução de Falha de Segmentação com PyQt5 no Raspberry Pi 4

## Introdução

Este documento descreve a solução para resolver falhas de segmentação (segmentation fault) ao usar PyQt5 no Raspberry Pi 4, especialmente ao lidar com threads. A abordagem envolve o uso de `QThread`, `pyqtSignal` e `pyqtSlot` para gerenciar tarefas de forma segura, garantindo que todas as interações com a interface gráfica sejam feitas a partir do thread principal do Qt.

## Problema

Ao desenvolver uma aplicação PyQt5 no Raspberry Pi 4 que utiliza threads para atualizar a interface gráfica e executar operações complexas, é comum encontrar falhas de segmentação. Essas falhas ocorrem porque o PyQt5 não é totalmente thread-safe, especialmente quando se tenta atualizar a UI a partir de threads diferentes do thread principal.

## Solução

Para resolver o problema de falha de segmentação, seguimos as etapas abaixo:

1. **Utilização de `QThread` para Gerenciamento de Threads**:
   - `QThread` permite a criação de threads personalizados para executar operações em segundo plano.
   - Utilizamos sinais (`pyqtSignal`) e slots (`pyqtSlot`) para comunicar-se de maneira segura entre threads.

2. **Atualização Segura da Interface Gráfica**:
   - Para garantir que a UI seja atualizada a partir do thread principal, utilizamos o método `QMetaObject.invokeMethod` com `Qt.QueuedConnection`. Esse método enfileira a chamada de um método para ser executado de forma segura no thread principal.

## Implementação

### Classe Atualizador

A classe `Atualizador` é responsável por emitir sinais para atualizar a interface com a data e hora atuais.

```python
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Q_ARG, Qt
from datetime import datetime

class Atualizador(QThread):
    sinal_atualizar = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        while self._running:
            try:
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                QMetaObject.invokeMethod(self, "emit_sinal_atualizar", Qt.QueuedConnection, Q_ARG(str, data_hora))
                self.sleep(1)
            except Exception as e:
                print(f"Erro na Thread Atualizador: {e}")
                self._running = False

    @pyqtSlot(str)
    def emit_sinal_atualizar(self, data_hora):
        self.sinal_atualizar.emit(data_hora)

    def parar(self):
        self._running = False
```

### Classe ExecutaRotinaThread

A classe `ExecutaRotinaThread` executa operações complexas e emite sinais ao finalizar.

```python
class ExecutaRotinaThread(QThread):
    sinal_execucao = pyqtSignal(list, list, list, list)

    def __init__(self, operacao):
        super().__init__()
        self.operacao = operacao
        self._running = True

    def run(self):
        while self._running:
            try:
                # Operações complexas aqui...
                result_condu_e = []
                result_condu_d = []
                result_iso_e = []
                result_iso_d = []

                # Código de execução da rotina
                # ...

                QMetaObject.invokeMethod(self, "emit_sinal_execucao", Qt.QueuedConnection, 
                                         Q_ARG(list, result_condu_e), Q_ARG(list, result_iso_e), 
                                         Q_ARG(list, result_condu_d), Q_ARG(list, result_iso_d))
                self.sleep(1)
            except Exception as e:
                print(f"Erro na Thread ExecutaRotina: {e}")
                self._running = False

    @pyqtSlot(list, list, list, list)
    def emit_sinal_execucao(self, result_condu_e, result_iso_e, result_condu_d, result_iso_d):
        self.sinal_execucao.emit(result_condu_e, result_iso_e, result_condu_d, result_iso_d)

    def parar(self):
        self._running = False
```

### Classe TelaExecucao

A classe `TelaExecucao` gerencia a interface gráfica e as threads.

```python
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QCoreApplication

class TelaExecucao(QDialog):
    def __init__(self, dado=None, io=None, db=None, rotina=None, nome_prog=None, continuacao=None, db_rotina=None):
        super().__init__()

        self.inicializa_variaveis(dado, io, db, rotina, nome_prog, continuacao, db_rotina)
        self.inicializa_ui()
        self.inicializa_threads()

    def inicializa_variaveis(self, dado, io, db, rotina, nome_prog, continuacao, db_rotina):
        self.dado = dado
        self.io = io
        self.database = db
        self.rotina = rotina
        self.nome_prog = nome_prog
        self.continuacao = continuacao
        self.db_rotina = db_rotina

    def inicializa_ui(self):
        self.ui = Ui_TelaExecucao()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowState.WindowMaximized)

    def inicializa_threads(self):
        self.atualizador = Atualizador()
        self.atualizador.sinal_atualizar.connect(self.atualiza_valor)
        self.atualizador.start()

        self.execucao = ExecutaRotinaThread(self)
        self.execucao.sinal_execucao.connect(self.execucao_finalizada)
        self.execucao.start()

    @pyqtSlot(str)
    def atualiza_valor(self, data_hora):
        # Atualizar interface com data_hora
        pass

    @pyqtSlot(list, list, list, list)
    def execucao_finalizada(self, cond_e, iso_e, cond_d, iso_d):
        # Atualizar interface com resultados dos testes
        pass

    def parar_threads(self):
        self.atualizador.parar()
        self.execucao.parar()
```

## Considerações Finais

Esta abordagem garante que todas as interações com a interface gráfica sejam feitas a partir do thread principal do Qt, evitando falhas de segmentação. Utilizando `QThread`, `pyqtSignal` e `pyqtSlot`, gerenciamos eficientemente as threads e a comunicação entre elas, mantendo a aplicação responsiva e estável.

Caso tenha alguma dúvida ou precise de suporte adicional, sinta-se à vontade para entrar em contato.
