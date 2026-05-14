"""
Finovate WiFiNexus Guardian - Professional Wireless Intelligence Platform
Version: 1.0.0
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

def main():
    """Main entry point for WiFiNexus Guardian"""
    
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("WiFiNexus Guardian")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Finovate - AHMED EG")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show splash screen
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.black)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage(
        "WiFiNexus Guardian\nv1.0.0\n\nProfessional Wireless Intelligence Platform\n\n© 2025 Ahmed Mostafa Ibrahim",
        Qt.AlignCenter,
        Qt.cyan
    )
    splash.show()
    app.processEvents()
    
    # Initialize core components
    from core.initializer import CoreInitializer
    from gui.main_window import MainWindow
    
    initializer = CoreInitializer()
    
    def show_main_window():
        splash.finish(main_win)
        main_win.show()
        
    # Initialize with splash visible
    initializer.initialize_all()
    
    # Create main window
    main_win = MainWindow()
    
    # Schedule main window display
    QTimer.singleShot(2000, show_main_window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
