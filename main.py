import sys
import requests
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from win import Ui_MainWindow


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()

            total_length = response.headers.get('content-length')

            if total_length is None:
                self.error.emit("Unable to get file size")
                return

            total_length = int(total_length)
            downloaded = 0

            with open(self.save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    file.write(data)
                    done = int(50 * downloaded / total_length)
                    self.progress.emit(done * 2)

            self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_download)

    def start_download(self):
        self.textEdit.append("Start downloading...")

        url = 'https://github.com/ElliotCHEN37/UninstallToolCrack/raw/main/msimg32.dll'

        self.textEdit.append("Please save the patch file to Uninstall Tool installation directory")

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Patch File", "msimg32.dll", "Patch File (msimg32.dll)")

        if not save_path:
            self.textEdit.append("No save location selected, download canceled.")
            return

        self.thread = DownloadThread(url, save_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(self.download_error)
        self.thread.start()

    def update_progress(self, percent):
        self.progressBar.setValue(percent)

    def download_finished(self, save_path):
        self.textEdit.append(f"The file was successfully downloaded and saved to {save_path}")
        self.textEdit.append(
            "To enable the license, plz follow these steps:\n1. Run Uninstall Tool\n2. Enter the key (User name and Serial key can be anything)\n3. Re-start uninstall tool")

    def download_error(self, error_message):
        self.textEdit.append(f"An error occurred while downloading the file: {error_message}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
