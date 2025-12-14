import time
import random
import socket
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

class PacketType(Enum):
    SYN = "SYN"
    SYN_ACK = "SYN_ACK"
    ACK = "ACK"
    DATA = "DATA"
    FIN = "FIN"
    HEARTBEAT = "HEARTBEAT"

@dataclass
class Packet:
    packet_id: int
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    packet_type: PacketType
    sequence_num: int
    acknowledgment_num: int
    data: bytes = b""
    timestamp: float = time.time()

class SimulatedTCP:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        self.sequence_num = random.randint(1000, 9000)
        self.receive_buffer: Dict[int, Packet] = {}
        self.sent_packets: Dict[int, Packet] = {}
        self.connections: Dict[tuple, Any] = {}  # (ip, port) -> connection state
        self.packet_loss_rate = 0.01
        self.network_delay_ms = 50
        self.is_running = True
        self.receive_callback: Optional[Callable] = None
        
        # Start receive thread
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def send_packet(self, dest_ip: str, dest_port: int, packet_type: PacketType, data: bytes = b"") -> bool:
        """Simulate sending a TCP packet"""
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            print(f"[TCP] Packet lost from {self.ip_address}:{self.port} to {dest_ip}:{dest_port}")
            return False
        
        # Create packet
        packet = Packet(
            packet_id=random.randint(1, 1000000),
            source_ip=self.ip_address,
            source_port=self.port,
            dest_ip=dest_ip,
            dest_port=dest_port,
            packet_type=packet_type,
            sequence_num=self.sequence_num,
            acknowledgment_num=0,
            data=data
        )
        
        self.sequence_num += len(data)
        self.sent_packets[packet.packet_id] = packet
        
        # Simulate network delay
        delay_seconds = self.network_delay_ms / 1000.0
        time.sleep(delay_seconds)
        
        # In real implementation, this would send to network
        print(f"[TCP] Sent {packet_type.value} packet from {self.ip_address}:{self.port} to {dest_ip}:{dest_port}")
        
        return True
    
    def receive_packet(self, packet: Packet) -> bool:
        """Process received packet"""
        if packet.dest_ip != self.ip_address or packet.dest_port != self.port:
            return False
        
        self.receive_buffer[packet.packet_id] = packet
        
        # Handle different packet types
        if packet.packet_type == PacketType.HEARTBEAT:
            # Send ACK for heartbeat
            self.send_packet(
                packet.source_ip, packet.source_port,
                PacketType.ACK, b"HEARTBEAT_ACK"
            )
        
        elif packet.packet_type == PacketType.DATA:
            # Send ACK for data
            ack_data = f"ACK:{packet.sequence_num}".encode()
            self.send_packet(
                packet.source_ip, packet.source_port,
                PacketType.ACK, ack_data
            )
            
            if self.receive_callback:
                self.receive_callback(packet)
        
        return True
    
    def _receive_loop(self):
        """Simulated receive loop"""
        while self.is_running:
            time.sleep(0.1)  # Check for packets every 100ms
    
    def send_data(self, dest_ip: str, dest_port: int, data: bytes) -> bool:
        """Send data with TCP-like reliability"""
        # Simulate three-way handshake
        if not self.send_packet(dest_ip, dest_port, PacketType.SYN):
            return False
        
        # Wait for SYN-ACK (simulated)
        time.sleep(self.network_delay_ms / 1000.0 * 2)
        
        # Send ACK
        if not self.send_packet(dest_ip, dest_port, PacketType.SYN_ACK):
            return False
        
        # Send data in chunks
        chunk_size = 1460  # Typical TCP MSS
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if not self.send_packet(dest_ip, dest_port, PacketType.DATA, chunk):
                # Retry logic
                if not self.send_packet(dest_ip, dest_port, PacketType.DATA, chunk):
                    return False
        
        # Close connection
        self.send_packet(dest_ip, dest_port, PacketType.FIN)
        
        return True
    
    def set_receive_callback(self, callback: Callable):
        """Set callback for received data"""
        self.receive_callback = callback
    
    def stop(self):
        """Stop the TCP simulation"""
        self.is_running = False