Step-by-Step
=============================

Prerequisite
-------------

1. Make sure you have ``Python >= 3.9`` installed on your system. If not, download and install it from `Python.org <https://www.python.org/downloads/>`_.
2. Make sure you have pip installed on your system. This allows you to install Python packages from the Python Package Index (PyPI). To test if you have pip installed, run the following command: ``pip list``. If you have pip installed, you will see a list of installed packages. 
3. Download the scripts from `cable-qualification-test-suite/scripts/ <https://github.com/xenanetworks/cable-qualification-test-suite/tree/main/scripts>`_

    * cable_qualification.py: This is the main script that will be used to run the test.
    * requirements.txt: This file contains the required packages to run the test.
    * subtests.py: This file contains the subtests that will be used in the main script.
    * reportgen.py: This file contains the functions to generate the test csv report.
    * misc.py: This file contains the helper functions that will be used in the main script.

3. Install the required packages using the following command: ``pip install -r requirements.txt``. This will install the following packages:

    * ``tdl-xoa-driver>=1.1.0``
    * ``matplotlib>=3.9.2``
    * ``pyyaml>=6.0.1``
    * ``pydantic>=2.0``

.. seealso::
    
    Read `install tdl-xoa-driver <https://docs.xenanetworks.com/projects/tdl-xoa-driver/en/latest/getting_started/index.html>`_ for details about installing ``tdl-xoa-driver``.

.. important::

    You can either install the Python packages globally or in a virtual environment. It is recommended to use a virtual environment to avoid conflicts with other Python projects. Read `Python Virtual Environment <https://docs.python.org/3/library/venv.html>`_ for more information.


Run Test
---------

1. Open the ``/script/test_config.yml`` and change the configuraiton to match your setup.

.. code-block:: yaml

    test_config:
        chassis_ip: "10.10.10.10"
        username: "CableQualificationTest"
        password: "xena"
        tcp_port: 22606
        module_list:
            - 3
            - 6
        port_speed: "1x800G"
        module_media_tga: "QSFPDD800"
        module_media_l1: "QSFPDD800_ANLT"
        port_pair_list:
            - tx: "3/0"
              rx: "6/0"
        csv_report_filename: "cable_qualification_test_report.csv"
        log_filename: "cable_qualification_test.log"
        prbs_test_config:
            duration: 10
            polynomial: "PRBS31"
        fec_test_config:
            duration: 10
        latency_frameloss_test_config:
            duration: 10
            start_rate: 0.1
            end_rate: 1.0
            step_rate: 0.1
            packet_sizes:
                - 64

* ``chassis_ip``: IP address of the chassis.
* ``username``: Username used to connect to the chassis. This name is also used to reserve the ports.
* ``password``: Password used to connect to the chassis. Default password is "xena".
* ``tcp_port``: TCP port used to connect to the chassis. Default port is 22606.
* ``module_list``: List of modules that you use in the test.
* ``port_speed``: Speed of the ports, allowed values are:

  * "1x800G", "2x400G", "4x200G", "8x100G"
  * "1x400G", "2x200G", "4x100G", "8x50G"

* ``module_media_tga``: Media type of the module used by Latency and Frame Loss Test. Allowed values are:

  * "QSFPDD800"
  * "QSFP112"
  * "OSFP800"
  * "QSFPDD"

* ``module_media_l1``: Media type of the module used by FEC BER test, PRBS test, and SIV information. Allowed values are:

  * "QSFPDD800_ANLT"
  * "QSFP112_ANLT"
  * "OSFP800_ANLT"
  * "QSFPDD_ANLT"

* ``port_pair_list``: List of port pairs that you want to test. Each port pair should have a ``tx`` and ``rx`` port. The port format is ``<module>/<port>``.

* ``csv_report_filename``: Name of the CSV report file.

* ``log_filename``: Name of the log file.

* ``prbs_test_config``: Configuration for the PRBS test.

  * ``duration``: Duration of the test in seconds.
  * ``polynomial``: PRBS polynomial used in the test. Allowed values are:

    * "PRBS31"
    * "PRBS13"

* ``fec_test_config``: Configuration for the FEC BER test.

  * ``duration``: Duration of the test in seconds.

* ``latency_frameloss_test_config``: Configuration for the Latency and Frame Loss Test.

  * ``duration``: Duration of the test in seconds.
  * ``start_rate``: Start rate of the test in fraction.
  * ``end_rate``: End rate of the test in fraction.
  * ``step_rate``: Step rate of the test in fraction.
  * ``packet_sizes``: List of packet sizes in bytes used in the test.

2. Open the ``cable_qualification.py``. An example of how to use the ``class CableQualificationTest`` is show in ``main()`` function. You can modify the ``main()`` function to match your setup. You can also import ``class CableQualificationTest`` into your own script and use it to run the test.

.. code-block:: python

    async def main():
        stop_event = asyncio.Event()
        try:
            test = CableQualificationTest("test_config.yml")
            await test.run()
        except KeyboardInterrupt:
            stop_event.set()

    if __name__ == "__main__":
        asyncio.run(main())

3. Open a terminal/command prompot, go to the ``script/`` folder and run the script using the following command ``python cable_qualification.py``.

    * Your terminal will show the progress of the test and save the outputs into a log file.
    * The script will generate a CSV report file with the test results. The report will be saved in the same folder as the script.
    * The script will also generate a SIV plot PNG files for all ports in the ``PORT_PAIRS``. The plot PNG files will be saved ``script/`` folder.