'''Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.'''

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
        
