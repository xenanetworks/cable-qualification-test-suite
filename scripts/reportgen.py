# ***********************************************************************************************
# this library file contains report gen for cable quality test
# ***********************************************************************************************

import time
import csv

class PRBSReportGenerator:
    def __init__(self):
        self.name = "PRBS Test"
        self.chassis = "10.10.10.10"
        self.fieldnames = ["Time", "PRBS Lock", "PRBS Bits", "PRBS Errors", "PRBS BER"]
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.database = {}

    def record_data(self, port_name: str, prbs_lock: str, prbs_bits: int, prbs_errors: int) -> None:
        time_str = time.strftime("%H:%M:%S", time.localtime())
        if port_name not in self.database:
            self.database[port_name] = []
        if prbs_errors == 0:
            self.database[port_name].append({
                "Time": time_str,
                "PRBS Lock": prbs_lock,
                "PRBS Bits": prbs_bits,
                "PRBS Errors": prbs_errors,
                "PRBS BER": '{:.2e}'.format(abs(4.6/prbs_bits))
            })
        else:
            self.database[port_name].append({
                "Time": time_str,
                "PRBS Lock": prbs_lock,
                "PRBS Bits": prbs_bits,
                "PRBS Errors": prbs_errors,
                "PRBS BER": '{:.2e}'.format(abs(prbs_errors/prbs_bits))
            })
    
    def generate_report(self, filename: str) -> None:
        headers = [
            ["*******************************************"],
            ["Test:", self.name],
            ["Chassis:", self.chassis],
            ["Datetime:", self.datetime],
            []
        ]
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in headers:
                writer.writerow(line)
            for key, value in self.database.items():
                writer.writerow([key])
                dict_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                dict_writer.writeheader()
                for data in value:
                    dict_writer.writerow(data)
                writer.writerow([])

class FECReportGenerator:
    def __init__(self):
        self.name = "FEC BER Test"
        self.chassis = "10.10.10.10"
        self.fieldnames = ["Time", "Pre-FEC BER", "Post-FEC BER"]
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.database = {}

    def record_data(self, port_name: str, pre_fec_ber: str, post_fec_ber: str) -> None:
        time_str = time.strftime("%H:%M:%S", time.localtime())
        if port_name not in self.database:
            self.database[port_name] = []
        self.database[port_name].append({
            "Time": time_str,
            "Pre-FEC BER": pre_fec_ber,
            "Post-FEC BER": post_fec_ber,
        })
        
    
    def generate_report(self, filename: str) -> None:
        headers = [
            ["*******************************************"],
            ["Test:", self.name],
            ["Chassis:", self.chassis],
            ["Datetime:", self.datetime],
            []
        ]
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in headers:
                writer.writerow(line)
            for key, value in self.database.items():
                writer.writerow([key])
                dict_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                dict_writer.writeheader()
                for data in value:
                    dict_writer.writerow(data)
                writer.writerow([])

class TransceiverReportGenerator:
    def __init__(self):
        self.name = "Transceiver Info"
        self.chassis = "10.10.10.10"
        self.fieldnames = ["Description", "ASCII Value", "Raw Value"]
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.database = {}

    def record_data(self, port_name: str, description: str, ascii_value: str, raw_value: str) -> None:
        if port_name not in self.database:
            self.database[port_name] = []
        self.database[port_name].append({
            "Description": description,
            "ASCII Value": ascii_value,
            "Raw Value": raw_value,
        })
        
    def generate_report(self, filename: str) -> None:
        headers = [
            ["*******************************************"],
            ["Test:", self.name],
            ["Chassis:", self.chassis],
            ["Datetime:", self.datetime],
            []
        ]
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in headers:
                writer.writerow(line)
            for key, value in self.database.items():
                writer.writerow([key])
                dict_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                dict_writer.writeheader()
                for data in value:
                    dict_writer.writerow(data)
                writer.writerow([])

class LatencyFrameLossReportGenerator:
    def __init__(self):
        self.name = "Latency and Frame Loss Test"
        self.chassis = "10.10.10.10"
        self.fieldnames = ["Description", "Rate (%)", "Packet Size (bytes)", "Frame Loss", "Latency (ns)", "Jitter (ns)"]
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.database = {}

    def record_data(self, port_name: str, description: str, traffic_rate: float, packet_size: int, frame_loss: int, latency: int, jitter: int) -> None:
        if port_name not in self.database:
            self.database[port_name] = []
        self.database[port_name].append({
            "Description": description,
            "Rate (%)": traffic_rate,
            "Packet Size (bytes)": packet_size,
            "Frame Loss": frame_loss,
            "Latency (ns)": latency,
            "Jitter (ns)": jitter,
        })
        
    
    def generate_report(self, filename: str) -> None:
        headers = [
            ["*******************************************"],
            ["Test:", self.name],
            ["Chassis:", self.chassis],
            ["Datetime:", self.datetime],
            []
        ]
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in headers:
                writer.writerow(line)
            for key, value in self.database.items():
                writer.writerow([key])
                dict_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                dict_writer.writeheader()
                for data in value:
                    dict_writer.writerow(data)
                writer.writerow([])

class TXTapReportGenerator:
    def __init__(self):
        self.name = "TX Tap Informaton"
        self.chassis = "10.10.10.10"
        self.fieldnames = ["Lane", "Pre3 (dB)", "Pre2 (dB)", "Pre (dB)", "Main (mV)", "Post (dB)"]
        self.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.database = {}

    def record_data(self, port_name: str, lane: int, pre3_db: float, pre2_db: float, pre_db: float, main_mv: int, post_db: float) -> None:
        time_str = time.strftime("%H:%M:%S", time.localtime())
        if port_name not in self.database:
            self.database[port_name] = []
        self.database[port_name].append({
            "Lane": lane,
            "Pre3 (dB)": pre3_db,
            "Pre2 (dB)": pre2_db,
            "Pre (dB)": pre_db,
            "Main (mV)": main_mv,
            "Post (dB)": post_db,
        })
    
    def generate_report(self, filename: str) -> None:
        headers = [
            ["*******************************************"],
            ["Test:", self.name],
            ["Chassis:", self.chassis],
            ["Datetime:", self.datetime],
            []
        ]
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in headers:
                writer.writerow(line)
            for key, value in self.database.items():
                writer.writerow([key])
                dict_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                dict_writer.writeheader()
                for data in value:
                    dict_writer.writerow(data)
                writer.writerow([])
