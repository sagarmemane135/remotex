"""
Exit codes for RemoteX CLI.
Standardized exit codes for consistent error handling.
"""

class ExitCode:
    """Standardized exit codes for RemoteX."""
    
    # Success
    SUCCESS = 0
    
    # General errors (1-9)
    GENERAL_ERROR = 1
    INVALID_USAGE = 2
    
    # Connection errors (10-19)
    CONNECTION_ERROR = 10
    CONNECTION_TIMEOUT = 11
    AUTH_ERROR = 12
    HOST_KEY_ERROR = 13
    
    # Configuration errors (20-29)
    CONFIG_ERROR = 20
    HOST_NOT_FOUND = 21
    INVALID_CONFIG = 22
    CONFIG_FILE_ERROR = 23
    
    # Execution errors (30-39)
    COMMAND_FAILED = 30
    COMMAND_TIMEOUT = 31
    REMOTE_ERROR = 32
    
    # Permission errors (40-49)
    PERMISSION_ERROR = 40
    SSH_KEY_ERROR = 41
    
    # Input errors (50-59)
    INVALID_INPUT = 50
    MISSING_ARGUMENT = 51
    
    # System errors (60-69)
    SYSTEM_ERROR = 60
    INTERRUPT = 130  # Standard SIGINT code


# Error message templates with suggestions
ERROR_MESSAGES = {
    ExitCode.CONNECTION_ERROR: {
        "title": "Connection Failed",
        "suggestions": [
            "Check if the server is online: ping <hostname>",
            "Verify SSH service is running on the server",
            "Check firewall rules and network connectivity"
        ]
    },
    ExitCode.CONNECTION_TIMEOUT: {
        "title": "Connection Timeout",
        "suggestions": [
            "Increase timeout with --timeout option",
            "Check network latency: ping <hostname>",
            "Verify server is not overloaded"
        ]
    },
    ExitCode.AUTH_ERROR: {
        "title": "Authentication Failed",
        "suggestions": [
            "Verify your SSH key is correct",
            "Check SSH key permissions: chmod 600 ~/.ssh/id_rsa",
            "Ensure your public key is in server's ~/.ssh/authorized_keys"
        ]
    },
    ExitCode.HOST_NOT_FOUND: {
        "title": "Host Not Found",
        "suggestions": [
            "List available hosts: remotex list",
            "Add the host: remotex add",
            "Check your SSH config: cat ~/.ssh/config"
        ]
    },
    ExitCode.CONFIG_ERROR: {
        "title": "Configuration Error",
        "suggestions": [
            "Check SSH config syntax: ssh -G <hostname>",
            "Verify config file permissions",
            "Review SSH config at ~/.ssh/config"
        ]
    },
    ExitCode.COMMAND_FAILED: {
        "title": "Command Failed",
        "suggestions": [
            "Check command syntax",
            "Verify you have necessary permissions on remote server",
            "Try running the command directly: ssh <host> '<command>'"
        ]
    },
    ExitCode.SSH_KEY_ERROR: {
        "title": "SSH Key Error",
        "suggestions": [
            "Check if key file exists",
            "Verify key permissions: chmod 600 <keyfile>",
            "Generate a new key: ssh-keygen -t ed25519"
        ]
    },
    ExitCode.INVALID_CONFIG: {
        "title": "Invalid Configuration",
        "suggestions": [
            "Run config validation: remotex config show",
            "Check for syntax errors in SSH config",
            "Restore default config if needed"
        ]
    }
}


def get_error_suggestions(exit_code: int) -> dict:
    """
    Get error message and suggestions for an exit code.
    
    Args:
        exit_code: The exit code
        
    Returns:
        dict: Error title and suggestions, or None if not found
    """
    return ERROR_MESSAGES.get(exit_code, {
        "title": "Error",
        "suggestions": ["Check the error message above for details"]
    })
