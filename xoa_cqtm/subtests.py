# *************************************
# author: leonard.yu@teledyne.com
# *************************************

import asyncio
from xoa_driver import testers
from xoa_driver import modules
from xoa_driver import ports
from xoa_driver import enums
from xoa_driver import utils
from xoa_driver.hlfuncs import mgmt, headers
from xoa_driver.misc import Hex
from .utils import *
from .reportgen import *
import logging
from typing import List, Any
from decimal import Decimal, getcontext
import matplotlib.pyplot as plt
from collections import deque

# *************************************************************************************
# func: prbs_test
# *************************************************************************************
async def prbs_test(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str, test_config: dict) -> None:
    """PRBS Test
    """
    # Init report generator
    report_gen = PRBSReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)

    # Read test configuration
    duration: int = test_config["duration"]
    polynomial: enums.PRBSPolynomial = enums.PRBSPolynomial[test_config["polynomial"]]

    # Establish connection to a Xena tester using Python context manager
    # The connection will be automatically terminated when it is out of the block
    logger.info(f"=============== PRBS BER Test - Start ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    
    # Reserve and reset ports
    logger.info(f"Reserve and reset ports")
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    await reserve_reset_ports_in_list(tester_obj, tx_port_list)
    await reserve_reset_ports_in_list(tester_obj, rx_port_list)
    
    # Configure the PRBS polynomial on the TX ports, and statistics mode on the Rx ports, using command grouping.
    logger.info(f"Set PRBS polynomial on TX ports and statistics mode on RX ports")
    prbs_config_tokens = []
    for tx_port_obj, rx_port_obj in zip(tx_port_list, rx_port_list):
        prbs_config_tokens.append(tx_port_obj.l1.prbs_config.set(
            prbs_inserted_type=enums.PRBSInsertedType.PHY_LINE,
            polynomial=polynomial,
            invert=enums.PRBSInvertState.INVERTED,
            statistics_mode=enums.PRBSStatisticsMode.ACCUMULATIVE))
        prbs_config_tokens.append(rx_port_obj.l1.prbs_config.set(
            prbs_inserted_type=enums.PRBSInsertedType.PHY_LINE,
            polynomial=polynomial,
            invert=enums.PRBSInvertState.INVERTED,
            statistics_mode=enums.PRBSStatisticsMode.ACCUMULATIVE))
    await asyncio.gather(*prbs_config_tokens)

    # Enable PRBS on all serdes of all Tx ports. SerDes count of each port is detected automatically.
    logger.info(f"Enable PRBS on all serdes of all TX ports")
    tx_prbs_tokens = []
    serdes_count_list = []
    for tx_port_obj in tx_port_list:
        _p_capability = await tx_port_obj.capabilities.get()
        serdes_count = _p_capability.serdes_count
        serdes_count_list.append(serdes_count)
        logger.info(f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id} Serdes count: {serdes_count}")
        for i in range(serdes_count):
            tx_prbs_tokens.append(tx_port_obj.l1.serdes[i].prbs.control.set(prbs_seed=0, prbs_on_off=enums.PRBSOnOff.PRBSON, error_on_off=enums.ErrorOnOff.ERRORSOFF))
    await asyncio.gather(*tx_prbs_tokens)
    await asyncio.sleep(1.0)

    # Prepare the PRBS statistics tokens for later use
    prbs_stats_token_list = []
    for rx_port_obj, serdes_count in zip(rx_port_list, serdes_count_list):
        _prbs_serdes_stats_tokens = [] # commands bound for the same port
        for i in range(serdes_count):
            _prbs_serdes_stats_tokens.append(rx_port_obj.serdes[i].prbs.status.get())
        prbs_stats_token_list.append(_prbs_serdes_stats_tokens)

    # clear counters on the Rx port
    logger.info(f"Clear counters on the RX ports")
    clear_counter_tokens = []
    for rx_port_obj in rx_port_list:
        clear_counter_tokens.append(rx_port_obj.pcs_pma.rx.clear.set())
    await asyncio.gather(*clear_counter_tokens)

    # Start collecting PRBS statistics on RX ports
    logger.info(f"Start collecting PRBS statistics on RX ports")
    for i in range(duration):
        logger.info(f"  Progress: {i+1}/{duration}")
        
        for serdes_tokens in prbs_stats_token_list:
            _index = prbs_stats_token_list.index(serdes_tokens)
            _resps = await utils.apply(*serdes_tokens)
            rx_port_obj = rx_port_list[_index]
            serdes_count = serdes_count_list[_index]
            for i in range(serdes_count):
                _prbs_lock = convert_prbs_lock_status(_resps[i].lock)
                if _resps[i].error_count > 0:
                    logger.info(f"  Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}, SerDes {i}: PRBS Lock={_prbs_lock}, PRBS Bits={_resps[i].byte_count*8}, PRBS Errors={_resps[i].error_count}, Error Rate={_resps[i].error_count/_resps[0].byte_count/8}")
                else:
                    logger.info(f"  Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}, SerDes {i}: PRBS Lock={_prbs_lock}, PRBS Bits={_resps[i].byte_count*8}, PRBS Errors={_resps[i].error_count}, Error Rate<{4.6/_resps[0].byte_count/8}")
                report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id} - SerDes {i}", prbs_lock=_prbs_lock, prbs_bits=_resps[i].byte_count*8, prbs_errors=_resps[i].error_count)

        await asyncio.sleep(1.0)

    # Generate report
    logger.info(f"Generate PRBS report")
    report_gen.generate_report(report_filename)

    # Stop PRBS on TX ports
    logger.info(f"Stop PRBS on TX ports")
    prbs_stop_tokens = []
    for tx_port_obj, serdes_count in zip(tx_port_list, serdes_count_list):
        for i in range(serdes_count):
            prbs_stop_tokens.append(tx_port_obj.l1.serdes[i].prbs.control.set(prbs_seed=0, prbs_on_off=enums.PRBSOnOff.PRBSOFF, error_on_off=enums.ErrorOnOff.ERRORSOFF))
    await asyncio.gather(*prbs_stop_tokens)

    # Release the ports
    logger.info(f"Release the ports")
    await release_ports_in_list(tx_port_list)
    await release_ports_in_list(rx_port_list)

    # The End
    logger.info(f"=============== PRBS BER Test - End =====================")

# *************************************************************************************
# func: fec_test
# *************************************************************************************
async def fec_test(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str, test_config: dict) -> None:
    """FEC Test
    """
    
    # Init report generator
    report_gen = FECReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)

    # Read test configuration
    duration: int = test_config["duration"]

    # Establish connection to a Xena tester using Python context manager
    # The connection will be automatically terminated when it is out of the block
    logger.info(f"=============== FEC BER Test - Start ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    
    # Reserve and reset ports
    logger.info(f"Reserve and reset ports")
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    await reserve_reset_ports_in_list(tester_obj, tx_port_list)
    await reserve_reset_ports_in_list(tester_obj, rx_port_list)
    
    # Enable FEC on TX ports
    logger.info(f"Enable FEC on TX ports")
    fec_config_tokens = []
    for tx_port_obj in tx_port_list:
        fec_config_tokens.append(tx_port_obj.fec_mode.set(mode=enums.FECMode.ON))
    await asyncio.gather(*fec_config_tokens)

    # Prepare the FEC statistics tokens for later use
    fec_stats_tokens = []
    for rx_port_obj in rx_port_list:
        fec_stats_tokens.append(rx_port_obj.pcs_pma.rx.total_status.get())

    # clear counters on the Rx port
    logger.info(f"Clear counters on the RX ports")
    clear_counter_tokens = []
    for rx_port_obj in rx_port_list:
        clear_counter_tokens.append(rx_port_obj.pcs_pma.rx.clear.set())
    await asyncio.gather(*clear_counter_tokens)

    # Start collecting pre-FEC and post-FEC statistics on RX ports
    logger.info(f"Start collecting pre-FEC and post-FEC statistics on RX ports")
    for i in range(duration):
        logger.info(f"  Progress: {i+1}/{duration}")

        total_status_list = await asyncio.gather(*fec_stats_tokens)

        for total_status, rx_port_obj in zip(total_status_list, rx_port_list):
            pre_fec_ber = calc_fec_ber(total_status.total_pre_fec_ber)
            post_fec_ber = calc_fec_ber(total_status.total_post_fec_ber)
            logger.info(f"  Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}: Pre-FEC BER={pre_fec_ber}, Post-FEC BER={post_fec_ber}")

            report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", pre_fec_ber=pre_fec_ber, post_fec_ber=post_fec_ber)

        await asyncio.sleep(1.0)

    # Generate report
    logger.info(f"Generate FEC BER report")
    report_gen.generate_report(report_filename)

    # Release the ports
    logger.info(f"Release the ports")
    await release_ports_in_list(tx_port_list)
    await release_ports_in_list(rx_port_list)

    # The End
    logger.info(f"=============== FEC BER Test - End =====================")

# *************************************************************************************
# func: tcvr_basic_info
# *************************************************************************************
async def tcvr_basic_info(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str) -> None:
    """Read transceiver basic info
    """

    # Init report generator
    report_gen = TransceiverReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)

    # Establish connection to a Xena tester using Python context manager
    # The connection will be automatically terminated when it is out of the block
    logger.info(f"=============== Read Transceiver Info - Start ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    
    # Reserve and reset ports
    logger.info(f"Reserve and reset ports")
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    await reserve_reset_ports_in_list(tester_obj, tx_port_list)
    await reserve_reset_ports_in_list(tester_obj, rx_port_list)

    # Read TX ports transceiver info
    logger.info(f"Read TX ports transceiver info")
    for tx_port_obj in tx_port_list:
        result = await get_tcvr_vendor_name(tx_port_obj)
        report_gen.record_data(port_name=f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_vendor_pn(tx_port_obj)
        report_gen.record_data(port_name=f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_vendor_sn(tx_port_obj)
        report_gen.record_data(port_name=f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_cable_length(tx_port_obj)
        report_gen.record_data(port_name=f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
    
    # Read RX ports transceiver info
    logger.info(f"Read RX ports transceiver info")
    for rx_port_obj in rx_port_list:
        result = await get_tcvr_vendor_name(rx_port_obj)
        report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_vendor_pn(rx_port_obj)
        report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_vendor_sn(rx_port_obj)
        report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])
        result = await get_tcvr_cable_length(rx_port_obj)
        report_gen.record_data(port_name=f"Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}", description=result["description"], ascii_value=result["acsii_value"], raw_value=result["hex_value"])

    # Generate report
    logger.info(f"Generate trasceiver basic info report")
    report_gen.generate_report(report_filename)

    # Release the ports
    logger.info(f"Release the ports")
    await release_ports_in_list(tx_port_list)
    await release_ports_in_list(rx_port_list)

    # The End
    logger.info(f"=============== Read Transceiver Info - End =====================")

# *************************************************************************************
# func: latency_frame_loss_test
# *************************************************************************************
async def latency_frame_loss_test(tester_obj: testers.L23Tester, port_pair_list: List[dict], report_filename: str, logger_name: str, test_config: dict) -> None:
    """Latency and Frame Loss Test
    """
    getcontext().prec = 6

    # Init report generator
    report_gen = LatencyFrameLossReportGenerator()
    report_gen.chassis = tester_obj.info.host

    # Get logger
    logger = logging.getLogger(logger_name)

    # Read test configuration
    start_rate: float = test_config["start_rate"]
    end_rate: float = test_config["end_rate"]
    step_rate: float = test_config["step_rate"]
    packet_sizes = test_config["packet_sizes"]
    duration: int = test_config["duration"]
    
    # Establish connection to a Xena tester using Python context manager
    # The connection will be automatically terminated when it is out of the block
    logger.info(f"=============== Latency & Frame Loss Test - Start ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    logger.info(f"Test configuration:")
    logger.info(f"  Start Rate: {start_rate*100}%")
    logger.info(f"  End Rate: {end_rate*100}%")
    logger.info(f"  Step Rate: {step_rate*100}%")
    logger.info(f"  Packet Sizes: {packet_sizes} bytes")
    logger.info(f"  Duration: {duration} seconds (each)")
    traffic_rates = [Decimal(start_rate) + Decimal(step_rate)*i for i in range(int((end_rate-start_rate)/step_rate)+1)]
    if end_rate not in traffic_rates:
        traffic_rates.append(Decimal(end_rate))
    logger.info(f"Total tests: {len(traffic_rates)*len(packet_sizes)}")

    # Reserve and reset ports
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    logger.info(f"Reserve and reset ports")
    await reserve_reset_ports_in_list(tester_obj, tx_port_list)
    await reserve_reset_ports_in_list(tester_obj, rx_port_list)
    await asyncio.sleep(1.0)
    
    i = 0
    for traffic_rate in traffic_rates:
        for packet_size in packet_sizes:
            logger.info(f"Test {i} (Rate={traffic_rate*100}%, Packet Size={packet_size} bytes)")

            # Configure streams
            logger.info(f"Configure streams")
            clear_tokens = []
            start_tokens = []
            stop_tokens = []
            tpld_id_list = [i for i in range(0, len(tx_port_list))]
            for tx_port_obj, rx_port_obj, tpld_id in zip(tx_port_list, rx_port_list, tpld_id_list):
                stream_obj = await tx_port_obj.streams.create()
                stream_index = stream_obj.idx
                _dmac_resp = await rx_port_obj.net_config.mac_address.get()
                _smac_resp = await tx_port_obj.net_config.mac_address.get()
                await utils.apply(
                    stream_obj.tpld_id.set(test_payload_identifier=tpld_id),
                    stream_obj.enable.set_on(),
                    stream_obj.comment.set(comment=f"Latency and Frame Loss Test Stream ({stream_index}/{tpld_id})"),
                    stream_obj.payload.content.set(payload_type=enums.PayloadType.INCREMENTING, hex_data=Hex("DEAD")),
                    stream_obj.rate.fraction.set(stream_rate_ppm=int(1_000_000*traffic_rate)),
                    stream_obj.packet.length.set(length_type=enums.LengthType.FIXED, min_val=packet_size, max_val=packet_size),
                    stream_obj.packet.header.protocol.set(segments=[
                        enums.ProtocolOption.ETHERNET]),
                    stream_obj.packet.header.data.set(hex_data=Hex(f"{_dmac_resp.mac_address}{_smac_resp.mac_address}FFFF")),
                )
                clear_tokens.append(tx_port_obj.statistics.tx.clear.set())
                clear_tokens.append(tx_port_obj.statistics.rx.clear.set())
                clear_tokens.append(rx_port_obj.statistics.tx.clear.set())
                clear_tokens.append(rx_port_obj.statistics.rx.clear.set())

                start_tokens.append(tx_port_obj.traffic.state.set_start())
                stop_tokens.append(tx_port_obj.traffic.state.set_stop())
            await asyncio.sleep(1.0)

            # Batch clear statistics on TX and RX ports
            logger.info(f"Clear statistics on TX and RX ports")
            await asyncio.gather(*clear_tokens)
            await asyncio.sleep(1.0)

            # Start traffic
            logger.info(f"Start traffic")
            await asyncio.gather(*start_tokens)

            #  Test duration in seconds
            logger.info(f"Test duration: {duration} seconds")
            await asyncio.sleep(duration)

            # Stop traffic
            logger.info(f"Stop traffic")
            await asyncio.gather(*stop_tokens)
            await asyncio.sleep(1.0)

            # # Query stream statistics
            for tx_port_obj, rx_port_obj , tpld_id in zip(tx_port_list, rx_port_list, tpld_id_list):
                tx_stream, rx_stream, rx_stream_latency, rx_stream_jitter = await asyncio.gather(
                    tx_port_obj.statistics.tx.obtain_from_stream(0).get(),
                    rx_port_obj.statistics.rx.access_tpld(tpld_id).traffic.get(),
                    rx_port_obj.statistics.rx.access_tpld(tpld_id).latency.get(),
                    rx_port_obj.statistics.rx.access_tpld(tpld_id).jitter.get(),
                )
                _description = f"Port {tx_port_obj.kind.module_id}/{tx_port_obj.kind.port_id} -> Port {rx_port_obj.kind.module_id}/{rx_port_obj.kind.port_id}"
                _frame_loss = tx_stream.packet_count_since_cleared - rx_stream.packet_count_since_cleared
                _latency = rx_stream_latency.avg_val
                _jitter = rx_stream_jitter.avg_val
                logging.info(f"{_description}")
                logging.info(f"  Rate: {traffic_rate*100} %")
                logging.info(f"  Packet Size: {packet_size} bytes")
                logging.info(f"  Frame Loss: {_frame_loss}")
                logging.info(f"  Latency   : {_latency} ns")
                logging.info(f"  Jitter    : {_jitter} ns")
                report_gen.record_data(port_name=_description, description=_description, traffic_rate=float(traffic_rate), packet_size=packet_size, frame_loss=_frame_loss, latency=_latency, jitter=_jitter)
            for tx_port_obj in tx_port_list:
                await tx_port_obj.streams.obtain(0).delete()
            i += 1    

    # Generate report
    logger.info(f"Generate latency and frame loss report")
    report_gen.generate_report(report_filename)

    # Release the ports
    logger.info(f"Release the ports")
    await release_ports_in_list(tx_port_list)
    await release_ports_in_list(rx_port_list)

    # The End
    logger.info(f"=============== Latency & Frame Loss Test - End =====================")

# *************************************************************************************
# func: signal_integrity_info
# *************************************************************************************
async def signal_integrity_info(tester_obj: testers.L23Tester, port_pair_list: List[dict], logger_name: str, should_histogram: bool, path: str) -> None:
    """Signal Integrity Info
    """

    # Get logger
    logger = logging.getLogger(logger_name)

    # Establish connection to a Xena tester using Python context manager
    # The connection will be automatically terminated when it is out of the block
    
    logger.info(f"=============== Signal Integrity - Start ====================")
    logger.info(f"{'Tester:':<20}{tester_obj.info.host}")
    logger.info(f"{'Username:':<20}{tester_obj.session.owner_name}")
    
    # Reserve and reset ports
    logger.info(f"Reserve and reset ports")
    tx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "tx")
    rx_port_list: List[ports.Z800FreyaPort] = get_port_list(tester_obj, port_pair_list, "rx")
    await reserve_reset_ports_in_list(tester_obj, tx_port_list)
    await reserve_reset_ports_in_list(tester_obj, rx_port_list)

    await asyncio.sleep(3.0)

    # Merge TX and RX port list
    total_port_list = list(set(tx_port_list + rx_port_list))

    for port_obj in total_port_list:
        # Read number of serdes lanes
        resp = await port_obj.capabilities.get()
        # Show all lanes
        lanes_to_show = resp.serdes_count
        lanes = [i for i in range(lanes_to_show)]

        # figure config
        plt.ion()
        fig = plt.figure(figsize=(10,20), dpi=80, constrained_layout=True)
        fig.suptitle(f"Port {port_obj.kind.module_id}/{port_obj.kind.port_id} Signal Integrity")

        # grid spec
        # if lanes_to_show == 1:
        gs = fig.add_gridspec(nrows=lanes_to_show, ncols=1)
        # if lanes_to_show > 1:
        #     gs = fig.add_gridspec(nrows=math.ceil(lanes_to_show/2), ncols=2)

        # add subplots
        siv_subplots = []
        for i in range(lanes_to_show):
            # siv_subplots.append(fig.add_subplot(gs[i%gs.nrows, int(i/gs.nrows)]))
            siv_subplots.append(fig.add_subplot(gs[i, 0]))
        
        # data dequeue for each serdes lane. queue depth = density*2000
        INT_CNT_PER_DATA = 2000
        density = 1
        data_queue = []
        for _ in range(lanes_to_show):
            data_queue.append(deque((), maxlen=density*INT_CNT_PER_DATA))

        # set x and y label for each subplot
        for i in range(lanes_to_show):
            siv_subplots[i].set(xlabel=f"Value", ylabel=f"Lane {lanes[i]}")
        
        # group control commands for each serdes lane together to later send it as a command group.
        control_cmd_group = []
        for i in range(lanes_to_show):
            control_cmd_group.append(port_obj.l1.serdes[lanes[i]].medium.siv.control.set(opcode=enums.Layer1Opcode.START_SCAN))
        
        # get commands for each serdes lane together to later send it as a command group.
        get_cmd_group = []
        for i in range(lanes_to_show):
            get_cmd_group.append(port_obj.l1.serdes[lanes[i]].medium.siv.data.get())

        resp_group = ()
        await utils.apply(*control_cmd_group)
        while True:
            # get responses from all lanes
            resp_group = await utils.apply(*get_cmd_group)
            result_flags = [x.result for x in resp_group]
            if 0 in result_flags:
                # if not all lanes are ready in data, query again.
                continue
            else:
                for i in range(lanes_to_show):
                    siv_raw_levels = resp_group[i].value[0:12]
                    siv_raw_values = resp_group[i].value[12:]

                    # convert from 12 raw bytes into 6 signed int
                    siv_int_levels = []
                    for x in zip(siv_raw_levels[0::2], siv_raw_levels[1::2]):
                        siv_int_levels.append(int.from_bytes(bytes(x), byteorder='big', signed=True))
                    # Please note: only the first slicer data is used here.

                    # convert from 4000 bytes into 2000 signed int
                    siv_int_values = []
                    for x in zip(siv_raw_values[0::2], siv_raw_values[1::2]):
                        siv_int_values.append(int.from_bytes(bytes(x), byteorder='big', signed=True))
                    # put value data in queue
                    data_queue[i].extend(tuple(siv_int_values))

                    # Plot dots
                    siv_subplots[i].cla()
                    siv_subplots[i].relim()
                    siv_subplots[i].autoscale_view()
                    siv_subplots[i].set(xlabel=f"Value", ylabel=f"Lane {lanes[i]}")

                    if should_histogram:
                        logger.info(f"Plotting histogram")
                        siv_subplots[i].hist(x=[*data_queue[i]], bins=128, range=(-64, 63), density=False, color="blue", orientation="horizontal")
                    else:
                        logger.info(f"Plotting sample points")
                        siv_subplots[i].plot([*data_queue[i]], 'bs')


                    # ax.plot(x3, y3, color='red', linestyle='solid', marker='D')

                    # levels contains 6 values, 4 average pam4 levels and 2 slicers, (<p1> <p2> <p3> <m1> <m2> <m3>)
                    # add base slicer (this is always at 0)
                    y = 0
                    siv_subplots[i].axhline(y, color='black', linestyle='-', linewidth=0.5)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'B={y}', fontsize="small")
                    # add upper slicer <p2>
                    y = siv_int_levels[1]
                    siv_subplots[i].axhline(y, color='green', linestyle='dashed', linewidth=0.5)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'S={y}', fontsize="small")
                    # add lower slicer <m2>
                    y = siv_int_levels[4]
                    siv_subplots[i].axhline(y, color='green', linestyle='dashed', linewidth=0.5)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'S={y}', fontsize="small")
                    # add average level 3 <p3>
                    y = siv_int_levels[2]
                    siv_subplots[i].axhline(y, color='black', linestyle='dashed', linewidth=0.1)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'L3={y}', fontsize="small")
                    # add average level 2 <p1>
                    y = siv_int_levels[0]
                    siv_subplots[i].axhline(y, color='black', linestyle='dashed', linewidth=0.1)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'L2={y}', fontsize="small")
                    # add average level 1 <m3>
                    y = siv_int_levels[5]
                    siv_subplots[i].axhline(y, color='black', linestyle='dashed', linewidth=0.1)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'L1={y}', fontsize="small")
                    # add average level 0 <m1>
                    y = siv_int_levels[3]
                    siv_subplots[i].axhline(y, color='black', linestyle='dashed', linewidth=0.1)
                    siv_subplots[i].text(siv_subplots[i].get_xlim()[1] + 0.1, y, f'L0={y}', fontsize="small")

                if should_histogram:
                    filename = f"siv_hist_p{port_obj.kind.module_id}{port_obj.kind.port_id}.png"
                    plt.savefig(os.path.join(path, filename))
                else:
                    filename = f"siv_sample_p{port_obj.kind.module_id}{port_obj.kind.port_id}.png"
                    plt.savefig(os.path.join(path, filename))
                plt.close(fig)

                break
        
        await asyncio.sleep(3.0)

    logger.info(f"=============== Signal Integrity - End ====================")

