"""
Advanced Process Manager for WiFiNexus Guardian
Handles subprocess execution with robust error handling, timeouts, and recovery mechanisms.
"""

import subprocess
import logging
import time
import os
import signal
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ProcessExecutionError(Exception):
    """Custom exception for process execution failures"""
    def __init__(self, command: str, returncode: int, stdout: str, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Command '{command}' failed with code {returncode}: {stderr}")

class RobustProcessManager:
    """
    Manages external tool execution with:
    - Comprehensive error handling
    - Timeout management
    - Automatic retry logic
    - Output validation
    - Resource cleanup
    """
    
    def __init__(self, timeout: int = 300, max_retries: int = 3, retry_delay: float = 2.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.running_processes: Dict[int, subprocess.Popen] = {}
        
    def execute(
        self,
        command: list,
        capture_output: bool = True,
        validate_output: Optional[callable] = None,
        require_success: bool = True,
        description: str = ""
    ) -> Tuple[bool, str, str]:
        """
        Execute a command with robust error handling
        
        Args:
            command: List of command arguments
            capture_output: Whether to capture stdout/stderr
            validate_output: Optional function to validate output
            require_success: Whether to raise exception on failure
            description: Human-readable description for logging
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        cmd_str = ' '.join(command)
        desc = description or cmd_str
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Executing: {desc} (Attempt {attempt + 1}/{self.max_retries})")
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                
                pid = process.pid
                self.running_processes[pid] = process
                logger.debug(f"Started process PID: {pid}")
                
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    returncode = process.returncode
                    
                    # Remove from running processes
                    if pid in self.running_processes:
                        del self.running_processes[pid]
                    
                    # Log output
                    if stdout:
                        logger.debug(f"STDOUT: {stdout[:500]}...")
                    if stderr:
                        logger.warning(f"STDERR: {stderr[:500]}...")
                    
                    # Validate output if validator provided
                    if validate_output and not validate_output(stdout, stderr, returncode):
                        raise ProcessExecutionError(
                            cmd_str, returncode, stdout, 
                            stderr or "Output validation failed"
                        )
                    
                    # Check success
                    if require_success and returncode != 0:
                        raise ProcessExecutionError(cmd_str, returncode, stdout, stderr)
                    
                    logger.info(f"Successfully completed: {desc}")
                    return True, stdout or "", stderr or ""
                    
                except subprocess.TimeoutExpired:
                    logger.error(f"Timeout expired for: {desc}")
                    self._kill_process_tree(process)
                    if attempt == self.max_retries - 1:
                        raise ProcessExecutionError(
                            cmd_str, -1, "", "Operation timed out"
                        )
                    
                except Exception as e:
                    logger.error(f"Error during execution of {desc}: {str(e)}")
                    if pid in self.running_processes:
                        self._kill_process_tree(process)
                    if attempt == self.max_retries - 1:
                        raise
                        
            except ProcessExecutionError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error executing {desc}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise ProcessExecutionError(cmd_str, -1, "", str(e))
            
            # Retry delay
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        return False, "", "Max retries exceeded"
    
    def _kill_process_tree(self, process: subprocess.Popen):
        """Kill process and all its children"""
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Failed to kill process tree: {e}")
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
            except:
                pass
    
    def cleanup_all(self):
        """Clean up all running processes"""
        logger.info("Cleaning up all running processes...")
        for pid, process in list(self.running_processes.items()):
            try:
                self._kill_process_tree(process)
            except Exception as e:
                logger.error(f"Failed to cleanup process {pid}: {e}")
        self.running_processes.clear()
    
    @staticmethod
    def check_command_exists(command: str) -> bool:
        """Check if a command exists in the system PATH"""
        try:
            result = subprocess.run(
                ['which', command] if os.name != 'nt' else ['where', command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_command_version(command: str) -> Optional[str]:
        """Get version string of a command"""
        try:
            for flag in ['--version', '-version', 'version', '-v']:
                result = subprocess.run(
                    [command, flag],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip().split('\n')[0]
        except Exception:
            pass
        return None
