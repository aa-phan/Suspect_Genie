import sys
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget,
    QTextEdit,
    QFileDialog,
    QLabel,
    QCheckBox,
    QSlider,
    QFrame,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QFontDatabase, QPixmap
from model import predict_package_suspects
import pandas as pd

# Define color constants
SYMBOTIC_GREEN = "#7AB80E"
SYMBOTIC_DARK = "#1A1A1A"
SYMBOTIC_DARKER = "#000000"
SYMBOTIC_GRAY = "#333333"
SYMBOTIC_LIGHT_GRAY = "#666666"

class SectionFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("section")
        self.setStyleSheet(f"""
            QFrame#section {{
                background-color: {SYMBOTIC_GRAY};
                border: 1px solid {SYMBOTIC_LIGHT_GRAY};
                border-radius: 8px;
            }}
            QLabel, QCheckBox {{
                background-color: {SYMBOTIC_GRAY};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

    def layout(self):
        return self._layout

class CSVProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suspect Genie")
        self.setGeometry(100, 100, 1200, 800)

        # Add window icon
        icon = QIcon("./Symbotic_Logo.png")
        self.setWindowIcon(icon)
        # Also set the application-wide icon (shows in taskbar)
        app = QApplication.instance()
        app.setWindowIcon(icon)

        # Set application-wide font
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        main_widget.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {SYMBOTIC_DARKER};
            }}
            QPushButton {{
                background-color: {SYMBOTIC_GREEN};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: #8BC34A;
            }}
            QPushButton:disabled {{
                background-color: {SYMBOTIC_LIGHT_GRAY};
            }}
            QLabel {{
                color: white;
                letter-spacing: 0.2px;
                background-color: transparent;
            }}
            QCheckBox {{
                color: white;
                font-size: 14px;
                letter-spacing: 0.2px;
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {SYMBOTIC_LIGHT_GRAY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {SYMBOTIC_GREEN};
                border: 2px solid {SYMBOTIC_GREEN};
            }}
            QSlider {{
                background-color: {SYMBOTIC_GRAY};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {SYMBOTIC_LIGHT_GRAY};
                height: 6px;
                background: {SYMBOTIC_GRAY};
                margin: 2px 0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {SYMBOTIC_GREEN};
                border: none;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QTableWidget {{
                background-color: {SYMBOTIC_DARK};
                color: white;
                border: none;
                gridline-color: {SYMBOTIC_LIGHT_GRAY};
                font-family: 'Cascadia Code', 'SF Mono', 'Consolas', monospace;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {SYMBOTIC_GREEN};
            }}
            QHeaderView::section {{
                background-color: {SYMBOTIC_GRAY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
            QScrollBar:vertical {{
                background: {SYMBOTIC_DARK};
                width: 12px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {SYMBOTIC_LIGHT_GRAY};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar:horizontal {{
                background: {SYMBOTIC_DARK};
                height: 12px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {SYMBOTIC_LIGHT_GRAY};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {SYMBOTIC_DARK};
                min-width: 280px;
                max-width: 280px;
                padding: 24px;
                border-right: 1px solid {SYMBOTIC_LIGHT_GRAY};
            }}
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(16)
        sidebar.setLayout(sidebar_layout)
        
        # Create title section
        title_section = SectionFrame()
        title_section.setStyleSheet(f"""
            QFrame#section {{
                background-color: {SYMBOTIC_GRAY};
                border: 1px solid {SYMBOTIC_GREEN};
                border-radius: 8px;
            }}
            QLabel {{
                background-color: {SYMBOTIC_GRAY};
            }}
        """)
        
        # Add logo/title
        logo_label = QLabel("Suspect Genie")
        logo_label.setStyleSheet(f"""
            color: {SYMBOTIC_GREEN};
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)
        title_section.layout().addWidget(logo_label)
        
        # Add file selection button
        self.select_file_btn = QPushButton("Select CSV File")
        self.select_file_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SYMBOTIC_LIGHT_GRAY};
                color: white;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {SYMBOTIC_GREEN};
                color: white;
            }}
        """)
        title_section.layout().addWidget(self.select_file_btn)
        
        sidebar_layout.addWidget(title_section)
        
        # Create filters section
        filters_section = SectionFrame()
        filters_section.setStyleSheet(f"""
            QFrame#section {{
                background-color: {SYMBOTIC_GRAY};
                border: 1px solid {SYMBOTIC_GREEN};
                border-radius: 9px;
            }}
            QLabel, QCheckBox, QSlider {{
                background-color: {SYMBOTIC_GRAY};
            }}
        """)
        
        # Add section title
        filters_title = QLabel("Filters")
        filters_title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {SYMBOTIC_GREEN};
            margin-bottom: 8px;
        """)
        filters_section.layout().addWidget(filters_title)
        
        # Add suspect filter
        self.filter_suspects = QCheckBox("Show only suspect=1 entries")
        self.filter_suspects.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            margin-left: 8px;
        """)
        filters_section.layout().addWidget(self.filter_suspects)
        
        # Add probability threshold slider
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(8)
        
        slider_label = QLabel("Threshold:")
        slider_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            margin-left: 4px;
        """)
        slider_layout.addWidget(slider_label)
        
        self.prob_slider = QSlider(Qt.Orientation.Horizontal)
        self.prob_slider.setMinimum(0)
        self.prob_slider.setMaximum(100)
        self.prob_slider.setValue(0)
        self.prob_slider.setTickPosition(QSlider.TickPosition.NoTicks)
        slider_layout.addWidget(self.prob_slider)
        
        self.prob_threshold_label = QLabel("0%")
        self.prob_threshold_label.setStyleSheet(f"""
            color: {SYMBOTIC_GREEN};
            font-size: 14px;
            font-weight: 600;
            min-width: 45px;
        """)
        slider_layout.addWidget(self.prob_threshold_label)
        filters_section.layout().addLayout(slider_layout)
        
        sidebar_layout.addWidget(filters_section)
        
        # Create stats section
        stats_section = SectionFrame()
        stats_section.setStyleSheet(f"""
            QFrame#section {{
                background-color: {SYMBOTIC_GRAY};
                border: 1px solid {SYMBOTIC_GREEN};
                border-radius: 8px;
            }}
            QLabel {{
                background-color: {SYMBOTIC_GRAY};
            }}
        """)
        
        # Add section title
        stats_title = QLabel("Statistics")
        stats_title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {SYMBOTIC_GREEN};
            margin-bottom: 8px;
        """)
        stats_section.layout().addWidget(stats_title)
        
        # Add suspect count
        self.suspect_count_label = QLabel("Suspect entries: 0")
        self.suspect_count_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: white;
            margin-left: 2px;
        """)
        stats_section.layout().addWidget(self.suspect_count_label)
        
        sidebar_layout.addWidget(stats_section)
        sidebar_layout.addStretch()  # This pushes everything up
        
        # Create a horizontal layout for the logo
        logo_container = QHBoxLayout()
        logo_container.setContentsMargins(0, 0, 0, 8)  # Add some bottom margin
        
        # Add logo at the bottom
        bottom_logo = QLabel()
        bottom_logo.setStyleSheet("""
            padding: 8px;
        """)
        # Set a fixed size for the logo
        bottom_logo.setFixedSize(160, 160)
        
        # Load and set the logo image
        logo_path = "./Symbotic_Logo.png"
        logo_pixmap = QPixmap(logo_path)
        bottom_logo.setPixmap(logo_pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Add the logo to the horizontal layout with stretches on both sides
        logo_container.addStretch()
        logo_container.addWidget(bottom_logo)
        logo_container.addStretch()
        
        # Add the logo container to the sidebar
        sidebar_layout.addLayout(logo_container)
        main_layout.addWidget(sidebar)
        
        # Create main content area
        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_area.setLayout(content_layout)
        
        # Create header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {SYMBOTIC_DARK};
                border-bottom: 1px solid {SYMBOTIC_LIGHT_GRAY};
                padding: 16px;
                border-radius: 8px;
            }}
        """)
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("""
            font-size: 15px;
            color: #CCCCCC;
            font-weight: 400;
            letter-spacing: 0.2px;
        """)
        header_layout.addWidget(self.file_label)
        
        self.process_btn = QPushButton("Process File")
        header_layout.addWidget(self.process_btn)
        
        content_layout.addWidget(header)
        
        # Create results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(0)
        self.results_table.setRowCount(0)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().setSectionsClickable(True)
        self.results_table.horizontalHeader().setSortIndicatorShown(True)
        content_layout.addWidget(self.results_table)
        
        main_layout.addWidget(content_area)
        
        # Connect buttons and slider to functions
        self.select_file_btn.clicked.connect(self.select_file)
        self.process_btn.clicked.connect(self.process_file)
        self.prob_slider.valueChanged.connect(self.update_probability_label)
        self.prob_slider.valueChanged.connect(self.process_file)
        self.filter_suspects.stateChanged.connect(self.on_checkbox_changed)
        
        # Initialize variables
        self.selected_file = None
        self.process_btn.setEnabled(False)
        self.current_results_df = None

        # After creating the controls, disable them initially
        self.filter_suspects.setEnabled(False)
        self.prob_slider.setEnabled(False)

    def update_probability_label(self):
        value = self.prob_slider.value()
        # Enforce minimum of 50 when checkbox is checked
        if self.filter_suspects.isChecked() and value < 50:
            self.prob_slider.setValue(50)
            value = 50
        self.prob_threshold_label.setText(f"{value}%")
    
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_name:
            self.selected_file = file_name
            self.file_label.setText(f"Selected: {file_name}")
            self.process_btn.setEnabled(True)
            # Enable the filter controls
            self.filter_suspects.setEnabled(True)
            self.prob_slider.setEnabled(True)
    
    def update_table(self, df):
        self.results_table.setSortingEnabled(False)
        
        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col])
                item = QTableWidgetItem()
                
                if df.iloc[row, col] is not None:
                    if isinstance(df.iloc[row, col], (int, float)):
                        item.setData(Qt.ItemDataRole.DisplayRole, df.iloc[row, col])
                    else:
                        item.setText(value)
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(row, col, item)
        
        self.results_table.setSortingEnabled(True)
    
    def process_file(self):
        try:
            if self.selected_file is None:
                return  # Don't process if no file selected
            
            if self.current_results_df is None:
                self.current_results_df = predict_package_suspects(self.selected_file, threshold=0.5)
            
            results_df = self.current_results_df.copy()
            
            # Apply threshold filter first
            threshold = self.prob_slider.value() / 100.0
            filtered_df = results_df[results_df['Probability'] >= threshold]
            
            # Always count suspect=1 entries regardless of checkbox
            suspect_count = (filtered_df['Suspect'] == 1).sum()
            self.suspect_count_label.setText(f"Suspect entries: {suspect_count}")
            
            # Apply suspect filter if checkbox is checked
            if self.filter_suspects.isChecked():
                filtered_df = filtered_df[filtered_df['Suspect'] == 1]
            
            # Format probability as percentage
            filtered_df['Probability'] = filtered_df['Probability'].apply(lambda x: f"{x*100:.2f}%")
            
            self.update_table(filtered_df)
            
        except Exception as e:
            self.file_label.setText(f"Error processing file: {str(e)}")
            print(f"Error processing file: {e}")
    def on_checkbox_changed(self, state):
        if state == Qt.CheckState.Checked:
            # When showing non-suspects, restrict to 50-100
            self.prob_slider.setMinimum(50)
            if self.prob_slider.value() < 50:
                self.prob_slider.setValue(50)
        else:
            # When showing all entries, allow full range 0-100
            self.prob_slider.setMinimum(0)
        self.process_file()

def main():
    app = QApplication(sys.argv)
    window = CSVProcessorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()