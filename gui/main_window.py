"""
Main Window - Primary GUI for WiFiNexus Guardian
Cyber Neon Theme with PySide6
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QFrame,
    QScrollArea, QSplitter, QStatusBar, QToolBar,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QFont, QColor, QPalette


class CyberButton(QPushButton):
    """Custom styled button with cyber neon effect"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0A0A0A;
                color: #00D9FF;
                border: 2px solid #00D9FF;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00D9FF;
                color: #0A0A0A;
                border: 2px solid #00D9FF;
            }
            QPushButton:pressed {
                background-color: #0099CC;
            }
        """)


class CyberPanel(QFrame):
    """Custom panel with glass/cyber effect"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("CyberPanel")
        self.setStyleSheet("""
            QFrame#CyberPanel {
                background-color: rgba(10, 10, 10, 0.9);
                border: 1px solid #00D9FF;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                color: #00D9FF;
                font-size: 14px;
                font-weight: bold;
            """)
            layout.addWidget(title_label)


class MainWindow(QMainWindow):
    """Main application window with Cyber Neon theme"""
    
    # Signals
    scan_started = Signal()
    scan_completed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("WiFiNexus Guardian v1.0.0")
        self.setMinimumSize(1200, 800)
        
        # Apply cyber neon theme
        self._apply_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        self._create_header(main_layout)
        
        # Content area with sidebar
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar navigation
        sidebar = self._create_sidebar()
        content_splitter.addWidget(sidebar)
        content_splitter.setStretchFactor(0, 0)
        
        # Main content area
        self.content_stack = QStackedWidget()
        self._create_content_pages()
        content_splitter.addWidget(self.content_stack)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self._create_statusbar()
        
        # System tray
        self._create_system_tray()
        
        # Timers for live updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_live_data)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Show startup warning
        self._show_startup_warning()
    
    def _apply_theme(self):
        """Apply Cyber Neon theme to application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0A0A0A;
            }
            QLabel {
                color: #FFFFFF;
            }
            QStatusBar {
                background-color: #0A0A0A;
                color: #00D9FF;
                border-top: 1px solid #00D9FF;
            }
            QSplitter::handle {
                background-color: #00D9FF;
                width: 2px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
    
    def _create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 217, 255, 0.1);
                border-bottom: 2px solid #00D9FF;
                border-radius: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Title
        title_label = QLabel("📡 WiFiNexus Guardian")
        title_label.setStyleSheet("""
            color: #00D9FF;
            font-size: 28px;
            font-weight: bold;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick stats
        stats_layout = QHBoxLayout()
        
        networks_label = QLabel("🌐 Networks: --")
        networks_label.setStyleSheet("color: #00FF99; font-size: 14px;")
        stats_layout.addWidget(networks_label)
        
        devices_label = QLabel("📱 Devices: --")
        devices_label.setStyleSheet("color: #7A00FF; font-size: 14px;")
        stats_layout.addWidget(devices_label)
        
        header_layout.addLayout(stats_layout)
        
        layout.addWidget(header_frame)
    
    def _create_sidebar(self) -> QWidget:
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 217, 255, 0.05);
                border-right: 1px solid #00D9FF;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", 0),
            ("📶 WiFi Scanner", 1),
            ("🔍 Hidden Networks", 2),
            ("📱 Device Monitor", 3),
            ("📊 Packet Analyzer", 4),
            ("📈 Spectrum", 5),
            ("⚡ Speed Test", 6),
            ("🤖 AI Center", 7),
            ("📋 Logs", 8),
            ("⚙️ Settings", 9)
        ]
        
        for text, index in nav_buttons:
            btn = CyberButton(text)
            btn.clicked.connect(lambda checked, i=index: self.content_stack.setCurrentIndex(i))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return sidebar
    
    def _create_content_pages(self):
        """Create content pages for the stacked widget"""
        
        # Page 1: Dashboard
        dashboard = self._create_dashboard_page()
        self.content_stack.addWidget(dashboard)
        
        # Page 2: WiFi Scanner
        scanner = self._create_scanner_page()
        self.content_stack.addWidget(scanner)
        
        # Page 3-9: Placeholder pages
        for page_name in ["Hidden Networks", "Device Monitor", "Packet Analyzer", 
                          "Spectrum", "Speed Test", "AI Center", "Logs", "Settings"]:
            page = self._create_placeholder_page(page_name)
            self.content_stack.addWidget(page)
    
    def _create_dashboard_page(self) -> QWidget:
        """Create dashboard page"""
        page = QScrollArea()
        page.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Welcome message
        welcome = QLabel("Welcome to WiFiNexus Guardian")
        welcome.setStyleSheet("color: #00D9FF; font-size: 20px; font-weight: bold;")
        layout.addWidget(welcome)
        
        # Stats panels
        stats_layout = QHBoxLayout()
        
        # Network health panel
        health_panel = CyberPanel("Network Health")
        health_label = QLabel("Score: --/100")
        health_label.setStyleSheet("color: #00FF99; font-size: 16px;")
        health_panel.layout().addWidget(health_label)
        stats_layout.addWidget(health_panel)
        
        # Signal strength panel
        signal_panel = CyberPanel("Signal Strength")
        signal_label = QLabel("-- dBm")
        signal_label.setStyleSheet("color: #00D9FF; font-size: 16px;")
        signal_panel.layout().addWidget(signal_label)
        stats_layout.addWidget(signal_panel)
        
        # Connected devices panel
        devices_panel = CyberPanel("Connected Devices")
        devices_label = QLabel("--")
        devices_label.setStyleSheet("color: #7A00FF; font-size: 16px;")
        devices_panel.layout().addWidget(devices_label)
        stats_layout.addWidget(devices_panel)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        scan_btn = CyberButton("🔍 Scan Networks")
        scan_btn.clicked.connect(self._start_scan)
        actions_layout.addWidget(scan_btn)
        
        analyze_btn = CyberButton("🤖 AI Analysis")
        analyze_btn.clicked.connect(self._run_ai_analysis)
        actions_layout.addWidget(analyze_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        page.setWidget(content)
        return page
    
    def _create_scanner_page(self) -> QWidget:
        """Create WiFi scanner page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("WiFi Network Scanner")
        title.setStyleSheet("color: #00D9FF; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Scanner controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = CyberButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_scan)
        controls_layout.addWidget(refresh_btn)
        
        export_btn = CyberButton("📤 Export")
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        
        # Results area (placeholder)
        results_panel = CyberPanel("Scan Results")
        results_label = QLabel("Click Refresh to scan for networks...")
        results_panel.layout().addWidget(results_label)
        layout.addWidget(results_panel)
        
        layout.addStretch()
        return page
    
    def _create_placeholder_page(self, title: str) -> QWidget:
        """Create a placeholder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel(f"{title}\n\nModule under development")
        label.setStyleSheet("color: #888888; font-size: 16px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        
        return page
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Status indicators
        self.status_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_label)
        
        self.statusBar.showMessage("© 2025 Ahmed Mostafa Ibrahim - Finovate | Professional Wireless Intelligence Platform")
    
    def _create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("WiFiNexus Guardian")
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        scan_action = QAction("Quick Scan", self)
        scan_action.triggered.connect(self._start_scan)
        tray_menu.addAction(scan_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _show_startup_warning(self):
        """Show legal warning on startup"""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Legal Notice - WiFiNexus Guardian")
        msg.setText("""
⚠️ AUTHORIZED USE ONLY ⚠️

This software is intended for authorized network analysis and diagnostics only.

By using this software, you confirm that:
• You have authorization to analyze the target networks
• You will not use this tool for illegal activities
• You understand and comply with local laws and regulations

Unauthorized access to computer networks is illegal.
""")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Ok)
        
        response = msg.exec()
        
        if response == QMessageBox.Cancel:
            QApplication.quit()
    
    @Slot()
    def _start_scan(self):
        """Start network scan"""
        self.status_label.setText("Scanning...")
        self.scan_started.emit()
        
        # Simulate scan completion
        QTimer.singleShot(3000, lambda: self.status_label.setText("Scan complete"))
    
    @Slot()
    def _refresh_scan(self):
        """Refresh network scan"""
        self._start_scan()
    
    @Slot()
    def _run_ai_analysis(self):
        """Run AI network analysis"""
        self.status_label.setText("Running AI analysis...")
        
        # Simulate analysis
        QTimer.singleShot(2000, lambda: self.status_label.setText("Analysis complete"))
    
    @Slot()
    def _update_live_data(self):
        """Update live data in UI"""
        # This would be connected to actual data sources
        pass
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop timers
        self.update_timer.stop()
        
        # Minimize to tray instead of closing
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "WiFiNexus Guardian",
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()
