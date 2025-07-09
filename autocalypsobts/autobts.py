import os
import sys
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CaptureWorker(QThread):
    output_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.errorOccurred.connect(self.handle_error)
        self.process.finished.connect(self.process_finished)
    
    def run(self):
        self.process.start('sudo', ['tshark', '-i', 'lo', '-l', '-Y', 'gsm_sms', '-T', 'fields', '-e', 'gsm_sms.tp-oa', '-e', 'gsm_sms.tp-da', '-e', 'gsm_sms.sms_text'])
        if self.process.waitForStarted():
            print("tshark process started")
        else:
            print("Failed to start tshark process")
        self.exec_()  # Run the event loop to handle signals
    
    def read_output(self):
        print("Reading output from tshark")
        while self.process.canReadLine():
            line = self.process.readLine().data().decode().strip()
            if line:
                self.output_signal.emit(line)
    
    def handle_error(self, error):
        print(f"Process error: {error}")
    
    def process_finished(self, exit_code, exit_status):
        print(f"Process finished with code {exit_code}, status {exit_status}")
    
    def stop(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            self.process.waitForFinished(5000)  # Wait up to 5 seconds
            if self.process.state() != QProcess.NotRunning:
                self.process.kill()
        self.quit()  # Stop the event loop

class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    def __init__(self, text, color="#2196F3", hover_color="#1976D2", text_color="#FFFFFF"):
        super().__init__(text)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.setFixedHeight(45)
        self.setMinimumWidth(120)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
        
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.color}, stop: 1 {self.darken_color(self.color, 0.8)});
                color: {self.text_color};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.hover_color}, stop: 1 {self.darken_color(self.hover_color, 0.8)});
                transform: scale(1.02);
            }}
            QPushButton:pressed {{
                background: {self.darken_color(self.hover_color, 0.7)};
            }}
        """)
    
    def darken_color(self, color, factor):
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

class SMPPSpamDialog(QDialog):
    def __init__(self, parent=None, theme='dark'):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("SMPP Bradbury Configuration")
        self.setModal(False)  # Make dialog non-modal
        layout = QFormLayout(self)
        
        self.sender_edit = QLineEdit()
        self.message_edit = QLineEdit()
        
        layout.addRow("Sender:", self.sender_edit)
        layout.addRow("Message:", self.message_edit)
        
        self.send_button = ModernButton("Send", "#FFD700", "#FFA000", "#000000")
        self.send_button.clicked.connect(self.accept)
        layout.addRow(self.send_button)
        
        self.apply_theme()
    
    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background: #1a1a2e;
                    color: #ffffff;
                }
                QLineEdit {
                    background: #2a2a3e;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #FFFFFF;
                    color: #000000;
                }
                QLineEdit {
                    background: #F0F0F0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #000000;
                }
            """)

class USSDSpamDialog(QDialog):
    def __init__(self, parent=None, theme='dark'):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("USSD Spam Configuration")
        self.setModal(False)  # Make dialog non-modal
        layout = QFormLayout(self)
        
        self.message_edit = QLineEdit()
        
        layout.addRow("Message:", self.message_edit)
        
        self.send_button = ModernButton("Send", "#FFD700", "#FFA000", "#000000")
        self.send_button.clicked.connect(self.accept)
        layout.addRow(self.send_button)
        
        self.apply_theme()
    
    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background: #1a1a2e;
                    color: #ffffff;
                }
                QLineEdit {
                    background: #2a2a3e;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #FFFFFF;
                    color: #000000;
                }
                QLineEdit {
                    background: #F0F0F0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #000000;
                }
            """)

class SMSDDOSDialog(QDialog):
    def __init__(self, parent=None, theme='dark'):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("SMS DDOS Configuration")
        self.setModal(False)  # Make dialog non-modal
        layout = QFormLayout(self)
        
        self.number_edit = QLineEdit()
        self.count_edit = QLineEdit()
        self.message_edit = QLineEdit()
        
        layout.addRow("Target Number:", self.number_edit)
        layout.addRow("Message Count:", self.count_edit)
        layout.addRow("Message Content:", self.message_edit)
        
        self.start_button = ModernButton("Start DDOS", "#FF4500", "#E64A19", "#FFFFFF")
        self.start_button.clicked.connect(self.accept)
        layout.addRow(self.start_button)
        
        self.apply_theme()
    
    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background: #1a1a2e;
                    color: #ffffff;
                }
                QLineEdit {
                    background: #2a2a3e;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #FFFFFF;
                    color: #000000;
                }
                QLineEdit {
                    background: #F0F0F0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #000000;
                }
            """)

class SpoofMSISDNDialog(QDialog):
    def __init__(self, parent=None, theme='dark'):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("Spoof MSISDN")
        self.setModal(False)  # Make dialog non-modal
        layout = QFormLayout(self)
        
        self.id_edit = QLineEdit()
        self.number_edit = QLineEdit()
        
        layout.addRow("Target ID:", self.id_edit)
        layout.addRow("Spoof Number:", self.number_edit)
        
        self.change_button = ModernButton("Change MSISDN", "#FFD700", "#FFA000", "#000000")
        self.change_button.clicked.connect(self.accept)
        layout.addRow(self.change_button)
        
        self.apply_theme()
    
    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background: #1a1a2e;
                    color: #ffffff;
                }
                QLineEdit {
                    background: #2a2a3e;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background: #FFFFFF;
                    color: #000000;
                }
                QLineEdit {
                    background: #F0F0F0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #000000;
                }
            """)

class CalypsoBTSGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto CalypsoBTS.V2 - Professional Edition Powered By Mini0com Alrayane")
        self.setFixedSize(900, 500)  # Increased width to 900
        self.setWindowIcon(QIcon('ico.png'))
        self.current_theme = 'dark'
        self.help_text = None  # Reference to help_text QLabel
        self.capture_worker = None  # Initialize capture worker
        
        self.apply_dark_theme()
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("CalypsoBTS.V2 Powered By Mini0com")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
        """)
        layout.addWidget(title)
        
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        bts_tab = self.create_bts_tab()
        tab_widget.addTab(bts_tab, "BTS Control")
        
        sub_tab = self.create_subscribers_tab()
        tab_widget.addTab(sub_tab, "Subscribers")
        
        sms_capture_tab = self.create_sms_capture_tab()
        tab_widget.addTab(sms_capture_tab, "SMS Capture")
        
        help_tab = self.create_help_tab()
        tab_widget.addTab(help_tab, "Help")
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a1a2e, stop: 1 #16213e);
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.05);
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                padding: 14px 30px;
                margin-right: 4px;
                min-width: 120px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4CAF50, stop: 1 #388E3C);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.2);
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        if self.help_text:
            self.help_text.setStyleSheet("""
                QLabel {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 20px;
                    line-height: 1.6;
                    color: #ffffff;
                }
            """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                background: #F5F5F5;
            }
            QTabBar::tab {
                background: #E0E0E0;
                color: #000000;
                padding: 14px 30px;
                margin-right: 4px;
                min-width: 120px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4CAF50, stop: 1 #388E3C);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #D0D0D0;
            }
            QLabel {
                color: #000000;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        if self.help_text:
            self.help_text.setStyleSheet("""
                QLabel {
                    background: #F0F0F0;
                    border-radius: 10px;
                    padding: 20px;
                    line-height: 1.6;
                    color: #000000;
                }
            """)
    
    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.apply_light_theme()
            self.current_theme = 'light'
        else:
            self.apply_dark_theme()
            self.current_theme = 'dark'
    
    def create_bts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        config_group = QGroupBox("Configuration Files")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        config_layout = QHBoxLayout(config_group)
        
        btn_openbsc = ModernButton("OpenBSC.cfg", "#4CAF50", "#388E3C")
        btn_openbsc.clicked.connect(self.click_button5)
        btn_osmobts = ModernButton("OsmoBTS.cfg", "#4CAF50", "#388E3C")
        btn_osmobts.clicked.connect(self.click_button6)
        
        config_layout.addWidget(btn_openbsc)
        config_layout.addWidget(btn_osmobts)
        layout.addWidget(config_group)
        
        trx_group = QGroupBox("TRX Controls")
        trx_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #FF9800;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        trx_layout = QGridLayout(trx_group)
        
        trx1_layout = QHBoxLayout()
        btn_trx1 = ModernButton("TRX1", "#9E9E9E", "#757575", "#000000")
        btn_trx1.clicked.connect(self.click_button13)
        btn_trx1_config = ModernButton("⚙", "#40E0D0", "#00BCD4")
        btn_trx1_config.setFixedWidth(40)
        btn_trx1_config.clicked.connect(self.click_button12)
        trx1_layout.addWidget(btn_trx1)
        trx1_layout.addWidget(btn_trx1_config)
        
        trx2_layout = QHBoxLayout()
        btn_trx2 = ModernButton("TRX2", "#9E9E9E", "#757575", "#000000")
        btn_trx2.clicked.connect(self.click_button)
        btn_trx2_config = ModernButton("⚙", "#9E9E9E", "#757575")
        btn_trx2_config.setFixedWidth(40)
        btn_trx2_config.clicked.connect(self.click_button14)
        trx2_layout.addWidget(btn_trx2)
        trx2_layout.addWidget(btn_trx2_config)
        
        clock_layout = QHBoxLayout()
        btn_clock = ModernButton("Clock", "#00BCD4", "#0097A7")
        btn_clock.clicked.connect(self.click_button2)
        btn_clock_config = ModernButton("⚙", "#40E0D0", "#00BCD4")
        btn_clock_config.setFixedWidth(40)
        btn_clock_config.clicked.connect(self.click_button11)
        clock_layout.addWidget(btn_clock)
        clock_layout.addWidget(btn_clock_config)
        
        trx_widget1 = QWidget()
        trx_widget1.setLayout(trx1_layout)
        trx_widget2 = QWidget()
        trx_widget2.setLayout(trx2_layout)
        clock_widget = QWidget()
        clock_widget.setLayout(clock_layout)
        
        trx_layout.addWidget(trx_widget1, 0, 0)
        trx_layout.addWidget(trx_widget2, 0, 1)
        trx_layout.addWidget(clock_widget, 0, 2)
        
        layout.addWidget(trx_group)
        
        system_group = QGroupBox("System Controls")
        system_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #F44336;
                border: 2px solid #F44336;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        system_layout = QHBoxLayout(system_group)
        
        btn_db = ModernButton("DB", "#9E9E9E", "#757575", "#000000")
        btn_db.clicked.connect(self.click_button3)
        btn_bts = ModernButton("START BTS", "#F44336", "#D32F2F")
        btn_bts.clicked.connect(self.click_button4)
        
        system_layout.addWidget(btn_db)
        system_layout.addWidget(btn_bts)
        layout.addWidget(system_group)
        
        layout.addStretch()
        return widget
    
    def create_subscribers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        sub_group = QGroupBox("Subscriber Management")
        sub_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #9C27B0;
                border: 2px solid #9C27B0;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        sub_layout = QGridLayout(sub_group)
        
        btn_subscribers = ModernButton("View Subscribers", "#E066FF", "#D81B60")
        btn_subscribers.clicked.connect(self.click_button7)
        
        btn_spoof_msisdn = ModernButton("Spoof MSISDN", "#E066FF", "#D81B60")
        btn_spoof_msisdn.clicked.connect(self.click_button_spoof_msisdn)
        
        btn_remove_db = ModernButton("Remove Database", "#424242", "#212121", "#FF5722")
        btn_remove_db.clicked.connect(self.click_button8)
        
        sub_layout.addWidget(btn_subscribers, 0, 0)
        sub_layout.addWidget(btn_spoof_msisdn, 0, 1)
        sub_layout.addWidget(btn_remove_db, 0, 2)
        
        layout.addWidget(sub_group)
        
        comm_group = QGroupBox("Communication Tools")
        comm_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #FFC107;
                border: 2px solid #FFC107;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        comm_layout = QGridLayout(comm_group)
        
        btn_test_sms = ModernButton("Send Test SMS", "#FFD700", "#FFA000", "#000000")
        btn_test_sms.clicked.connect(self.click_button9)
        btn_smpp_spam = ModernButton("SMPP SPAM", "#FFD700", "#FFA000", "#000000")
        btn_smpp_spam.clicked.connect(self.click_button15)
        btn_ussd_spam = ModernButton("USSD SPAM", "#FFD700", "#FFA000", "#000000")
        btn_ussd_spam.clicked.connect(self.click_button16)
        btn_sms_ddos = ModernButton("SMS DDOS", "#FF4500", "#E64A19", "#FFFFFF")
        btn_sms_ddos.clicked.connect(self.click_button17)
        btn_console = ModernButton("OpenBSC Console", "#4CAF50", "#388E3C")
        btn_console.clicked.connect(self.click_button10)
        btn_wireshark = ModernButton("Run Wireshark", "#2196F3", "#1976D2", "#FFFFFF")
        btn_wireshark.clicked.connect(self.click_button18)
        
        comm_layout.addWidget(btn_test_sms, 0, 0)
        comm_layout.addWidget(btn_smpp_spam, 0, 1)
        comm_layout.addWidget(btn_ussd_spam, 1, 0)
        comm_layout.addWidget(btn_sms_ddos, 1, 1)
        comm_layout.addWidget(btn_console, 2, 0)
        comm_layout.addWidget(btn_wireshark, 2, 1)
        
        layout.addWidget(comm_group)
        layout.addStretch()
        
        return widget
    
    def create_sms_capture_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        button_layout = QHBoxLayout()
        
        self.start_capture_btn = ModernButton("Start Capture SMS", "#4CAF50", "#388E3C", "#FFFFFF")
        self.start_capture_btn.clicked.connect(self.start_capture)
        
        button_layout.addWidget(self.start_capture_btn)
        
        layout.addLayout(button_layout)
        
        self.capture_output = QTextEdit()
        self.capture_output.setReadOnly(True)
        self.capture_output.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                font-family: Monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.capture_output)
        
        return widget
    
    def start_capture(self):
        if self.capture_worker is not None and self.capture_worker.isRunning():
            QMessageBox.information(self, "Capture Status", "Capture is already running.")
            return
        
        self.capture_worker = CaptureWorker()
        self.capture_worker.output_signal.connect(self.update_capture_output)
        self.capture_worker.start()
        
    def update_capture_output(self, text):
        self.capture_output.append(text)
    
    def closeEvent(self, event):
        if self.capture_worker is not None and self.capture_worker.isRunning():
            self.capture_worker.stop()
            self.capture_worker.wait()
        super().closeEvent(event)
    
    def create_help_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.help_text = QLabel("""
<h2 style='color: #4CAF50; text-align: center;'>CalypsoBTS Control Center</h2>

<h3 style='color: #FF9800;'> Correct Launch Sequence:</h3>
<p style='margin-left: 20px;'>
<strong>1.</strong> TRX1 (or TRX1 + TRX2)<br>
<strong>2.</strong> Clock<br>
<strong>3.</strong> Database<br>
<strong>4.</strong> BTS
</p>

<h3 style='color: #2196F3;'> Communication Features:</h3>
<p style='margin-left: 20px;'>
<strong>Test SMS:</strong> Sends test SMS from number 111 to all subscribers<br>
<strong>SMPP SPAM:</strong> Send SMPP spam messages to all subscribers<br>
<strong>USSD SPAM:</strong> Send USSD spam messages to all subscribers<br>
<strong>SMS DDOS:</strong> Launch SMS DDOS attack<br>
<strong>Subscribers:</strong> Shows ID, IMSI, MSISDN, IMEI, TMSI, Timestamp, mcc-mnc-type,<br>
<strong>Console:</strong> Access OpenBSC command interface
</p>

<h3 style='color: #9C27B0;'>⚙️ Configuration:</h3>
<p style='margin-left: 20px;'>
Edit OpenBSC and OsmoBTS configuration files directly<br>
Configure TRX settings with dedicated config buttons
</p>

<h3 style='color: #F44336;'>⚠️ Safety Notes:</h3>
<p style='margin-left: 20px;'>
Always follow the correct startup sequence<br>
Use "Remove Database" with caution - this action is irreversible
</p>

<hr style='border: 1px solid #3d3d3d; margin: 20px 0;'>

<p style='text-align: center; color: #757575; font-style: italic;'>
Professional CalypsoBTS.V2 Interface<br>
Enhanced with PyQt5 by Mini0com
</p>
        """)
        
        self.help_text.setWordWrap(True)
        self.help_text.setTextFormat(Qt.RichText)
        self.help_text.setAlignment(Qt.AlignTop)
        self.help_text.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 20px;
                line-height: 1.6;
                color: #ffffff;
            }
        """ if self.current_theme == 'dark' else """
            QLabel {
                background: #F0F0F0;
                border-radius: 10px;
                padding: 20px;
                line-height: 1.6;
                color: #000000;
            }
        """)
        
        scroll = QScrollArea()
        scroll.setWidget(self.help_text)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(scroll)
        
        theme_button = ModernButton("Switch Theme", "#2196F3", "#1976D2")
        theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_button)
        
        return widget
    
    def get_subscribers(self):
        stream = os.popen('sudo python3 /root/.osmocom/sub.py')
        return stream.read()
    
    def click_button(self):
        os.popen('sudo gnome-terminal -- ./trx2.sh')
    
    def click_button2(self):
        os.popen('sudo gnome-terminal -- ./transceiver.sh')
    
    def click_button3(self):
        os.popen('sudo gnome-terminal -- ./nitb.sh')
    
    def click_button4(self):
        os.popen('sudo gnome-terminal -- ./osmobts.sh')
    
    def click_button5(self):
        os.popen('sudo featherpad /root/.osmocom/open-bsc.cfg')
    
    def click_button6(self):
        os.popen('sudo featherpad /root/.osmocom/osmo-bts.cfg')
    
    def click_button7(self):
        stream = os.popen('sudo python3 /root/.osmocom/sub.py')
        out = stream.read()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('SUBSCRIBERS')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(f"<pre>{out}</pre>")
        msg_box.setMinimumWidth(700)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-family: Monospace;
                font-size: 12px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
                font-family: Monospace;
                font-size: 12px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
    
    def click_button8(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Confirm Database Removal')
        msg_box.setText('Are you sure you want to remove the database?\nThis action cannot be undone!')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.buttonClicked.connect(lambda button: self.handle_remove_db(button, msg_box))
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
    
    def handle_remove_db(self, button, msg_box):
        if button.text() == "&Yes":
            stream = os.popen('sudo rm /root/.osmocom/hlr.sqlite3 >/dev/null 2>&1 & echo "REMOVED"')
            out = stream.read()
            confirm_box = QMessageBox(self)
            confirm_box.setWindowTitle('Database Removed')
            confirm_box.setText(out)
            confirm_box.setStyleSheet("""
                QMessageBox {
                    background: #1a1a2e;
                    color: #ffffff;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                }
                QMessageBox QPushButton {
                    background: #4CAF50;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QMessageBox QPushButton:hover {
                    background: #388E3C;
                }
            """ if self.current_theme == 'dark' else """
                QMessageBox {
                    background: #FFFFFF;
                    color: #000000;
                }
                QMessageBox QLabel {
                    color: #000000;
                }
                QMessageBox QPushButton {
                    background: #4CAF50;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QMessageBox QPushButton:hover {
                    background: #388E3C;
                }
            """)
            confirm_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
            confirm_box.show()  # Use show() instead of exec_() for non-modal behavior
        msg_box.close()
    
    def click_button9(self):
        stream = os.popen('cd /root/.osmocom/ && sudo python3 smS.py 111 SMStestSMS & echo "SMS SENT!"')
        out = stream.read()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('SMS Status')
        msg_box.setText(out)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
    
    def click_button10(self):
        os.popen('sudo gnome-terminal -- ./console.sh')
    
    def click_button11(self):
        os.popen('sudo featherpad transceiver.sh')
    
    def click_button12(self):
        os.popen('sudo featherpad trx.sh')
    
    def click_button13(self):
        os.popen('sudo gnome-terminal -- ./trx.sh')
    
    def click_button14(self):
        os.popen('sudo featherpad trx2.sh')
    
    def click_button15(self):
        dialog = SMPPSpamDialog(self, self.current_theme)
        dialog.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.accepted.connect(lambda: self.handle_smpp_spam(dialog))
    
    def handle_smpp_spam(self, dialog):
        sender = dialog.sender_edit.text()
        message = dialog.message_edit.text()
        cmd = f'cd /root/.osmocom/ && sudo python3 smpp.py {sender} "{message}"'
        stream = os.popen(cmd)
        out = stream.read()
        subs = self.get_subscribers()
        report = f"SMPP Report:\nSubscribers:\n{subs}\nStatus:\n{out}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('SMPP Delivery Report')
        msg_box.setText(report)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.close()
    
    def click_button16(self):
        dialog = USSDSpamDialog(self, self.current_theme)
        dialog.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.accepted.connect(lambda: self.handle_ussd_spam(dialog))
    
    def handle_ussd_spam(self, dialog):
        message = dialog.message_edit.text()
        subs = self.get_subscribers()
        cmd = f'cd /root/.osmocom/ && sudo python3 ussd.py 1 "{message}"'
        stream = os.popen(cmd)
        out = stream.read()
        report = f"USSD Report:\nSubscribers:\n{subs}\nStatus:\n{out}"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('USSD Delivery Report')
        msg_box.setText(report)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.close()
    
    def click_button17(self):
        dialog = SMSDDOSDialog(self, self.current_theme)
        dialog.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.accepted.connect(lambda: self.handle_sms_ddos(dialog))
    
    def handle_sms_ddos(self, dialog):
        number = dialog.number_edit.text()
        count = dialog.count_edit.text()
        message = dialog.message_edit.text()
        cmd = f'cd /root/.osmocom/ && sudo python3 sms_attack.py {number} {count} "{message}"'
        os.system(f'gnome-terminal -- bash -c "{cmd}; exec bash"')
        dialog.close()
    
    def click_button18(self):
        subprocess.Popen(['sudo','wireshark', '-i', 'lo', '-k', '-f', '', '-Y', 'gsm_ipa'])
    
    def click_button_spoof_msisdn(self):
        dialog = SpoofMSISDNDialog(self, self.current_theme)
        dialog.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.accepted.connect(lambda: self.handle_spoof_msisdn(dialog))
    
    def handle_spoof_msisdn(self, dialog):
        target_id = dialog.id_edit.text()
        spoof_number = dialog.number_edit.text()
        cmd = f'cd /root/.osmocom && sudo python3 msisdn_changer.py {target_id} {spoof_number}'
        stream = os.popen(cmd)
        out = stream.read()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('MSISDN Change Status')
        msg_box.setText(out)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """ if self.current_theme == 'dark' else """
            QMessageBox {
                background: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background: #4CAF50;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QMessageBox QPushButton:hover {
                background: #388E3C;
            }
        """)
        msg_box.setWindowModality(Qt.NonModal)  # Make message box non-modal
        msg_box.show()  # Use show() instead of exec_() for non-modal behavior
        dialog.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalypsoBTSGUI()
    window.show()
    sys.exit(app.exec_())
