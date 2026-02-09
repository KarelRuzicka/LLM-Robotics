# LLM-Robotics





# Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/KarelRuzicka/LLM-Robotics.git
   cd LLM-Robotics
   ```
2. (Optional) Create a virtual environment (python venv or conda):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux
    `venv\Scripts\activate` # On Windows
    ```
3. (Optional) If you plan to use the premade control scripts for the real/simulated Unitree G1 robots, manually install the necessary dependencies:
    - unitree_sdk2py
    - teleimager
    ```bash
    cd {{package_location}}
    pip install -e .
    ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```