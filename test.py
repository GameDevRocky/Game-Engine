from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

view = QWebEngineView()
layout.addWidget(view)
# Load from the running Vite dev server so the preamble / HMR client is served correctly
view.setUrl(QUrl("http://localhost:5173/"))

window.setLayout(layout)
window.show()

app.exec()
