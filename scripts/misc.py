# ***********************************************************************************************
# this library file contains functions for cable quality test
# ***********************************************************************************************

import asyncio

from xoa_driver import testers
from xoa_driver import modules
from xoa_driver import ports
from xoa_driver import enums
from xoa_driver.hlfuncs import mgmt
import logging
from typing_extensions import List, Any
import time, os

def get_port_list(tester_obj: testers.L23Tester, port_pair_list: List[dict], key_str: str) -> List[Any]:
    _port_obj_list = []
    for port_pair in port_pair_list:
        _port_str = port_pair[key_str]

        # Access module on the tester
        _mid = int(_port_str.split("/")[0])
        _pid = int(_port_str.split("/")[1])
        module_obj = tester_obj.modules.obtain(_mid)

        if not isinstance(module_obj, modules.Z800FreyaModule):
            logging.info(f"This script is only for Freya module")
            return []

        # Get the port on module as TX port
        port_obj = module_obj.ports.obtain(_pid)

        # Inset the port object to the list
        _port_obj_list.append(port_obj)
    return _port_obj_list

# def get_value_list(tester: testers.L23Tester, port_pair_list: List[dict], key_str: str) -> List[Any]:
#     _value_list = []
#     for port_pair in port_pair_list:
#         _value = port_pair[key_str]
#         _value_list.append(_value)
#     return _value_list

async def reserve_reset_ports_in_list(tester_obj: testers.L23Tester, port_obj_list: List[ports.Z800FreyaPort]) -> None:
    for _port in port_obj_list:
        _module_id = _port.kind.module_id
        _module = tester_obj.modules.obtain(_module_id)
        await mgmt.free_module(module=_module, should_free_ports=False)
        await mgmt.reserve_port(_port)
        await mgmt.reset_port(_port)
    await asyncio.sleep(1.0)

async def release_ports_in_list(port_obj_list: List[ports.Z800FreyaPort]) -> None:
    for _port in port_obj_list:
        await mgmt.free_port(_port)
    await asyncio.sleep(1.0)

def calc_fec_ber(original_data: int) -> str:
    if original_data == 0:
        return "0.0"
    elif original_data == -1:
        return "-1.0"
    else:
        return '{:.2e}'.format(abs(1/original_data))
    
def convert_prbs_lock_status(original_data: enums.PRBSLockStatus) -> str:
    if original_data == enums.PRBSLockStatus.PRBSOFF:
        return "No Lock"
    elif original_data == enums.PRBSLockStatus.PRBSON:
        return "Lock"
    else:
        return "Unstable"

def hex_to_ascii(hex_str) -> str:
    ascii_str = ""
    for i in range(0, len(hex_str), 2):
        byte = int(hex_str[i:i+2], 16)
        if byte < 127:
            ascii_str += chr(byte)
        else:
            ascii_str += "?"
    return ascii_str

def beautify_hex(hex_str) -> str:
    b_hex_str = ""
    for i in range(0, len(hex_str), 2):
        b_hex_str = b_hex_str + hex_str[i:i+2] + " "
    return b_hex_str

def hex_to_filtered_ascii(hex_str) -> str:
    allowed_ascii_codes = [i for i in range(48,58)]
    allowed_ascii_codes.extend([i for i in range(65,91)])
    allowed_ascii_codes.extend([i for i in range(97,123)])
    ascii_str = ""
    for i in range(0, len(hex_str), 2):
        byte = int(hex_str[i:i+2], 16)
        if byte in allowed_ascii_codes:
            ascii_str += chr(byte)
        else:
            ascii_str += ""
    return ascii_str

async def get_tcvr_vendor_name(port_obj: ports.Z800FreyaPort) -> dict:
    description = "Vendor Name"
    page_address = 0x00
    byte_address = 129
    length = 16
    resp = await port_obj.transceiver.access_rw_seq(
        page_address=page_address,
        register_address=byte_address,
        byte_count=length).get()
    _raw_value = resp.value
    _acsii_value = hex_to_ascii(_raw_value)
    _hex_value = beautify_hex(_raw_value)
    _filtered_acsii_value = hex_to_filtered_ascii(_raw_value)
    result = {
        "description": description,
        "hex_value": _hex_value,
        "acsii_value": _acsii_value,
        "filtered_acsii_value": _filtered_acsii_value
    }
    return result

async def get_tcvr_vendor_pn(port_obj: ports.Z800FreyaPort) -> dict:
    description = "Vendor P/N"
    page_address = 0x00
    byte_address = 148
    length = 16
    resp = await port_obj.transceiver.access_rw_seq(
        page_address=page_address,
        register_address=byte_address,
        byte_count=length).get()
    _raw_value = resp.value
    _acsii_value = hex_to_ascii(_raw_value)
    _hex_value = beautify_hex(_raw_value)
    _filtered_acsii_value = hex_to_filtered_ascii(_raw_value)
    result = {
        "description": description,
        "hex_value": _hex_value,
        "acsii_value": _acsii_value,
        "filtered_acsii_value": _filtered_acsii_value
    }
    return result

async def get_tcvr_vendor_sn(port_obj: ports.Z800FreyaPort) -> dict:
    description = "Vendor S/N"
    page_address = 0x00
    byte_address = 166
    length = 16
    resp = await port_obj.transceiver.access_rw_seq(
        page_address=page_address,
        register_address=byte_address,
        byte_count=length).get()
    _raw_value = resp.value
    _acsii_value = hex_to_ascii(_raw_value)
    _hex_value = beautify_hex(_raw_value)
    _filtered_acsii_value = hex_to_filtered_ascii(_raw_value)
    result = {
        "description": description,
        "hex_value": _hex_value,
        "acsii_value": _acsii_value,
        "filtered_acsii_value": _filtered_acsii_value
    }
    return result

async def get_tcvr_cable_length(port_obj: ports.Z800FreyaPort) -> dict:
    description = "Cable Length"
    page_address = 0x00
    byte_address = 202
    length = 1
    length_multiplier_decoder = {
        "0" : 0.1,
        "1" : 1,
        "2" : 10,
        "3" : 100
    }
    resp = await port_obj.transceiver.access_rw_seq(
        page_address=page_address,
        register_address=byte_address,
        byte_count=length).get()
    _raw_value = resp.value
    _hex_value = beautify_hex(_raw_value)
    _length_multiplier = length_multiplier_decoder[str(int(_raw_value, 16) >> 6)]
    _base_length = int(_raw_value, 16) & 0x3F
    _acsii_value = f"{_base_length * _length_multiplier} m"
    result = {
        "description": description,
        "hex_value": _hex_value,
        "acsii_value": _acsii_value
    }
    return result

async def create_report_dir(tester_obj: testers.L23Tester, port_pair_list: List[dict]) -> str:
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    port_obj = tx_port_list[0]
    # read vendor name and pn but only keep the good characters
    tmp = await get_tcvr_vendor_name(port_obj)
    filtered_vendor_name = tmp["filtered_acsii_value"]
    tmp = await get_tcvr_vendor_pn(port_obj)
    filtered_vendor_pn = tmp["filtered_acsii_value"]
    datetime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    path = filtered_vendor_name + "_" + filtered_vendor_pn + "_" + datetime
    if not os.path.exists(path):
        os.makedirs(path)
    return path

