"""Demonstrate basic Unix process, file, device, and error operations."""

import os
import subprocess
from pathlib import Path


TEST_FILE = Path("lab1_controlled_test.txt")


def demonstrate_process_creation() -> None:
    """Create a child, run a harmless command, and wait for it."""
    print("=== PROCESS EVIDENCE ===")
    print(f"Parent PID: {os.getpid()}")
    print(f"Parent PPID: {os.getppid()}")

    child_pid = os.fork()
    if child_pid == 0:
        try:
            print(f"Child PID: {os.getpid()}", flush=True)
            print(f"Child PPID: {os.getppid()}", flush=True)

            command = ["uname", "-s"]
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            print(
                f"Child command: {' '.join(command)} -> "
                f"{result.stdout.strip()}",
                flush=True,
            )
        except (OSError, subprocess.SubprocessError) as error:
            print(f"Child command error: {error}", flush=True)
            os._exit(1)
        os._exit(0)

    completed_pid, status = os.waitpid(child_pid, 0)
    if os.WIFEXITED(status):
        exit_code = os.WEXITSTATUS(status)
        print(f"Waited for child PID: {completed_pid}")
        print(f"Child exit status: {exit_code}")
    else:
        print(f"Child PID {completed_pid} did not exit normally")


def demonstrate_file_operations() -> None:
    """Create, write, read, and close a controlled test file."""
    print("\n=== FILE EVIDENCE ===")
    content = "Controlled file operation completed.\n"
    file_handle = None
    try:
        file_handle = TEST_FILE.open("w", encoding="utf-8")
        file_handle.write(content)
        file_handle.close()
        file_handle = None
        print(f"Created and wrote: {TEST_FILE}")

        file_handle = TEST_FILE.open("r", encoding="utf-8")
        read_content = file_handle.read()
        print(f"Read content: {read_content.strip()}")
    except OSError as error:
        print(f"File operation error for {TEST_FILE}: {error}")
    finally:
        if file_handle is not None:
            file_handle.close()
        try:
            TEST_FILE.unlink()
            print(f"Closed and removed controlled file: {TEST_FILE}")
        except FileNotFoundError:
            pass
        except OSError as error:
            print(f"Cleanup error for {TEST_FILE}: {error}")


def demonstrate_device_interface() -> None:
    """Inspect the writable Unix null device without retaining data."""
    print("\n=== DEVICE INTERFACE EVIDENCE ===")
    device_path = Path("/dev/null")
    device_handle = None
    try:
        device_handle = device_path.open("w", encoding="utf-8")
        device_handle.write("discarded device test\n")
        print(f"Opened, wrote to, and inspected: {device_path}")
    except OSError as error:
        print(f"Device interface error for {device_path}: {error}")
    finally:
        if device_handle is not None:
            device_handle.close()
            print(f"Closed device interface: {device_path}")


def demonstrate_invalid_path() -> None:
    """Show clear handling for an expected failed file operation."""
    print("\n=== ERROR-HANDLING EVIDENCE ===")
    invalid_path = Path("missing_directory_for_lab1") / "missing_file.txt"
    try:
        invalid_path.open("r", encoding="utf-8")
    except OSError as error:
        print(f"Expected invalid-path error for {invalid_path}: {error}")


def main() -> None:
    demonstrate_process_creation()
    demonstrate_file_operations()
    demonstrate_device_interface()
    demonstrate_invalid_path()


if __name__ == "__main__":
    main()