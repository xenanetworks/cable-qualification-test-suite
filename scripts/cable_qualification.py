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
CHASSIS_IP = "10.165.136.60"
USERNAME = "xoa"
TOPOLOGY = [
    {"tx": "3/0", "rx": "6/0"},
    {"tx": "3/1", "rx": "6/1"},
]
MODULE_LIST = [3, 6]
REPORT_FILENAME = "cable_qualification_test_report.csv"
PRBS_CONFIG = {
    "duration": 10,
    "polynomial": enums.PRBSPolynomial.PRBS31,
    }
FEC_CONFIG = {
    "duration": 10,
    }
LATENCY_FRAME_LOSS_CONFIG = {
    "start_rate": 0.1,
    "end_rate": 1.0,
    "step_rate": 0.2,
    "packet_sizes": [128],
    "duration": 5,
    }

#---------------------------
# cable_qualification_test
#---------------------------
async def cable_qualification_test(chassis: str, username: str, port_pair_list: List[Any], report_filename: str):
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
    
    await change_module_media(
        chassis=chassis,
        username=username,
        module_list=MODULE_LIST,
        logger_name="cable_qualification_test",
        media=enums.MediaConfigurationType.QSFPDD800_ANLT,
        port_speed="2x400G"
    )
    await tcvr_basic_info(
        chassis=chassis,
        username=username,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test")
    await prbs_test(
        chassis=chassis,
        username=username,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=PRBS_CONFIG)
    await fec_test(
        chassis=chassis,
        username=username,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=FEC_CONFIG)
    await siv_info(
        chassis=chassis,
        username=username,
        port_pair_list=port_pair_list,
        logger_name="cable_qualification_test")
    await change_module_media(
        chassis=chassis,
        username=username,
        module_list=MODULE_LIST,
        logger_name="cable_qualification_test",
        media=enums.MediaConfigurationType.QSFPDD800,
        port_speed="2x400G"
    )
    await latency_frame_loss_test(
        chassis=chassis,
        username=username,
        port_pair_list=port_pair_list,
        report_filename=report_filename,
        logger_name="cable_qualification_test",
        test_config=LATENCY_FRAME_LOSS_CONFIG)
    

async def main():
    stop_event = asyncio.Event()
    try:
        await cable_qualification_test(
            chassis=CHASSIS_IP,
            username=USERNAME,
            port_pair_list=TOPOLOGY,
            report_filename=REPORT_FILENAME
        )
        
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    asyncio.run(main())
