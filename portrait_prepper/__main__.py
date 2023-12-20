# make contorller
# make 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = PictureEditor()
    editor.show()
    sys.exit(app.exec_())