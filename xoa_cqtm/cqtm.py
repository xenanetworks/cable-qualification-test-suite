# *************************************
# author: leonard.yu@teledyne.com
# *************************************

import asyncio
from xoa_driver import testers
from xoa_driver import enums
from .utils import *
from .subtests import *
from .models import *
import yaml, json
from pathlib import Path
import logging

# *************************************************************************************
# class: XenaCableQualification
# description: This class provides an automated cable qualification framework that 
# uses a combination of various measurements to benchmark the quality of a cable. 
# The measurements include PRBS-based BER testing, FEC testing, SIV, TCVR basic info, 
# latency and frame loss testing.
# *************************************************************************************

class XenaCableQualification:
    """This class provides an automated cable qualification framework that uses a combination of various measurements to benchmark the quality of a cable. The measurements include PRBS-based BER testing, FEC testing, SIV, TCVR basic info, latency and frame loss testing.
    """
    def __init__(self, test_config_file: str, enable_comm_trace: bool = False):
        self.enable_comm_trace = enable_comm_trace
        self.test_config_file = test_config_file
        self.test_config: CableQualificationTestConfig
        self.tester_obj: testers.L23Tester

        self.load_test_config(test_config_file)

    async def connect(self):
        self.tester_obj = await testers.L23Tester(host=self.chassis_ip, username=self.username, password=self.password, port=self.tcp_port, enable_logging=self.enable_comm_trace)

    async def disconnect(self):
        await self.tester_obj.session.logoff()

    def load_test_config(self, test_config_file: str):
        with open(test_config_file, "r") as f:
            test_config_dict = yaml.safe_load(f)
            test_config_value = json.dumps(test_config_dict["test_config"])
            self.test_config = CableQualificationTestConfig.model_validate_json(test_config_value)

    async def create_report_dir(self):
        self.path = await create_report_dir(self.tester_obj, self.port_pair_list)
        # configure basic logger
        logging.basicConfig(
            format="%(asctime)s  %(message)s",
            level=logging.DEBUG,
            handlers=[
                logging.FileHandler(filename=os.path.join(self.path, self.log_filename), mode="a"),
                logging.StreamHandler()]
            )
    
    @property
    def chassis_ip(self):
        return self.test_config.chassis_ip
    
    @property
    def username(self):
        return self.test_config.username
    
    @property
    def password(self):
        return self.test_config.password
    
    @property
    def tcp_port(self):
        return self.test_config.tcp_port
    
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
        return enums.MediaConfigurationType[self.test_config.module_media]
    
    @property
    def module_media_l1(self):
        return enums.MediaConfigurationType[self.test_config.module_media+"_ANLT"]
    
    @property
    def report_filepathname(self):
        return os.path.join(self.path, self.test_config.csv_report_filename)
    
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
    
    @property
    def host_tx_eq(self):
        return self.test_config.host_tx_eq.model_dump()
    
    @property
    def module_tx_eq(self):
        return self.test_config.module_tx_eq.model_dump()

    async def run_prbs_test(self):
        await prbs_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.prbs_test_config)

    async def run_fec_test(self):
        await fec_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.prbs_test_config)

    async def run_latency_frame_loss_test(self):
        await latency_frame_loss_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.latency_frameloss_test_config)

    async def get_siv_sample(self):
        await signal_integrity_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=False, path=self.path)

    async def get_siv_histogram(self):
        await signal_integrity_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=True, path=self.path)

    async def get_tcvr_basic_info(self):
        await tcvr_basic_info(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name)

    async def change_module_media_tg(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_tga, self.port_speed, self.logger_name,)

    async def change_module_media_l1(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_l1, self.port_speed, self.logger_name,)

    async def read_host_tx_eq(self):
        await read_host_tx_eq(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name)

    async def load_host_tx_eq(self):
        await load_host_tx_eq(self.tester_obj, self.port_pair_list, self.logger_name, self.host_tx_eq)

    async def load_module_tx_eq(self):
        await load_module_tx_eq(self.tester_obj, self.port_pair_list, self.logger_name, self.module_tx_eq)

    async def read_module_tx_eq(self):
        await read_module_tx_eq(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name)
    
    async def run(self):
        await self.connect()
        await self.create_report_dir()
        await self.change_module_media_l1()
        await self.get_tcvr_basic_info()
        await self.load_host_tx_eq()
        await self.read_host_tx_eq()
        await self.load_module_tx_eq()
        await self.read_module_tx_eq()
        await self.run_prbs_test()
        await self.run_fec_test()
        await self.get_siv_sample()
        await self.get_siv_histogram()
        await self.change_module_media_tg()
        await self.load_host_tx_eq()
        await self.load_module_tx_eq()
        await self.run_latency_frame_loss_test()
        await self.disconnect()
