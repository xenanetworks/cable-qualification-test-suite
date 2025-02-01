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
from typing_extensions import List, Any
from misc import *
from scripts.subtests import *
from models import *
import yaml, json
from pathlib import Path
import logging, sys, os

#---------------------------
# CableQualificationTest
#---------------------------

class CableQualificationTest:
    def __init__(self, chassis: str, test_config_file: str, username: str = "CableQualificationTest", password: str = "xena", tcp_port: int = 22606, enable_logging: bool = False):
        self.chassis = chassis
        self.username = username
        self.password = password
        self.tcp_port = tcp_port
        self.enable_logging = enable_logging
        self.test_config_file = test_config_file
        self.test_config: CableQualificationTestConfig
        self.tester_obj: testers.L23Tester

        script_dir = Path(__file__).resolve().parent
        file_path = script_dir / test_config_file
        self.load_test_config(str(file_path))

    async def connect(self):
        self.tester_obj = await testers.L23Tester(host=self.chassis, username=self.username, password=self.password, port=self.tcp_port, enable_logging=self.enable_logging)

    async def disconnect(self):
        await self.tester_obj.session.logoff()

    def load_test_config(self, test_config_file: str):
        with open(test_config_file, "r") as f:
            test_config_dict = yaml.safe_load(f)
            test_config_value = json.dumps(test_config_dict["test_config"])
            self.test_config = CableQualificationTestConfig.model_validate_json(test_config_value)

            # configure basic logger
            logging.basicConfig(
                format="%(asctime)s  %(message)s",
                level=logging.DEBUG,
                handlers=[
                    logging.FileHandler(filename=self.log_filename, mode="a"),
                    logging.StreamHandler()]
                )
    
    @property
    def port_pair_list(self):
        __list = []
        for port_pair in self.test_config.port_pair_list:
            __list.append(port_pair.model_dump())
        return __list
    
    @property
    def module_list(self):
        return self.test_config.module_list
    
    @property
    def port_speed(self):
        return self.test_config.port_speed
    
    @property
    def module_media_tga(self):
        return enums.MediaConfigurationType[self.test_config.module_media_tga]
    
    @property
    def module_media_l1(self):
        return enums.MediaConfigurationType[self.test_config.module_media_l1]
    
    @property
    def report_filename(self):
        return self.test_config.csv_report_filename
    
    @property
    def log_filename(self):
        return self.test_config.log_filename
    
    @property
    def logger_name(self):
        return self.log_filename.replace(".log", "")
    
    @property
    def prbs_test_config(self):
        return self.test_config.prbs_test_config.model_dump()
    
    @property
    def fec_test_config(self):
        return self.test_config.fec_test_config.model_dump()
    
    @property
    def latency_frameloss_test_config(self):
        return self.test_config.latency_frameloss_test_config.model_dump()

    async def run_prbs_test(self):
        await prbs_test(self.tester_obj, self.port_pair_list, self.report_filename, self.logger_name, self.prbs_test_config)

    async def run_fec_test(self):
        await fec_test(self.tester_obj, self.port_pair_list, self.report_filename, self.logger_name, self.prbs_test_config)

    async def run_latency_frame_loss_test(self):
        await latency_frame_loss_test(self.tester_obj, self.port_pair_list, self.report_filename, self.logger_name, self.latency_frameloss_test_config)

    async def get_siv_sample(self):
        await siv_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=False)

    async def get_siv_histogram(self):
        await siv_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=True)

    async def get_tcvr_basic_info(self):
        await tcvr_basic_info(self.tester_obj, self.port_pair_list, self.report_filename, self.logger_name)

    async def change_module_media_tg(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_tga, self.port_speed, self.logger_name,)

    async def change_module_media_l1(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_l1, self.port_speed, self.logger_name,)
    
    async def run(self):
        await self.connect()
        await self.change_module_media_l1()
        await self.get_tcvr_basic_info()
        await self.run_prbs_test()
        await self.run_fec_test()
        await self.get_siv_sample()
        await self.get_siv_histogram()
        await self.change_module_media_tg()
        await self.run_latency_frame_loss_test()
        await self.disconnect()


#---------------------------
# main()
#---------------------------
async def main():
    stop_event = asyncio.Event()
    try:
        test = CableQualificationTest("10.165.136.60", "test_config.yml")
        await test.run()
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    asyncio.run(main())
