Step-by-Step
=============================

Prerequisite
-------------

1. Make sure you have ``Python >= 3.11`` installed on your system. If not, download and install it from `Python.org <https://www.python.org/downloads/>`_.
2. Make sure you have pip installed on your system. This allows you to install Python packages from the Python Package Index (PyPI). To test if you have pip installed, run the following command: ``pip list``. If you have pip installed, you will see a list of installed packages. 
3. Download the scripts from `cable-qualification-test-suite/scripts/ <https://github.com/xenanetworks/cable-qualification-test-suite/tree/main/scripts>`_

    * cable_qualification.py: This is the main script that will be used to run the test.
    * requirements.txt: This file contains the required packages to run the test.
    * subtests.py: This file contains the subtests that will be used in the main script.
    * reportgen.py: This file contains the functions to generate the test csv report.
    * misc.py: This file contains the helper functions that will be used in the main script.

3. Install the required packages using the following command: ``pip install -r requirements.txt``. This will install the following packages:

    * ``xoa-driver>=2.9.3``
    * ``matplotlib>=3.9.2``

.. seealso::
    
    Read `install xoa-driver <https://docs.xenanetworks.com/projects/xoa-python-api/en/latest/getting_started/index.html>`_ for details about installing ``xoa-driver``.

.. important::

    You can either install the Python packages globally or in a virtual environment. It is recommended to use a virtual environment to avoid conflicts with other Python projects. Read `Python Virtual Environment <https://docs.python.org/3/library/venv.html>`_ for more information.


Run Test
---------

1. Open the ``cable_qualification.py`` and change the global variables to match your setup.

.. code-block:: python

    #---------------------------
    # GLOBAL VARIABLES
    #---------------------------

    CHASSIS_IP = "10.10.10.10"    # This is the IP address of the chassis
    USERNAME = "xoa"                # This is the username to login to the chassis and port reservation
    PASSWORD = "xena"               # This is the password to login to the chassis
    TCPPORT= 22606                  # This is the TCP port to login to the chassis
    REPORT_FILENAME = "cable_qualification_test_report.csv" # This is the filename of the report

    MODULE_LIST = [3, 6]    # This is the list of modules to be used in the test
    PORT_PAIRS = [
        {"tx": "3/0", "rx": "6/0"}, # This is the port pair to be tested
        {"tx": "3/1", "rx": "6/1"}, # This is the port pair to be tested
    ]

    PRBS_TEST_CONFIG = {
        "duration": 10,                             # Duration of the test in seconds
        "polynomial": enums.PRBSPolynomial.PRBS31,  # PRBS polynomial to be used
        }
    FEC_TEST_CONFIG = {
        "duration": 10,                             # Duration of the test in seconds
        }
    LATENCY_FRAMELOSS_TEST_CONFIG = {
        "start_rate": 0.1,                          # Start traffic rate (0.1 = 10%)
        "end_rate": 1.0,                            # End traffic rate (1.0 = 100%)
        "step_rate": 0.2,                           # Step traffic rate (0.1 = 10%)
        "packet_sizes": [128],                      # Packet sizes to be tested (bytes)
        "duration": 10,                             # Duration of each test in seconds
        }


* ``CHASSIS_IP``: This is the IP address of the chassis. Make sure to change it to match your setup.
* ``USERNAME``: This is the username to login to the chassis. It is the username used for port reservation.
* ``PASSWORD``: This is the password to login to the chassis. Default password is ``xena``. Change it if you have a different password.
* ``TCPPORT``: This is the TCP port to login to the chassis. Default port is ``22606``. Change it if you have a different TCP port number.
* ``REPORT_FILENAME``: This is the filename of the CSV report. Change it to the desired filename.

* ``MODULE_LIST``: This is the list of modules to be used in the test. Change it to match your setup.
* ``PORT_PAIRS``: This is the list of port pairs to be tested. One port pair is defined as unidirectionl topology in a dictionary with the ``tx`` and ``rx`` keys. Change it to match your setup.
* ``PRBS_TEST_CONFIG``: This is the configuration for the PRBS test. It applies to all the port pairs. Change it to match your setup.
* ``FEC_TEST_CONFIG``: This is the configuration for the FEC test. It applies to all the port pairs. Change it to match your setup.
* ``LATENCY_FRAMELOSS_TEST_CONFIG``: This is the configuration for the Latency and Frame Loss test. It applies to all the port pairs. Change it to match your setup.



2. Open a terminal/command prompot, go to the ``script/`` folder and run the script using the following command ``python cable_qualification.py``.

    * Your terminal will show the progress of the test and save the outputs into a log file.
    * The script will generate a CSV report file with the test results. The report will be saved in the same folder as the script.
    * The script will also generate a SIV plot PNG file for all ports in the ``PORT_PAIRS``. The plot PNG files will be saved in the same folder as the script.