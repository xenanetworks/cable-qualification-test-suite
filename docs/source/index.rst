=====================================================
Xena Cable Qualification Test Methodology
=====================================================

Welcome to the Xena Cable Qualification Test Methodology. This automated framework evaluates cable quality and performance through:

* PRBS-based BER Testing
* Pre-FEC and Post-FEC BER Measurement
* Latency and Frame Loss Testing (RFC 2544)
* Signal Integrity Verification (SIV) and Signal Integrity Diagrams
* Transceiver Information Logging
* TX Equalization Settings Logging

This methodology provides essential data for informed cable selection and optimization. The test is performed using the following equipment:

* Teledyne LeCroy Xena Z800 Freya

.. important:: 

    Current version requires all the test ports are on the same chassis. Multi-chassis support will be added in the future.

-----------

.. toctree::
    :maxdepth: 1
    :caption: Table of Content

    step_by_step
    introduction
    load_tx_eq
    tcvr_info
    read_tx_eq
    siv_info
    fec_ber_test
    prbs_ber_test
    latency_frameloss_test


