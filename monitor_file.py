import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class FilteredFileHandler(PatternMatchingEventHandler):
    def __init__(self, log_file, ignore_patterns=None):
        # Convert log_file to absolute path for reliable pattern matching
        self.log_file = os.path.abspath(log_file)
        
        # Create ignore patterns list, always including the log file
        print(f"*{os.path.basename(self.log_file)}")
        ignore_patterns_in = [f"*{os.path.basename(self.log_file)}"]
        if ignore_patterns:
            ignore_patterns_in.extend(ignore_patterns)
            
        # Initialize the pattern matching handler
        super().__init__(
            ignore_patterns=ignore_patterns_in,
            ignore_directories=True,
            case_sensitive=False
        )

    def log_event(self, event_type, path):
        # Convert to absolute path for consistent logging
        abs_path = os.path.abspath(path)
        
        # Double-check that we're not logging the log file itself
        if abs_path != self.log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_file, 'a') as f:
                f.write(f"{timestamp} - {event_type}: {path}\n")
            logging.info(f"{event_type}: {path}")

    def on_created(self, event):
        if not event.is_directory:
            self.log_event("File created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.log_event("File modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log_event("File deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.log_event("File moved/renamed", 
                          f"from {event.src_path} to {event.dest_path}")

def start_monitoring(path_to_watch, log_file="file_changes.log", ignore_patterns=None):
    """
    Start monitoring a directory for file changes with exclusion patterns.
    
    Args:
        path_to_watch (str): Directory path to monitor
        log_file (str): File path where to save the logs
        ignore_patterns (list): List of glob patterns to ignore (e.g., ["*.tmp", "*.log"])
    """
    try:
        # Initialize the event handler and observer
        event_handler = FilteredFileHandler(log_file, ignore_patterns)
        observer = Observer()
        
        # Schedule the observer
        observer.schedule(event_handler, path_to_watch, recursive=False)
        
        # Start the observer
        observer.start()
        logging.info(f"Started monitoring {path_to_watch}")
        logging.info(f"Logging changes to {log_file}")
        logging.info(f"Ignoring patterns: {event_handler.ignore_patterns}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logging.info("Monitoring stopped by user")
        
        observer.join()
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage with ignore patterns
    DIRECTORY_TO_WATCH = "."  # Current directory
    IGNORE_PATTERNS = [
        "*.tmp",        # Ignore temporary files
        "*.pyc",        # Ignore Python compiled files
        ".git/*",       # Ignore git directory
        "__pycache__/*" # Ignore Python cache directory
    ]
    
    start_monitoring(
        path_to_watch=DIRECTORY_TO_WATCH,
        log_file="file_changes.log",
        ignore_patterns=IGNORE_PATTERNS
    )
