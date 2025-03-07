################################################################
#
#            CABLE QUALIFICATION TEST METHODOLOGY
#
################################################################

import asyncio

from xoa_driver import testers
from xoa_driver import enums
from misc import *
from subtests import *
from models import *
import yaml, json
from pathlib import Path
import logging

#-----------------------------
# class CableQualificationTest
#-----------------------------

class CableQualificationTest:
    def __init__(self, test_config_file: str, enable_comm_trace: bool = False):
        self.enable_comm_trace = enable_comm_trace
        self.test_config_file = test_config_file
        self.test_config: CableQualificationTestConfig
        self.tester_obj: testers.L23Tester

        script_dir = Path(__file__).resolve().parent
        file_path = script_dir / test_config_file
        self.load_test_config(str(file_path))

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
    def topology(self):
        return self.test_config.topology
    
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
    async def port_pair_list(self):
        __list = []
        for port_pair in self.test_config.topology:
            

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

    async def run_prbs_test(self):
        await prbs_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.prbs_test_config)

    async def run_fec_test(self):
        await fec_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.prbs_test_config)

    async def run_latency_frame_loss_test(self):
        await latency_frame_loss_test(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name, self.latency_frameloss_test_config)

    async def get_siv_sample(self):
        await siv_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=False, path=self.path)

    async def get_siv_histogram(self):
        await siv_info(self.tester_obj, self.port_pair_list, self.logger_name, should_histogram=True, path=self.path)

    async def get_tcvr_basic_info(self):
        await tcvr_basic_info(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name)

    async def change_module_media_tg(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_tga, self.port_speed, self.logger_name,)

    async def change_module_media_l1(self):
        await change_module_media(self.tester_obj, self.module_list, self.module_media_l1, self.port_speed, self.logger_name,)

    async def get_tx_tap_info(self):
        await tx_tap_info(self.tester_obj, self.port_pair_list, self.report_filepathname, self.logger_name)
    
    async def run(self):
        await self.connect()
        await self.create_report_dir()
        await self.change_module_media_l1()
        await self.get_tcvr_basic_info()
        await self.get_tx_tap_info()
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
        test = CableQualificationTest("test_config.yml")
        await test.run()
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    asyncio.run(main())
