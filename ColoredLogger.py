import logging

class ColoredLogger(logging.Formatter):
    # ANSI escape codes for colors
    RED = "\033[31m"
    ORANGE = "\033[33m"
    RESET = "\033[0m"
    CRITICAL = "\033[41m"
    
    def format(self, record):
        # Apply the custom format
        log_msg = super().format(record)
        
        # Color based on the log level
        if record.levelno == logging.ERROR:
            log_msg = f"{self.RED}{log_msg}{self.RESET}"
        elif record.levelno == logging.WARNING:
            log_msg = f"{self.ORANGE}{log_msg}{self.RESET}"
        elif record.levelno == logging.CRITICAL:
            log_msg = f"{self.CRITICAL}{log_msg}{self.RESET}"
        
        return log_msg