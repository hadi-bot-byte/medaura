from dataclasses import dataclass
from enum import Enum
import time

class PacketType(Enum):
    SYN = 1
    SYN_ACK = 2
    ACK = 3
    DATA = 4
    FIN = 5
    HEARTBEAT = 6

@dataclass
class NetworkPacket:
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
    
    def to_bytes(self) -> bytes:
        """Convert packet to bytes for transmission"""
        # This is a simplified version
        header = f"{self.packet_id}|{self.source_ip}:{self.source_port}|{self.dest_ip}:{self.dest_port}|{self.packet_type.value}|{self.sequence_num}|{self.acknowledgment_num}"
        return header.encode() + b"||" + self.data
    
    @staticmethod
    def from_bytes(data: bytes) -> 'NetworkPacket':
        """Create packet from bytes"""
        try:
            header, packet_data = data.split(b"||", 1)
            parts = header.decode().split("|")
            
            return NetworkPacket(
                packet_id=int(parts[0]),
                source_ip=parts[1].split(":")[0],
                source_port=int(parts[1].split(":")[1]),
                dest_ip=parts[2].split(":")[0],
                dest_port=int(parts[2].split(":")[1]),
                packet_type=PacketType(int(parts[3])),
                sequence_num=int(parts[4]),
                acknowledgment_num=int(parts[5]),
                data=packet_data
            )
        except:
            raise ValueError("Invalid packet data")