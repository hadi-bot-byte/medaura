import os
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import NodeConfig, SystemConfig
from network.simulated_tcp import SimulatedTCP, Packet
from storage_virtual_node import StorageVirtualNode

@dataclass
class NodeStatus:
    is_alive: bool = True
    last_heartbeat: float = 0
    load_percentage: float = 0
    storage_used_percentage: float = 0

class VirtualMachine:
    def __init__(self, node_config: NodeConfig):
        self.config = node_config
        self.status = NodeStatus()
        
        # Create virtual storage node
        self.storage_node = StorageVirtualNode(
            node_id=node_config.node_id,
            cpu_capacity=node_config.cpu_cores,
            memory_capacity=node_config.memory_gb,
            storage_capacity=node_config.storage_gb,
            bandwidth=node_config.bandwidth_mbps
        )
        
        # Create network interface
        self.tcp_interface = SimulatedTCP(node_config.ip_address, node_config.port)
        self.tcp_interface.set_receive_callback(self._handle_received_packet)
        
        # Create virtual storage directory
        self.storage_path = f"storage/{node_config.node_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Node monitoring
        self.known_nodes: Dict[str, NodeStatus] = {}
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
        
        # File chunk storage tracking
        self.stored_chunks: Dict[str, List[str]] = {}  # file_id -> [chunk_ids]
        self.chunk_locations: Dict[str, str] = {}  # chunk_id -> file_path
        
        print(f"[VM] Node {node_config.node_id} initialized at {node_config.ip_address}:{node_config.port}")
    
    def _handle_received_packet(self, packet: Packet):
        """Handle incoming packets"""
        if packet.packet_type.name == "DATA":
            print(f"[VM {self.config.node_id}] Received data from {packet.source_ip}:{packet.source_port}")
            # Process the data (would be implemented based on protocol)
    
    def _heartbeat_monitor(self):
        """Monitor node health"""
        while True:
            current_time = time.time()
            
            # Check known nodes
            for node_id, status in list(self.known_nodes.items()):
                if current_time - status.last_heartbeat > SystemConfig.HEARTBEAT_TIMEOUT:
                    status.is_alive = False
                    print(f"[VM {self.config.node_id}] Node {node_id} is DEAD")
            
            # Send heartbeat to known nodes (simulated)
            for node_id, status in self.known_nodes.items():
                if status.is_alive:
                    # Simulate sending heartbeat
                    status.last_heartbeat = time.time()
            
            time.sleep(SystemConfig.HEARTBEAT_INTERVAL)
    
    def add_known_node(self, node_id: str, ip: str, port: int):
        """Add a node to known nodes list"""
        self.known_nodes[node_id] = NodeStatus(last_heartbeat=time.time())
        self.storage_node.add_connection(node_id, self.config.bandwidth_mbps)
    
    def store_chunk(self, file_id: str, chunk_id: int, chunk_data: bytes) -> bool:
        """Store a file chunk on this node"""
        chunk_filename = f"{file_id}_chunk_{chunk_id}.bin"
        chunk_path = os.path.join(self.storage_path, chunk_filename)
        
        try:
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data)
            
            # Update tracking
            if file_id not in self.stored_chunks:
                self.stored_chunks[file_id] = []
            self.stored_chunks[file_id].append(str(chunk_id))
            self.chunk_locations[f"{file_id}_{chunk_id}"] = chunk_path
            
            # Update storage usage
            self.storage_node.used_storage += len(chunk_data)
            
            print(f"[VM {self.config.node_id}] Stored chunk {chunk_id} of file {file_id}")
            return True
        except Exception as e:
            print(f"[VM {self.config.node_id}] Failed to store chunk: {e}")
            return False
    
    def retrieve_chunk(self, file_id: str, chunk_id: int) -> Optional[bytes]:
        """Retrieve a file chunk from this node"""
        chunk_path = self.chunk_locations.get(f"{file_id}_{chunk_id}")
        
        if not chunk_path or not os.path.exists(chunk_path):
            return None
        
        try:
            with open(chunk_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"[VM {self.config.node_id}] Failed to retrieve chunk: {e}")
            return None
    
    def get_node_info(self) -> Dict:
        """Get node information"""
        return {
            "node_id": self.config.node_id,
            "ip_address": self.config.ip_address,
            "port": self.config.port,
            "is_alive": self.status.is_alive,
            "storage": {
                "total": self.storage_node.total_storage,
                "used": self.storage_node.used_storage,
                "available": self.storage_node.total_storage - self.storage_node.used_storage,
                "used_percentage": (self.storage_node.used_storage / self.storage_node.total_storage) * 100
            },
            "stored_files": len(self.stored_chunks),
            "known_nodes": list(self.known_nodes.keys())
        }
    
    def get_storage_utilization(self) -> float:
        """Get storage utilization percentage"""
        return (self.storage_node.used_storage / self.storage_node.total_storage) * 100