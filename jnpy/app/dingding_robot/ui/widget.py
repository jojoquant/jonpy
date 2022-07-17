from vnpy.trader.ui import QtWidgets
from vnpy.trader.engine import MainEngine, EventEngine
from vnpy.trader.utility import save_json

from ..engine import APP_NAME, RobotEngine, WEBHOOK, TEST_CONTENT
from .ui_widget import Ui_widget


class RobotWidget(QtWidgets.QWidget):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.engine: RobotEngine = main_engine.get_engine(APP_NAME)
        self.ui = Ui_widget()
        self.ui.setupUi(self)

        self.ui.plainTextEdit.setPlainText(self.engine.webhook)

        self.ui.pushButton.clicked.connect(self.update_dingding_setting)
        self.ui.pushButton_3.clicked.connect(self.send_text)
        self.ui.pushButton_5.clicked.connect(self.send_markdown)
        self.ui.pushButton_2.clicked.connect(self.close)

    def update_dingding_setting(self):
        self.engine.webhook = self.ui.plainTextEdit.toPlainText()
        self.engine.test_content = self.ui.plainTextEdit_2.toPlainText()

        save_json(
            self.engine.robot_setting_filename,
            data={
                WEBHOOK: self.engine.webhook,
                TEST_CONTENT: self.engine.test_content
            }
        )
        self.close()

    def send_text(self):
        self.engine.webhook = self.ui.plainTextEdit.toPlainText()
        self.engine.test_content = self.ui.plainTextEdit_2.toPlainText()
        self.engine.send_text(content=self.engine.test_content)

    def send_markdown(self):
        self.engine.webhook = self.ui.plainTextEdit.toPlainText()
        self.engine.test_content = self.ui.plainTextEdit_2.toPlainText()
        self.engine.send_markdown(title="Dingding Robot Test", content=self.engine.test_content)
