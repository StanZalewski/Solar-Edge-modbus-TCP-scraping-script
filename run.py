import subprocess
import time
import os

RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"


# Path to your virtual environment
VENV_PATH = "./venv"

def run_scraper(display,meter):
    try:
        # Get the Python interpreter from the virtual environment
        python_executable = os.path.join(VENV_PATH, "bin", "python")
        # Run the scraper.py script using the virtual environment's Python
        subprocess.run([python_executable, "scraper.py", str(display), str(meter)], check=True)
        
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

if __name__ == "__main__":
    display = False
    additionalMeter = True
    while True:
        if display:
            print(f"{BOLD}{YELLOW}>>> Running scraper.py{RESET}")
        run_scraper(display,additionalMeter)
        if display:
            print(f"{BOLD}{YELLOW}>>> Sleep for 10s{RESET}\n")
        time.sleep(5)
        
