import csv
import sys
from model import process_csv_data

def read_csv_file(file_path):
    """
    Read CSV file and return list of dictionaries
    """
    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            return list(csv_reader)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def main():
    # Check if file path is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Read CSV file
    data = read_csv_file(file_path)
    
    # Process data
    output = process_csv_data(data)
    
    # Print output
    print(output)

if __name__ == "__main__":
    main()