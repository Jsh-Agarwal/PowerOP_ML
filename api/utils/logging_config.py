import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

class RequestResponseFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'request') or hasattr(record, 'response'):
            # Format request/response logs with extra detail
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'message': record.getMessage()
            }
            
            if hasattr(record, 'request'):
                log_data['request'] = record.request
            if hasattr(record, 'response'):
                log_data['response'] = record.response
                
            return json.dumps(log_data)
        return super().format(record)

def setup_logging():
    """Configure logging with file and console handlers."""
    # Create formatters
    detailed_formatter = RequestResponseFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # File handler for detailed logs
    today = datetime.now().strftime('%Y%m%d')
    detailed_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f'detailed_{today}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    detailed_handler.setFormatter(detailed_formatter)
    detailed_handler.setLevel(logging.DEBUG)

    # File handler for request/response logs
    api_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f'requests_{today}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setFormatter(detailed_formatter)
    api_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(detailed_handler)
    root_logger.addHandler(console_handler)

    # Configure API logger
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.DEBUG)
    api_logger.addHandler(api_handler)
