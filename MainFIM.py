import os
import hashlib
import time
import logging
import getpass
import time
from datetime import datetime

# Getting username
def get_username():
    return getpass.getuser()

# Setting up logging
def setup_logging(username):
    logger = logging.getLogger(f"user.{username}")
    logger.setLevel(logging.INFO)
    
    # Create folder with username if it doesn't exist
    log_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "Logs", username)
    os.makedirs(log_folder, exist_ok=True)
    
    # Use current timestamp to name log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_filename = f"{timestamp}.log"
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(os.path.join(log_folder, log_filename))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger

# Calculating the checksum
def calculate_file_checksum(filepath):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(4096):
            file_hash.update(chunk)
        return file_hash.hexdigest()

# Deleting basefile if exist
def erase_baseline_if_already_exist():
    baseline_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "baseline.txt")
    if os.path.exists(baseline_file_path):
        os.remove(baseline_file_path)

def create_baseline():
    # Delete baseline if it exists
    erase_baseline_if_already_exist()

    # For each file in the files folder, calculate the hash, and write to baseline.txt
    baseline_file = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "baseline.txt")
    with open(baseline_file, 'w') as f:
        files_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "Files")
        files = os.listdir(files_folder)
        for file_name in files:
            file_path = os.path.join(files_folder, file_name)
            file_hash = calculate_file_checksum(file_path)
            f.write(f"{file_path}|{file_hash}\n")

def monitor_files(logger):
    # Load file hash from baseline.txt and store them in a dictionary
    file_hash_dictionary = {}
    baseline_file = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "baseline.txt")
    with open(baseline_file, 'r') as f:
        for line in f:
            file_path, file_hash = line.strip().split('|')
            file_hash_dictionary[file_path] = file_hash

    # Begin monitoring files with saved baseline
    while True:
        time.sleep(1)

        # Collect all the files in the folder
        files_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Project", "FMI-Python", "Files")
        files = os.listdir(files_folder)

        # For each file calculate the hash, and compare with the saved hash
        for file_name in files:
            file_path = os.path.join(files_folder, file_name)
            file_hash = calculate_file_checksum(file_path)

            # Notify if a new file has been created
            if file_path not in file_hash_dictionary:
                logger.info(f"New file created! {file_path}")
                file_hash_dictionary[file_path] = file_hash
                
            # Compare hash of existing file with saved hash
            elif file_hash != file_hash_dictionary[file_path]:
                logger.info(f"File modified! {file_path}")
                file_hash_dictionary[file_path] = file_hash

        # Check for deleted files
        for file_path in file_hash_dictionary.copy():
            if not os.path.exists(file_path):
                logger.info(f"File deleted! {file_path}")
                del file_hash_dictionary[file_path]

# Main funtion
if __name__ == "__main__":
    username = get_username()
    logger = setup_logging(username)
    create_baseline()
    monitor_files(logger)