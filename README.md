# Capstone Project - Server Code
Authors:
  - Matthew Rizzo - rizzo.ma@northeastern.edu
  - Nicholas Rizzo - rizzo.n@northeastern.edu
  - Aman Kaur - kaur.am@northeastern.edu
  - Annie Waye - waye.a@northeastern.edu
  - Liz Woodwell - woodwell.e@northeastern.edu
  - Tyler Royere - royere.t@northeastern.edu

## Server Web Application APIs

see [api.md](./src/frontend/static/md/api.md) for routes to interact with web-app database interface


## Creating and Running the Project
* libraries - see [install/requirements.txt](install/requirements.txt)
  * However, existing scripts will handle the installation / setup of these libraries (assuming you can run the [install/setup.sh](install/setup.sh) or [install/setup.bat](install/setup.bat) files)
  * Feel free to look at the list within the text file
* Software
  * MySQLWorkbench + MySQLServer
    * Used as in class, to create the schema using the complete dump file
  * Python version 3.9 (python3.9)
    * Download Page: https://www.python.org/downloads/release/python-390/
    * Please select the option at the bottom of the page that matches your Operating System

### Setup Steps:
1. (For Windows Only) Download [Python3.9](https://www.python.org/downloads/release/python-390/)
   1. **Note:** Using a different / earlier version of python will result in the code not working. Please be sure your version is python 3.9.
   2. Please run `py -0` to see a list of installed python versions.
      1. Please confirm that you see `"-3.9-64 *"` or `"-3.9-64 "`. If not, the installation was not successful.
   3. If you are using Ubuntu or a Debian distribution, this install will be handled for you in [install/setup.sh](install/setup.sh).
2. Run setup scripts. Pick the correct one based on your operating system:
   * Windows: [install/setup.bat](install/setup.bat)
     * Note: this can be done through command prompt OR just double clicking on the file in `File Explorer`
   * Ubuntu/Debian/Windows Git-Bash: [install/setup.sh](install/setup.sh)
   * This handles the complete setup of a virtual environment with the correct libraries/packages for the project.
   * The virtual environment will live in `/capstone-venv` relative to the top level of this project
   * Depending on the operating system, the exact location of the python interpreter will change. However, the start scripts will handle that, and you do not need to figure it out.

### Running / Starting the Application Server:
1. Windows: [start.bat](start.bat)
   1. Note: this can be done through command prompt OR just double clicking on the file in `File Explorer`
   2. The application can also be started by clicking on the file itself in the file explorer.
2. Ubuntu/Debian/Windows Git-Bash: [start.sh](start.sh)
3. Each script will call `main.py` using the python virtual environment setup.
4. HTTP Routes can be querried using the following base url:
   1. `http://localhost:31025/`
   2. When the server starts it will also print this url in case port 31025 is taken
5. **NOTE On Windows:**
   1. The first time the program is run, Windows Firewall might block the application, please click "Allow Access". This issue should not happen again.
   2. When ending the program please do `Ctrl+C` then respond to `Terminate batch job (Y/N)?` with `y` and click enter.
