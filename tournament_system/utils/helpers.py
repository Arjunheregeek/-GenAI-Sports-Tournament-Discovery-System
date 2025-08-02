"""
Utility functions for the Tournament Calendar system.

Contains common helper functions used across different modules.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "tournament_calendar.log",
    max_log_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    """Set up logging configuration."""
    
    from logging.handlers import RotatingFileHandler
    
    # Create logger
    logger = logging.getLogger('tournament_calendar')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_log_size, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def load_json_file(filename: str, default: Any = None) -> Any:
    """Load JSON file with error handling."""
    try:
        if not os.path.exists(filename):
            print(f"⚠️  File {filename} not found")
            return default
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {filename}")
        return data
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return default

def save_json_file(data: Any, filename: str, indent: int = 2) -> bool:
    """Save data to JSON file with error handling."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        print(f"✅ Saved {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False

def create_backup(filename: str, backup_dir: str = "backups") -> Optional[str]:
    """Create a backup of a file."""
    try:
        if not os.path.exists(filename):
            return None
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = os.path.join(
            backup_dir, 
            f"{Path(filename).stem}_{timestamp}{Path(filename).suffix}"
        )
        
        # Copy file
        import shutil
        shutil.copy2(filename, backup_filename)
        
        print(f"✅ Created backup: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except:
        return ''

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common unwanted characters
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    return text.strip()

def format_date(date_str: str) -> str:
    """Format date string to a standard format."""
    if not date_str:
        return ""
    
    # This is a simple implementation - you might want to use dateutil for better parsing
    try:
        from datetime import datetime
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%d %B %Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matches, return as is
        return date_str.strip()
    except:
        return date_str

def calculate_confidence_score(data: Dict) -> float:
    """Calculate confidence score for extracted data."""
    score = 0.0
    total_fields = 0
    
    # Required fields
    required_fields = ['tournament_name', 'start_date', 'end_date', 'official_url']
    for field in required_fields:
        total_fields += 1
        if data.get(field) and data[field].strip():
            score += 1.0
    
    # Optional fields (half weight)
    optional_fields = ['level', 'streaming_links', 'image_url', 'summary']
    for field in optional_fields:
        total_fields += 0.5
        if data.get(field) and data[field].strip():
            score += 0.5
    
    # Calculate percentage
    if total_fields > 0:
        confidence = (score / total_fields) * 100
        return round(confidence, 2)
    
    return 0.0

def get_file_size(filename: str) -> str:
    """Get human-readable file size."""
    try:
        size = os.path.getsize(filename)
        
        # Convert to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown size"

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a simple text progress bar."""
    if total == 0:
        return "[" + "=" * width + "] 100%"
    
    progress = current / total
    filled_width = int(width * progress)
    bar = "=" * filled_width + "-" * (width - filled_width)
    percentage = progress * 100
    
    return f"[{bar}] {percentage:.1f}% ({current}/{total})"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters."""
    import re
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    return filename

def merge_dictionaries(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries, with dict2 values taking precedence."""
    merged = dict1.copy()
    merged.update(dict2)
    return merged

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def validate_environment_variables(required_vars: List[str]) -> List[str]:
    """Validate that required environment variables are set."""
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def print_banner(title: str, width: int = 60, char: str = "=") -> None:
    """Print a formatted banner."""
    print(char * width)
    print(f"{title:^{width}}")
    print(char * width)

def print_section(title: str, width: int = 60) -> None:
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))
