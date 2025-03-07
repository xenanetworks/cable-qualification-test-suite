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
from typing import List, Any
import time, os
from .reportgen import HostTxTapReportGenerator, ModuleTxTapReportGenerator
from .enums import Cursor
from .cmisfuncs import *

# *************************************************************************************
# func: get_port_list
# description: Get port object list from port pair list
# *************************************************************************************
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

# *************************************************************************************
# func: reserve_reset_ports_in_list
# description: Reserve and reset ports in the list
# *************************************************************************************
async def reserve_reset_ports_in_list(tester_obj: testers.L23Tester, port_obj_list: List[ports.Z800FreyaPort]) -> None:
    for _port in port_obj_list:
        _module_id = _port.kind.module_id
        _module = tester_obj.modules.obtain(_module_id)
        await mgmt.free_module(module=_module, should_free_ports=False)
        await mgmt.reserve_port(_port)
        await mgmt.reset_port(_port)
    await asyncio.sleep(1.0)

# *************************************************************************************
# func: release_ports_in_list
# description: Release ports in the list
# *************************************************************************************
async def release_ports_in_list(port_obj_list: List[ports.Z800FreyaPort]) -> None:
    for _port in port_obj_list:
        await mgmt.free_port(_port)
    await asyncio.sleep(1.0)

# *************************************************************************************
# func: calc_fec_ber
# description: Calculate FEC BER
# *************************************************************************************
def calc_fec_ber(original_data: int) -> str:
    if original_data == 0:
        return "0.0"
    elif original_data == -1:
        return "-1.0"
    else:
        return '{:.2e}'.format(abs(1/original_data))

# *************************************************************************************
# func: convert_prbs_lock_status
# description: Convert PRBS lock status to string
# *************************************************************************************
def convert_prbs_lock_status(original_data: enums.PRBSLockStatus) -> str:
    if original_data == enums.PRBSLockStatus.PRBSOFF:
        return "No Lock"
    elif original_data == enums.PRBSLockStatus.PRBSON:
        return "Lock"
    else:
        return "Unstable"

# *************************************************************************************
# func: hex_to_ascii
# description: Convert hex string to ascii string
# *************************************************************************************
def hex_to_ascii(hex_str) -> str:
    ascii_str = ""
    for i in range(0, len(hex_str), 2):
        byte = int(hex_str[i:i+2], 16)
        if byte < 127:
            ascii_str += chr(byte)
        else:
            ascii_str += "?"
    return ascii_str

# *************************************************************************************
# func: beautify_hex
# description: Beautify hex string
# *************************************************************************************
def beautify_hex(hex_str) -> str:
    b_hex_str = ""
    for i in range(0, len(hex_str), 2):
        b_hex_str = b_hex_str + hex_str[i:i+2] + " "
    return b_hex_str

# *************************************************************************************
# func: hex_to_filtered_ascii
# description: Hex to filtered ascii
# *************************************************************************************
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

# *************************************************************************************
# func: get_tcvr_vendor_name
# description: Get transceiver vendor name
# *************************************************************************************
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

# *************************************************************************************
# func: get_tcvr_vendor_pn
# description: Get transceiver vendor part number
# *************************************************************************************
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

# *************************************************************************************
# func: get_tcvr_vendor_sn
# description: Get transceiver vendor serial number
# *************************************************************************************
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

# *************************************************************************************
# func: get_tcvr_cable_length
# description: Get transceiver cable length
# *************************************************************************************
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

# *************************************************************************************
# func: create_report_dir
# description: Create report directory
# *************************************************************************************
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

# *************************************************************************************
# func: change_module_media
# description: Change module media and port speed
# *************************************************************************************
async def change_module_media(tester_obj: testers.L23Tester, module_list: List[int], media: enums.MediaConfigurationType, port_speed: str, logger_name: str) -> None:

    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"=============== Change Module Media and Port Speed ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    logger.info(f"{'Media:':<20}{media.name}")
    logger.info(f"{'Port Speed:':<20}{port_speed}")

    _port_count = int(port_speed.split("x")[0])
    _port_speed = int(port_speed.split("x")[1].replace("G", ""))
    _port_speed_config = [_port_speed*1000] * _port_count
    _port_speed_config.insert(0, _port_count)
    for _module_id in module_list:
        _module = tester_obj.modules.obtain(_module_id)
        await mgmt.free_module(module=_module, should_free_ports=True)
        await mgmt.reserve_module(module=_module)
        await _module.media.set(media_config=media)
        await _module.cfp.config.set(portspeed_list=_port_speed_config)

    logger.info(f"=============== Done ====================")

# *************************************************************************************
# func: read_host_tx_eq
# description: Read host-side TX equalization settings
# *************************************************************************************
async def read_host_tx_eq(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str) -> None:

    # Init report generator
    report_gen = HostTxTapReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"=============== Host-Side TX EQ Info ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")

    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    for tx_port_obj in tx_port_list:
        resp = await tx_port_obj.capabilities.get()
        serdes_cnt = resp.serdes_count
        for i in range(serdes_cnt):
            # get LEVEL
            resp = await tx_port_obj.l1.serdes[i].medium.tx.level.get()
            pre3_db = resp.pre3/10
            pre2_db = resp.pre2/10
            pre_db = resp.pre/10
            main_mv = resp.main
            post_db = resp.post/10
            logger.info(f"Lane {i}:  pre3 = {pre3_db}dB, pre2 = {pre2_db}dB, pre = {pre_db}dB, main = {main_mv}mV, post = {post_db}dB")
            report_gen.record_data(port_name=f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}", lane=i, pre3_db=pre3_db, pre2_db=pre2_db, pre_db=pre_db, main_mv=main_mv, post_db=post_db)

    report_gen.generate_report(report_filename)

# *************************************************************************************
# func: load_host_tx_eq
# description: Load host-side TX equalization settings
# *************************************************************************************
async def load_host_tx_eq(tester_obj: testers.L23Tester, port_pair_list: List[dict], logger_name: str, host_tx_eq: dict) -> None:
    
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"=============== Load Host TX EQ ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    logger.info(f"{'Enabled:':<20}{host_tx_eq['enable']}")

    if host_tx_eq['enable']:
        tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
        rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
        await reserve_reset_ports_in_list(tester_obj, tx_port_list)
        await reserve_reset_ports_in_list(tester_obj, rx_port_list)
        pre3 = host_tx_eq["pre3"]
        pre2 = host_tx_eq["pre2"]
        pre = host_tx_eq["pre"]
        main = host_tx_eq["main"]
        post = host_tx_eq["post"]
        for tx_port_obj, rx_port_obj in zip(tx_port_list, rx_port_list):
            resp = await tx_port_obj.capabilities.get()
            serdes_cnt = resp.serdes_count
            for i in range(serdes_cnt):
                await tx_port_obj.l1.serdes[i].medium.tx.native.set(pre3, pre2, pre, main, post)
                await rx_port_obj.l1.serdes[i].medium.tx.native.set(pre3, pre2, pre, main, post)
        await asyncio.sleep(1.0)

# *************************************************************************************
# func: load_module_tx_eq
# description: Load host-side TX equalization settings
# *************************************************************************************
async def load_module_tx_eq(tester_obj: testers.L23Tester, port_pair_list: List[dict], logger_name: str, module_tx_eq: dict):
    
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"=============== Load Module TX EQ ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    logger.info(f"{'Enabled:':<20}{module_tx_eq['enable']}")

    if module_tx_eq['enable']:
        tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
        rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
        await reserve_reset_ports_in_list(tester_obj, tx_port_list)
        await reserve_reset_ports_in_list(tester_obj, rx_port_list)
        pre = module_tx_eq["pre"]
        main = module_tx_eq["main"]
        post = module_tx_eq["post"]
        for tx_port_obj, rx_port_obj in zip(tx_port_list, rx_port_list):
            hotreconfig_supported = await hot_reconfiguration_supported(tx_port_obj, logger_name)
            if not hotreconfig_supported:
                logger.warning(f"Hot Reconfiguration is not supported on Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}")
                return
            hotreconfig_supported = await hot_reconfiguration_supported(rx_port_obj, logger_name)
            if not hotreconfig_supported:
                logger.warning(f"Hot Reconfiguration is not supported on Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}")
                return

            await output_eq_write_all(tx_port_obj, pre, Cursor.Precursor, logger_name)
            await output_eq_write_all(tx_port_obj, main, Cursor.Amplitude, logger_name)
            await output_eq_write_all(tx_port_obj, post, Cursor.Postcursor, logger_name)

            await output_eq_write_all(rx_port_obj, pre, Cursor.Precursor, logger_name)
            await output_eq_write_all(rx_port_obj, main, Cursor.Amplitude, logger_name)
            await output_eq_write_all(rx_port_obj, post, Cursor.Postcursor, logger_name)

            # Trigger the Provision-and-Commission procedure
            await trigger_provision_commission(port=tx_port_obj, logger_name=logger_name)
            await trigger_provision_commission(port=rx_port_obj, logger_name=logger_name)

            # Read ConfigStatus register to check if the EQ settings are applied.
            while True:
                config_status_list = await read_config_status_all(port=tx_port_obj, logger_name=logger_name)
                if ConfigStatus.ConfigInProgress in config_status_list:
                    logger.info(f"  ConfigStatus is still ConfigInProgress. Please wait for the configuration to complete.")
                    await asyncio.sleep(1)
                    continue
                elif len(set(config_status_list)) == 1 and ConfigStatus.ConfigSuccess in config_status_list:
                    logger.info(f"  Write operation successful")
                    return
                else:
                    logger.info(f"  Write operation failed. ({config_status_list})")
                    return


# *************************************************************************************
# func: read_module_tx_eq
# description: Read module-side TX equalization settings
# *************************************************************************************
async def read_module_tx_eq(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str) -> None:

    # Init report generator
    report_gen = ModuleTxTapReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)
    logger.info(f"=============== Module-Side TX EQ Info ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")

    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    for rx_port_obj in rx_port_list:
        pre_db_list = await output_eq_read_all(rx_port_obj, Cursor.Precursor, logger_name)
        main_db_list = await output_eq_read_all(rx_port_obj, Cursor.Amplitude, logger_name)
        post_db_list = await output_eq_read_all(rx_port_obj, Cursor.Postcursor, logger_name)
        for i, (pre_db, main_db, post_db) in enumerate(zip(pre_db_list, main_db_list, post_db_list)):
            logger.info(f"Lane {i}: pre = {pre_db}dB, main = {main_db}mV, post = {post_db}dB")
            report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", lane=i, pre_db=pre_db, main_db=main_db, post_db=post_db)

    report_gen.generate_report(report_filename)