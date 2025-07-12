"""
Security Module for UI Assistant

This module provides security-related functionality including:
- Input validation
- Access control for critical operations
- Permission management
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum, auto
from dataclasses import dataclass
from PySide6.QtCore import QRect, QPoint

class SecurityError(Exception):
    """Base class for security-related exceptions."""
    pass

class ValidationError(SecurityError):
    """Raised when input validation fails."""
    pass

class PermissionDeniedError(SecurityError):
    """Raised when a user doesn't have permission to perform an operation."""
    pass

class OperationType(Enum):
    """Types of operations that can be performed by the UI Assistant."""
    CLICK = auto()
    TYPE_TEXT = auto()
    NAVIGATE = auto()
    SCREENSHOT = auto()
    SYSTEM_COMMAND = auto()
    FILE_ACCESS = auto()
    NETWORK_ACCESS = auto()
    REGISTRY_ACCESS = auto()

@dataclass
class SecurityContext:
    """Context for security checks, containing information about the current operation."""
    user_id: str = "default"
    permissions: Set[str] = None
    is_privileged: bool = False
    source_ip: str = "127.0.0.1"
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = set()

class SecurityManager:
    """Manages security policies and validations for the UI Assistant."""
    
    # Define safe domains for navigation
    SAFE_DOMAINS = {
        "localhost",
        "127.0.0.1",
        "::1",
        # Add other trusted domains here
    }
    
    # Define safe file paths (regex patterns)
    SAFE_PATH_PATTERNS = [
        r'^[A-Za-z]:\\Users\\[^\\]+\\.*$',  # User home directory
        r'^/home/[^/]+/.*$',  # Unix home directory
        r'^/tmp/.*$',  # Temp directory
    ]
    
    # Define restricted commands/patterns
    RESTRICTED_COMMANDS = [
        r'rm\s+-[rf]',  # Recursive force remove
        r'mv\s+.*\s+/',  # Moving files to root
        r':\s*\{\s*:|\s*\|\s*:\s*\}',  # Fork bomb
        r'chmod\s+[0-7][0-7][0-7][0-7]?\s+',  # Dangerous chmod
        r'^\s*(wget|curl)\s+',  # Downloading files
        r'\$\{IFS\}',  # IFS injection
    ]
    
    def __init__(self):
        self._compiled_path_patterns = [re.compile(p) for p in self.SAFE_PATH_PATTERNS]
        self._compiled_restricted_commands = [re.compile(p, re.IGNORECASE) for p in self.RESTRICTED_COMMANDS]
    
    def validate_click_coordinates(self, x: int, y: int, screen_rect: QRect) -> Tuple[bool, str]:
        """Validate that click coordinates are within screen bounds."""
        if not isinstance(x, int) or not isinstance(y, int):
            return False, "Coordinates must be integers"
            
        if not screen_rect.contains(QPoint(x, y)):
            return False, f"Coordinates ({x}, {y}) are outside screen bounds {screen_rect}"
            
        return True, ""
    
    def validate_text_input(self, text: str, max_length: int = 1000) -> Tuple[bool, str]:
        """Validate text input to prevent injection attacks."""
        if not isinstance(text, str):
            return False, "Text must be a string"
            
        if len(text) > max_length:
            return False, f"Text exceeds maximum length of {max_length} characters"
            
        # Check for potential command injection
        for pattern in self._compiled_restricted_commands:
            if pattern.search(text):
                return False, "Input contains potentially dangerous patterns"
                
        return True, ""
    
    def validate_file_path(self, file_path: str, operation: str = 'read') -> Tuple[bool, str]:
        """
        Validate that a file path is safe for the specified operation.
        
        Args:
            file_path: The file path to validate
            operation: The operation to perform ('read', 'write', etc.)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Convert to absolute path and normalize
            abs_path = str(Path(file_path).absolute())
            
            # Check against safe path patterns
            if not any(pattern.match(abs_path) for pattern in self._compiled_path_patterns):
                return False, f"Access to path '{abs_path}' is not allowed"
                
            # Additional checks based on operation
            if operation == 'write':
                # Additional restrictions for write operations
                parent_dir = os.path.dirname(abs_path)
                if not os.path.exists(parent_dir) or not os.access(parent_dir, os.W_OK):
                    return False, f"Cannot write to path: '{abs_path}'. Parent directory is not writable"
                    
                # Check if file exists and is writable
                if os.path.exists(abs_path) and not os.access(abs_path, os.W_OK):
                    return False, f"File '{abs_path}' is not writable"
                
                # Prevent writing to system directories
                restricted_paths = [
                    r'C:\\Windows\\',
                    r'C:\\Program Files\\',
                    r'C:\\Program Files (x86)\\',
                    '/etc/',
                    '/usr/',
                    '/bin/',
                    '/sbin/',
                    '/System/Library/',
                    '/Library/',
                    '/Applications/'
                ]
                
                if any(abs_path.startswith(path) for path in restricted_paths):
                    return False, "Writing to system directories is not allowed"
                
                # Prevent writing dangerous file types
                dangerous_extensions = ['.exe', '.dll', '.bat', '.sh', '.py', '.js']
                if any(abs_path.lower().endswith(ext) for ext in dangerous_extensions):
                    return False, "Writing executable files is not allowed"
            
            # For read operations, check if file exists and is readable
            elif operation == 'read':
                if not os.path.exists(abs_path):
                    return False, f"File '{abs_path}' does not exist"
                if not os.access(abs_path, os.R_OK):
                    return False, f"File '{abs_path}' is not readable"
                
                # Prevent reading sensitive files
                sensitive_paths = [
                    '/etc/passwd', '/etc/shadow', '/etc/sudoers',
                    'C:\\Windows\\System32\\config\\SAM',
                    '~/.ssh/', '/root/.ssh/'
                ]
                
                for sensitive_path in sensitive_paths:
                    if abs_path.startswith(os.path.expanduser(sensitive_path)):
                        return False, "Access to sensitive files is not allowed"
                
            # All checks passed
            return True, ""
            
        except Exception as e:
            return False, f"Error validating file path: {str(e)}"
    
    def check_permission(self, context: SecurityContext, operation: OperationType) -> Tuple[bool, str]:
        """Check if the current context has permission to perform the operation."""
        # Always allow privileged users
        if context.is_privileged:
            return True, ""
        
        # Check operation-specific permissions
        if operation == OperationType.SYSTEM_COMMAND:
            if "execute_system_commands" not in context.permissions:
                return False, "Insufficient permissions to execute system commands"
                
        elif operation == OperationType.FILE_ACCESS:
            if "access_files" not in context.permissions:
                return False, "Insufficient permissions to access files"
                
        elif operation == OperationType.NETWORK_ACCESS:
            if "access_network" not in context.permissions:
                return False, "Insufficient permissions to access network"
                
        elif operation == OperationType.REGISTRY_ACCESS:
            return False, "Registry access is not allowed"
            
        return True, ""
    
    def sanitize_html(self, html: str) -> str:
        """Sanitize HTML to prevent XSS attacks."""
        # This is a basic example - consider using a library like bleach in production
        if not html:
            return ""
            
        # Remove potentially dangerous tags and attributes
        safe_html = re.sub(r'<\s*(script|iframe|object|embed|link|form|input|button).*?>', '', html, flags=re.IGNORECASE)
        safe_html = re.sub(r'on\w+\s*=', 'data-sanitized-', safe_html, flags=re.IGNORECASE)
        
        return safe_html

# Global instance
security_manager = SecurityManager()

def require_permission(operation: OperationType):
    """Decorator to check permissions before executing a method."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Get security context (assuming it's stored in the instance)
            context = getattr(self, '_security_context', None)
            if context is None:
                raise PermissionDeniedError("No security context available")
                
            # Check permissions
            allowed, reason = security_manager.check_permission(context, operation)
            if not allowed:
                raise PermissionDeniedError(reason or "Operation not permitted")
                
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
