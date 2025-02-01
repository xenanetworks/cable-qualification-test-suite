from pydantic import BaseModel

class LatencyFrameLossTestConfig(BaseModel):
    start_rate: float
    end_rate: float
    step_rate: float
    packet_sizes: list[int]
    duration: int

class FECTestConfig(BaseModel):
    duration: int

class PRBSTestConfig(BaseModel):
    duration: int
    polynomial: str

class PortPair(BaseModel):
    tx: str
    rx: str

class CableQualificationTestConfig(BaseModel):
    csv_report_filename: str
    log_filename: str
    module_list: list[int]
    port_pair_list: list[PortPair]
    port_speed: str
    module_media_tga: str
    module_media_l1: str
    prbs_test_config: PRBSTestConfig
    fec_test_config: FECTestConfig
    latency_frameloss_test_config: LatencyFrameLossTestConfig