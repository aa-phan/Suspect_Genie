import sys
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton, 
    QVBoxLayout, 
    QWidget,
    QTextEdit,
    QFileDialog,
    QLabel,
    QCheckBox,
    QSlider,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from model import predict_package_suspects
import pandas as pd

class CSVProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Processor")
        self.setGeometry(100, 100, 800, 600)  # Increased window size
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Create widgets
        self.file_label = QLabel("No file selected")
        self.select_file_btn = QPushButton("Select CSV File")
        self.process_btn = QPushButton("Process File")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))  # Use monospace font for table
        self.filter_suspects = QCheckBox("Show only suspect=1 entries")
        self.suspect_count_label = QLabel("Suspect entries: 0")
        
        # Create probability threshold slider
        self.prob_threshold_label = QLabel("Minimum Probability: 50%")
        self.prob_slider = QSlider(Qt.Orientation.Horizontal)
        self.prob_slider.setMinimum(0)
        self.prob_slider.setMaximum(100)
        self.prob_slider.setValue(50)
        self.prob_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.prob_slider.setTickInterval(10)
        
        # Create horizontal layout for slider and label
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Probability Threshold:"))
        slider_layout.addWidget(self.prob_slider)
        slider_layout.addWidget(self.prob_threshold_label)
        
        # Add widgets to layout
        layout.addWidget(self.file_label)
        layout.addWidget(self.select_file_btn)
        layout.addWidget(self.filter_suspects)
        layout.addWidget(self.suspect_count_label)
        layout.addLayout(slider_layout)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.output_text)
        
        # Connect buttons and slider to functions
        self.select_file_btn.clicked.connect(self.select_file)
        self.process_btn.clicked.connect(self.process_file)
        self.prob_slider.valueChanged.connect(self.update_probability_label)
        self.prob_slider.valueChanged.connect(self.process_file)
        
        # Initialize variables
        self.selected_file = None
        self.process_btn.setEnabled(False)
        self.current_results_df = None
    
    def update_probability_label(self):
        value = self.prob_slider.value()
        self.prob_threshold_label.setText(f"Minimum Probability: {value}%")
    
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
    
    def format_table(self, df):
        # Set column widths
        col_width = 20
        
        # Create header
        header = "| " + " | ".join(col.ljust(col_width) for col in df.columns) + " |"
        
        # Create separator line
        separator = "+" + "+".join("-" * (col_width + 2) for _ in df.columns) + "+"
        
        # Create rows
        rows = []
        for _, row in df.iterrows():
            row_str = "| " + " | ".join(str(val).ljust(col_width) for val in row) + " |"
            rows.append(row_str)
        
        # Combine all parts
        formatted_table = separator + "\n" + header + "\n" + separator + "\n"
        formatted_table += "\n".join(rows) + "\n" + separator
        
        return formatted_table
    
    def process_file(self):
        try:
            # Only load the file if we don't have results yet or if it's a new file
            if self.current_results_df is None:
                self.current_results_df = predict_package_suspects(self.selected_file, threshold=0.5)
            
            # Work with a copy of the results
            results_df = self.current_results_df.copy()
            
            # Count suspect entries before filtering
            suspect_count = (results_df['Suspect'] == 1).sum()
            self.suspect_count_label.setText(f"Suspect entries: {suspect_count}")
            
            # Apply probability threshold filter
            threshold = self.prob_slider.value() / 100.0
            results_df = results_df[results_df['Probability'] >= threshold]
            
            # Apply suspect filter if checkbox is checked
            if self.filter_suspects.isChecked():
                results_df = results_df[results_df['Suspect'] == 1]
            
            # Format probability as percentage
            results_df['Probability'] = results_df['Probability'].apply(lambda x: f"{x*100:.2f}%")
            
            # Format the table with equal-width columns and separators
            output_str = self.format_table(results_df)
            
            # Display in QTextEdit
            self.output_text.setText(output_str)
            
        except Exception as e:
            self.output_text.setText(f"Error processing file: {str(e)}")



def main():
    app = QApplication(sys.argv)
    window = CSVProcessorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()