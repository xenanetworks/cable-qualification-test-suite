# *************************************
# author: leonard.yu@teledyne.com
# *************************************

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

class HostTxEq(BaseModel):
    enable: bool
    pre3: int
    pre2: int
    pre: int
    main: int
    post: int

class ModuleTxEq(BaseModel):
    enable: bool
    pre: int
    main: int
    post: int

class CableQualificationTestConfig(BaseModel):
    chassis_ip: str
    username: str
    password: str
    tcp_port: int
    csv_report_filename: str
    log_filename: str
    module_list: list[int]
    port_pair_list: list[PortPair]
    port_speed: str
    module_media: str
    prbs_test_config: PRBSTestConfig
    fec_test_config: FECTestConfig
    latency_frameloss_test_config: LatencyFrameLossTestConfig
    host_tx_eq: HostTxEq
    module_tx_eq: ModuleTxEq