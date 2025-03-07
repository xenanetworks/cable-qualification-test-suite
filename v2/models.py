# ***********************************************************************************************
# this library file contains test configuration models for cable quality test
# ***********************************************************************************************

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

class HostTXEQ(BaseModel):
    pre3: int
    pre2: int
    pre: int
    main: int
    post: int

class PortConfig(BaseModel):
    chassis_ip: str
    password: str
    tcp_port: int
    port_idx: str
    port_speed: str
    module_media: str
    host_tx_eq: HostTXEQ
    
class PortPair(PortConfig):
    tx: PortConfig
    rx: PortConfig

class CableQualificationTestConfig(BaseModel):
    username: str
    topology: list[PortPair]
    csv_report_filename: str
    log_filename: str
    prbs_test_config: PRBSTestConfig
    fec_test_config: FECTestConfig
    latency_frameloss_test_config: LatencyFrameLossTestConfig