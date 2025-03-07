# *************************************
# author: leonard.yu@teledyne.com
# *************************************

import asyncio
from xoa_driver import  ports
from xoa_driver.misc import Hex
from .enums import *
import logging
from typing import List, Any

# *************************************************************************************
# func: hot_reconfiguration_supported
# description: Check if the transceiver supports hot reconfiguration
# *************************************************************************************
async def hot_reconfiguration_supported(port: ports.Z800FreyaPort, logger_name: str) -> bool:
    """Check if the transceiver supports hot reconfiguration
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Check if supports hot reconfiguration")
    resp = await port.transceiver.access_rw_seq(page_address=0x00, register_address=2, byte_count=1).get()
    int_value = int(resp.value, 16)
    stepped_config_only = (int_value >> 6) & 0x01
    if stepped_config_only == 0:
        return True
    else:
        auto_commisioning = int_value & 0x03
        if auto_commisioning == 2:
            return True
        else:
            return False
        
# *************************************************************************************
# func: read_config_status
# description: Read config status of a lane
# *************************************************************************************
async def read_config_status(port: ports.Z800FreyaPort, lane: int, logger_name: str) -> ConfigStatus:
    """Read the config status of each lane
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Read ConfigStatus - Lane {lane} ")
    assert 1<=lane<=8

    _page = 0x11
    _start_addr = 202
    _reg_addr = _start_addr + int((lane-1)/2)
    _size = 1
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    if lane % 2 == 0:
        _tmp = int(resp.value, 16) & 0xF0
        _read = _tmp >> 4
    else:
        _tmp = int(resp.value, 16) & 0x0F
        _read = _tmp
    logger.info(f"  Read operation done. Value: ConfigStatus={ConfigStatus(_read).name}")
    return ConfigStatus(_read)
        
# *************************************************************************************
# func: rx_output_eq_control_supported
# description: Check if the transceiver supports RX output eq control
# *************************************************************************************
async def rx_output_eq_control_supported(port: ports.Z800FreyaPort, logger_name: str) -> bool:
    """Check if the transceiver supports RX output eq control
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Check if supports RX output eq contorl")

    _page = 0x01
    _start_addr = 162
    _reg_addr = _start_addr
    _size = 1
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    int_value = int(resp.value, 16)
    support_flags = (int_value >> 2) & 0x07
    if support_flags != 0x07:
        return False
    else:
        return True

# *************************************************************************************
# func: apply_dp_deinit
# description: Deinitialize the Data Path associated with host lane
# (Write address 128 value with 0xFF)
# *************************************************************************************
async def apply_dp_deinit(port: ports.Z800FreyaPort, logger_name: str):
    """Deinitialize the Data Path associated with host lane (Write address 128 with 1)
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Deinitialize the Data Path associated with host lane (Write address 128 value with 0xFF)")

    _page = 0x01
    _start_addr = 128
    _reg_addr = _start_addr
    _size = 1
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex("FF"))
    await asyncio.sleep(1)

# *************************************************************************************
# func: trigger_provision
# description: Trigger Provision procedure using the Staged Control Set 0 settings 
# for host lane
# (Write address 143 value 0xFF)
# *************************************************************************************
async def trigger_provision(port: ports.Z800FreyaPort, logger_name: str):
    """Trigger Provision procedure using the Staged Control Set 0 settings for host lane (Write address 143 value 0xFF)
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Trigger Provision")

    _page = 0x01
    _start_addr = 143
    _reg_addr = _start_addr
    _size = 1
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex("FF"))
    await asyncio.sleep(1)

# *************************************************************************************
# func: trigger_provision_commission
# description: Trigger Provision-and-Commission procedure using the 
# Staged Control Set 0 settings for host lane
# (Write address 143 value 0xFF)
# *************************************************************************************
async def trigger_provision_commission(port: ports.Z800FreyaPort, logger_name: str):
    """Trigger Provision-and-Commission procedure using the Staged Control Set 0 
    settings for host lane (Write address 143 value 0xFF)
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Trigger Provision-and-Commission")

    _page = 0x01
    _start_addr = 143
    _reg_addr = _start_addr
    _size = 1
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex("FF"))
    await asyncio.sleep(1)

# *************************************************************************************
# func: apply_dp_init
# description: Initialize the Data Path associated with host lane 
# (Write address 128 with value 0x00)
# *************************************************************************************
async def apply_dp_init(port: ports.Z800FreyaPort, logger_name: str):
    """Initialize the Data Path associated with host lan (Write address 128 with value 0x00)
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Initialize the Data Path associated with host lan (Write address 128 with value 0x00)")

    _page = 0x01
    _start_addr = 128
    _reg_addr = _start_addr
    _size = 1
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex("00"))
    await asyncio.sleep(1)

# *************************************************************************************
# func: output_eq_write
# description: Write input dB value to a specified cursor on a specified lane
# *************************************************************************************
async def output_eq_write(port: ports.Z800FreyaPort, lane: int, db: int, cursor: Cursor, logger_name: str):
    """Write input dB value to a specified cursor on a specified lane
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Write {db} dB to {cursor.name} - Lane {lane} ")
    assert 1<=lane<=8
    assert 0<=db<=7

    _page = 0x10
    _start_addr = 162
    _reg_addr = _start_addr + int(cursor.value*4) + int((lane-1)/2)
    _size = 1
    
    # read the byte from the address
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    current_byte = int(resp.value, 16) # convert the existing byte value from hex string to int
    if lane % 2 == 0:
        _tmp = int(resp.value, 16) & 0xF0
        _read = _tmp >> 4
    else:
        _tmp = int(resp.value, 16) & 0x0F
        _read = _tmp
    logger.info(f"  Current value: {_read} dB")
    
    # write the new byte into the address
    if lane % 2 == 0:
        _tmp = (current_byte & 0x0F) + (db << 4)
    else:
        _tmp = (current_byte & 0xF0) + db
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex('{:02X}'.format(_tmp)))
    await asyncio.sleep(1)
    
# *************************************************************************************
# func: output_eq_read
# description: Read dB value from a specified cursor on a specified lane
# *************************************************************************************
async def output_eq_read(port: ports.Z800FreyaPort, lane: int, cursor: Cursor, logger_name: str) -> int:
    """Read dB value from a specified cursor on a specified lane
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Read dB from {cursor.name} - Lane {lane} ")
    assert 1<=lane<=8

    _page = 0x10
    _start_addr = 162
    _reg_addr = _start_addr + int(cursor.value*4) + int((lane-1)/2)
    _size = 1

    # read the byte from the address
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    current_byte = int(resp.value, 16) # convert the existing byte value from hex string to int
    if lane % 2 == 0:
        _tmp = int(resp.value, 16) & 0xF0
        _read = _tmp >> 4
    else:
        _tmp = int(resp.value, 16) & 0x0F
        _read = _tmp
    logger.info(f"  Current value: {_read} dB")
    return _read


# *************************************************************************************
# func: dp_read
# description: Read AppSelCode, DataPathID, and ExplicitControl to a specified lane
# *************************************************************************************
async def dp_read(port: ports.Z800FreyaPort, lane: int, logger_name: str):
    """Read AppSelCode, DataPathID, and ExplicitControl to a specified lane
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Read Data Path config - Lane {lane} ")
    assert 1<=lane<=8

    _page = 0x10
    _start_addr = 145
    _reg_addr = _start_addr + (lane-1)
    _size = 1
    
    # read the byte from the address again to verify the write
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    await asyncio.sleep(1)
    appsel_code = int(resp.value, 16) >> 4
    dp_id = (int(resp.value, 16) >> 1) & 0x07
    explicit_ctrl = int(resp.value, 16) & 0x01
    logger.info(f"  Read operation done. Value: AppSelCode={appsel_code}, DataPathID={dp_id}, ExplicitControl={explicit_ctrl}")
    return appsel_code, dp_id, explicit_ctrl


# *************************************************************************************
# func: dp_write
# description: Write AppSelCode, DataPathID, and ExplicitControl to a specified lane
# *************************************************************************************
async def dp_write(port: ports.Z800FreyaPort, lane: int, appsel_code: int, dp_id: int, explicit_ctrl: int, logger_name: str):
    """Write AppSelCode, DataPathID, and ExplicitControl to a specified lane
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Write AppSelCode={appsel_code}, DataPathID={dp_id}, ExplicitControl={explicit_ctrl} - Lane {lane} ")
    assert 1<=lane<=8
    assert 0<=appsel_code<=15
    assert 0<=dp_id<=7
    assert 0<=explicit_ctrl<=1

    _page = 0x10
    _start_addr = 145
    _reg_addr = _start_addr + (lane-1)
    _size = 1

    _tmp = (appsel_code<<4) + (dp_id<<1) + explicit_ctrl
    
    # write the new byte into the address
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=Hex('{:02X}'.format(_tmp)))
    await asyncio.sleep(1)

# *************************************************************************************
# func: output_eq_write_all
# description: Write output eq dB value to a specified cursor on all lanes
# *************************************************************************************
async def output_eq_write_all(port: ports.Z800FreyaPort, db: int, cursor: Cursor, logger_name: str):
    """Write output eq value to a specified cursor on all lanes
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Write {db} dB to {cursor.name}")
    assert 0<=db<=7

    _page = 0x10
    _start_addr = 162
    _reg_addr = _start_addr + int(cursor.value*4)
    _size = 4
    
    _value = (db << 4) | db
    _hex_value = Hex('{:02X}'.format(_value)*4)
    await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).set(value=_hex_value)
    await asyncio.sleep(1)

# *************************************************************************************
# func: read_config_status_all
# description: Read config status of all lanes
# *************************************************************************************
async def read_config_status_all(port: ports.Z800FreyaPort, logger_name: str) -> List[ConfigStatus]:
    """Read the config status of all lanes
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Read ConfigStatus")

    _page = 0x11
    _start_addr = 202
    _reg_addr = _start_addr
    _size = 4
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    all_status_hexstring = resp.value
    
    n = 1
    config_status_str_list = [all_status_hexstring[i:i+n] for i in range(0, len(all_status_hexstring), n)]
    config_status_list = [ConfigStatus(int(x, 16)) for x in config_status_str_list]

    logger.info(f"  Read operation done. Value: ConfigStatusList={config_status_str_list}")
    return config_status_list


# *************************************************************************************
# func: output_eq_read_all
# description: Read dB value from a specified cursor from all lanes
# *************************************************************************************
async def output_eq_read_all(port: ports.Z800FreyaPort, cursor: Cursor, logger_name: str) -> List[int]:
    """Read dB value from a specified cursor from all lanes
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"Port {port.kind.module_id}/{port.kind.port_id}: Read dB from {cursor.name}")

    _page = 0x10
    _start_addr = 162
    _reg_addr = _start_addr + int(cursor.value*4)
    _size = 4

    # read the byte from the address
    resp = await port.transceiver.access_rw_seq(page_address=_page, register_address=_reg_addr, byte_count=_size).get()
    all_eq_hexstring = resp.value

    n = 1
    eq_str_list = [all_eq_hexstring[i:i+n] for i in range(0, len(all_eq_hexstring), n)]
    final_eq_list = []
    final_eq_list.append(int(eq_str_list[1], 16))
    final_eq_list.append(int(eq_str_list[0], 16))
    final_eq_list.append(int(eq_str_list[3], 16))
    final_eq_list.append(int(eq_str_list[2], 16))
    final_eq_list.append(int(eq_str_list[5], 16))
    final_eq_list.append(int(eq_str_list[4], 16))
    final_eq_list.append(int(eq_str_list[7], 16))
    final_eq_list.append(int(eq_str_list[6], 16))
    return final_eq_list
