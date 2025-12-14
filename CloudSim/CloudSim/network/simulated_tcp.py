import time
import random
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable

class PacketType(Enum):
    SYN = 1
    SYN_ACK = 2
    ACK = 3
    DATA = 4
    FIN = 5
    HEARTBEAT = 6

@dataclass
class TCPPacket:
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    packet_type: PacketType
    seq_num: int
    ack_num: int
    data: bytes = b""
    timestamp: float = 0

class SimulatedTCP:
    """Simulates TCP/IP layer with timing measurement"""
    
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        self.seq_number = random.randint(1000, 9000)
        self.packet_loss_rate = 0.01
        self.network_delay = 0.05  # 50ms
        self.is_running = True
        
        # For timing measurement (64KB file transfer)
        self.transfer_start_time = 0
        self.transfer_end_time = 0
        
        # Callback for received data
        self.data_received_callback: Optional[Callable] = None
        
    def send_packet(self, packet: TCPPacket) -> bool:
        """Simulate sending a TCP packet with possible loss"""
        if random.random() < self.packet_loss_rate:
            print(f"[TCP] Packet lost from {packet.source_ip}:{packet.source_port} "
                  f"to {packet.dest_ip}:{packet.dest_port}")
            return False
        
        # Simulate network delay
        time.sleep(self.network_delay)
        
        print(f"[TCP] Packet sent: {packet.packet_type.name} from "
              f"{packet.source_ip}:{packet.source_port} to "
              f"{packet.dest_ip}:{packet.dest_port}")
        
        return True
    
    def receive_packet(self, packet: TCPPacket) -> bool:
        """Receive and process a TCP packet"""
        if packet.dest_ip != self.ip_address or packet.dest_port != self.port:
            return False
        
        # Send ACK for DATA packets
        if packet.packet_type == PacketType.DATA:
            ack_packet = TCPPacket(
                source_ip=self.ip_address,
                source_port=self.port,
                dest_ip=packet.source_ip,
                dest_port=packet.source_port,
                packet_type=PacketType.ACK,
                seq_num=self.seq_number,
                ack_num=packet.seq_num + len(packet.data)
            )
            self.send_packet(ack_packet)
            
            # Call callback if data received
            if self.data_received_callback and packet.data:
                self.data_received_callback(packet.data)
        
        return True
    
    def send_data(self, dest_ip: str, dest_port: int, data: bytes) -> float:
        """
        Send data with TCP simulation and return transfer time
        Implements 3-way handshake and timing
        """
        print(f"[TCP] Starting transfer of {len(data)} bytes to {dest_ip}:{dest_port}")
        
        # Start timing (REQUIREMENT #10)
        self.transfer_start_time = time.time()
        
        # Simulate 3-way handshake
        syn_packet = TCPPacket(
            source_ip=self.ip_address,
            source_port=self.port,
            dest_ip=dest_ip,
            dest_port=dest_port,
            packet_type=PacketType.SYN,
            seq_num=self.seq_number,
            ack_num=0
        )
        
        if not self.send_packet(syn_packet):
            return -1  # Failed
        
        # Wait for SYN-ACK (simulated)
        time.sleep(self.network_delay * 2)
        
        # Send ACK
        ack_packet = TCPPacket(
            source_ip=self.ip_address,
            source_port=self.port,
            dest_ip=dest_ip,
            dest_port=dest_port,
            packet_type=PacketType.ACK,
            seq_num=self.seq_number + 1,
            ack_num=self.seq_number + 1
        )
        self.send_packet(ack_packet)
        
        # Send data in chunks (64KB as required)
        chunk_size = 64 * 1024
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            
            data_packet = TCPPacket(
                source_ip=self.ip_address,
                source_port=self.port,
                dest_ip=dest_ip,
                dest_port=dest_port,
                packet_type=PacketType.DATA,
                seq_num=self.seq_number + i,
                ack_num=0,
                data=chunk
            )
            
            if not self.send_packet(data_packet):
                # Retry once
                print(f"[TCP] Retrying chunk {i//chunk_size}")
                if not self.send_packet(data_packet):
                    return -1  # Failed
        
        # Close connection
        fin_packet = TCPPacket(
            source_ip=self.ip_address,
            source_port=self.port,
            dest_ip=dest_ip,
            dest_port=dest_port,
            packet_type=PacketType.FIN,
            seq_num=self.seq_number + len(data),
            ack_num=0
        )
        self.send_packet(fin_packet)
        
        # End timing
        self.transfer_end_time = time.time()
        transfer_time = self.transfer_end_time - self.transfer_start_time
        
        print(f"[TCP] Transfer completed in {transfer_time:.4f} seconds")
        return transfer_time
    
    def set_data_received_callback(self, callback: Callable):
        self.data_received_callback = callback