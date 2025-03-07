Step-by-Step
=============================

Prerequisite
-------------

1. Install ``tdl-xoa-driver``. Read `install tdl-xoa-driver <https://docs.xenanetworks.com/projects/tdl-xoa-driver/en/latest/getting_started/index.html>`_ for details.
2. Download the library and the test script together with the test configuraiton from `Cable Qualification Test Methodology GitHub Repository <https://github.com/xenanetworks/cable-qualification-test-suite/>`_
3. Install the required packages using the following command: ``pip install -r requirements.txt``. This will install the following packages:

Change Test Configuration
-------------------------

Go to ``test/`` directory, change the ``test_config.yml`` to meet your test setup and requirements.

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
        module_media: "QSFPDD800"
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
                - 128
        host_tx_eq:
            enable: true
            pre3: 0
            pre2: 0
            pre: 12
            main: 42
            post: 0
        module_tx_eq:
            enable: true
            pre: 3
            main: 1
            post: 3

* ``chassis_ip``: IP address of the chassis.
* ``username``: Username used to connect to the chassis. This name is also used to reserve the ports.
* ``password``: Password used to connect to the chassis. Default password is "xena".
* ``tcp_port``: TCP port used to connect to the chassis. Default port is 22606.
* ``module_list``: List of modules that you use in the test.
* ``port_speed``: Speed of the ports, allowed values are:

  * "1x800G", "2x400G", "4x200G", "8x100G"
  * "1x400G", "2x200G", "4x100G", "8x50G"

* ``module_media``: Module media type. Allowed values are:

  * "QSFPDD800"
  * "QSFP112"
  * "OSFP800"
  * "QSFPDD"

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

* ``host_tx_eq``: Configuration for the host TX equalization.
* ``module_tx_eq``: Configuration for the module TX equalization.

Run the Test
------------

Then, still in ``test/`` directory, run ``python test.py`` to start the test. The test log and results will be saved in the log file specified in the test configuration and also printed on the console.

* Your terminal will show the progress of the test and save the outputs into a log file.
* The script will generate a CSV report file with the test results. The report will be saved in the same folder as the script.
* The script will also generate a SIV plot PNG files for all ports in the ``PORT_PAIRS``. The plot PNG files will be saved ``test/`` folder.