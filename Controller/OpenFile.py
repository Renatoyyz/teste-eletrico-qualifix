from PyQt5 import QtCore, QtGui, QtWidgets

class OpenFile:
    def __init__(self, dado=None, io=None, db=None):
        self.dado = dado
        self.io = io
        self.db = db
        self.image = None
        self.fileName = None
        self.dir_base_load_img = "/media/desenvolvimento"
        # self.dir_base_load_img = ""

    def load_image_dialog(self, event, size_x, size_y ):
        options = QtWidgets.QFileDialog.Options()
        filters = "Imagens (*.jpeg *.jpg *.png)"
    
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Selecionar Imagem", self.dir_base_load_img, filters, options=options
        )
        if self.fileName:
            self.load_image_url(self.fileName, size_x, size_y)

    def load_image_url(self, image_path, size_x, size_y):
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            # self.image = pixmap.scaled(self.lbImage.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image = pixmap.scaled(size_x, size_y)
            # self.lbImage.setPixmap(pixmap)
        else:
            self.image = None