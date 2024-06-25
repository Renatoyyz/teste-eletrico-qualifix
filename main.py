import sys
from PyQt5.QtWidgets import QApplication
from Model.Inicial import TelaInicial
from Controller.IOs import IO_MODBUS

from Controller.Dados import Dado
from Controller.DataBase import DataBase
from Controller.RotinaPrg import RotinaPrg

from img import logo_qualifix

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dado = Dado()
    db = DataBase()
    io = IO_MODBUS()
    rotina = RotinaPrg(dado=dado, io=io, db=db )

    window = TelaInicial(io=io, dado=dado, db=db, rotina=rotina)
    window.show()
    sys.exit([app.exec(),db.stop()])