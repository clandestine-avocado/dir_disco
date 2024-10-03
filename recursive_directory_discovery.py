import os
import pandas as pd
import logging
from pathlib import Path
import time
from datetime import datetime

# Create log and output directories
script_dir = Path(__file__).parent
log_dir = script_dir / "log"
output_dir = script_dir / "output"
log_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)

# Get current datetime for file naming
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"{current_datetime}_dir_discovery.log"),  # Log to file in log directory with datetime prefix
        logging.StreamHandler()  # Log to console
    ]
)

def traverse_directory(top_dir):
    """
    Recursively traverse a directory and return a DataFrame with the structure.
    
    Args:
    - top_dir (str or Path): The top level directory to start the search.
    
    Returns:
    - pd.DataFrame: A DataFrame containing file and directory details.
    - str: Path to the CSV file created from the DataFrame.
    """
    records = []  # To store information about each file/directory

    # Convert top_dir to Path object to handle path manipulation more easily
    top_dir = Path(top_dir)

    def process_directory(directory):
        try:
            # Iterate through all items in the directory
            for item in directory.iterdir():
                try:
                    # Get basic information
                    item_path = str(item.resolve())  # Full path
                    item_name = item.name  # File or directory name
                    item_type = 'Directory' if item.is_dir() else 'File'  # Type of item
                    item_size = item.stat().st_size if item.is_file() else None  # File size, None for directories
                    modification_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(item.stat().st_mtime))  # Modification time

                    # Log the processing of the item
                    logging.info(f"Processing {item_type}: {item_path}")

                    # Record the item details
                    records.append({
                        'Name': item_name,
                        'Path': item_path,
                        'Type': item_type,
                        'Size (bytes)': item_size,
                        'Modification Time': modification_time
                    })

                    # If it's a directory, recurse into it
                    if item.is_dir():
                        process_directory(item)

                except (PermissionError, FileNotFoundError) as e:
                    # Handle errors where a file or directory is inaccessible
                    logging.error(f"Error accessing {item}: {e}")
        except Exception as e:
            logging.error(f"Failed to process directory {directory}: {e}")

    # Start processing from the top level directory
    process_directory(top_dir)

    # Create a DataFrame from the collected records
    df = pd.DataFrame(records)

    # Save DataFrame as CSV in the output directory with datetime prefix
    csv_output_path = output_dir / f"{current_datetime}_dir_structure.csv"
    df.to_csv(csv_output_path, index=False)
    
    logging.info(f"CSV file created at {csv_output_path}")
    
    return df, str(csv_output_path)


# Example usage
if __name__ == "__main__":
    # Define the top level directory to traverse
    top_level_directory = r"C:\Users\kroy2\Documents"
    # "C:\Users\kroy2\Desktop"
    # Run the function and get the DataFrame and CSV path
    df, csv_file = traverse_directory(top_level_directory)

    # Print the DataFrame (optional)
    print(df.head())