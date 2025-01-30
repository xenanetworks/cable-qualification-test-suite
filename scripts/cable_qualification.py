################################################################
#
#            CABLE QUALIFICATION TEST METHODOLOGY
#
# 
#
################################################################

import asyncio

from xoa_driver import testers
from xoa_driver import modules
from xoa_driver import ports
from xoa_driver import enums
from xoa_driver import utils
from xoa_driver.hlfuncs import mgmt
from xoa_driver.misc import Hex
import logging, sys, os
from typing_extensions import List, Any
from misc import *
from subtests import *

#---------------------------
# GLOBAL VARIABLES
#---------------------------

CHASSIS_IP = "10.165.136.60" # This is the IP address of the chassis
USERNAME = "xoa"        # This is the username to login to the chassis
PASSWORD = "xena"        # This is the password to login to the chassis
TCPPORT= 22606          # This is the TCP port to login to the chassis
REPORT_FILENAME = "cable_qualification_test_report.csv"

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

#---------------------------
# cable_qualification_test
#---------------------------
async def cable_qualification_test(chassis: str, username: str, password: str, tcp_port: int, port_pair_list: List[Any], report_filename: str):
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    # configure basic logger
    logging.basicConfig(
        format="%(asctime)s  %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename=f"cable_qualification_test.log", mode="a"),
            logging.StreamHandler()]
        )
    # 1. Change Freya module media to L1 mode, where SIV is supported
    await change_module_media(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        module_list=MODULE_LIST,
        logger_name="cable_qualification_test",
        media=enums.MediaConfigurationType.QSFPDD800_ANLT,
        port_speed="2x400G"
    )
    # 2. Get basic information of the transceiver
    await tcvr_basic_info(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test")
    # 3. Run PRBS test
    await prbs_test(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=PRBS_TEST_CONFIG)
    # 4. Run FEC test
    await fec_test(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=FEC_TEST_CONFIG)
    # 5. Get SIV information
    await siv_info(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        port_pair_list=port_pair_list,
        logger_name="cable_qualification_test")
    # 6. Change Freya module media to TG mode, where traffic latency and frame loss is supported
    await change_module_media(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        module_list=MODULE_LIST,
        logger_name="cable_qualification_test",
        media=enums.MediaConfigurationType.QSFPDD800,
        port_speed="2x400G"
    )
    # 7. Run latency and frame loss test
    await latency_frame_loss_test(
        chassis=chassis,
        username=username,
        password=password,
        tcp_port=tcp_port,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=LATENCY_FRAMELOSS_TEST_CONFIG)
    

async def main():
    stop_event = asyncio.Event()
    try:
        await cable_qualification_test(
            chassis=CHASSIS_IP,
            username=USERNAME,
            password=PASSWORD,
            tcp_port=TCPPORT,
            port_pair_list=PORT_PAIRS,
            report_filename=REPORT_FILENAME
        )´
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    asyncio.run(main())
