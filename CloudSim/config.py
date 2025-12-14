import json
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class NodeConfig:
    node_id: str
    ip_address: str
    port: int
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    bandwidth_mbps: int

class SystemConfig:
    # Network configuration
    NETWORK_DELAY_MS = 50  # Simulated network delay
    PACKET_LOSS_RATE = 0.01  # 1% packet loss
    HEARTBEAT_INTERVAL = 5  # seconds
    HEARTBEAT_TIMEOUT = 15  # seconds
    
    # Storage configuration
    CHUNK_SIZE = 64 * 1024  # 64KB chunks
    REPLICATION_FACTOR = 3
    MAX_NODES = 10
    
    # File transfer simulation
    SIMULATION_FILE_SIZE = 64 * 1024  # 64KB for timing
    
    # Node configurations
    NODES: List[NodeConfig] = [
        NodeConfig("node1", "192.168.1.101", 8001, 4, 16, 500, 1000),
        NodeConfig("node2", "192.168.1.102", 8002, 4, 16, 500, 1000),
        NodeConfig("node3", "192.168.1.103", 8003, 4, 16, 500, 1000),
        NodeConfig("node4", "192.168.1.104", 8004, 4, 16, 500, 1000),
        NodeConfig("node5", "192.168.1.105", 8005, 4, 16, 500, 1000),
    ]
    
    @staticmethod
    def save_config(path: str = "config.json"):
        """Save configuration to file"""
        config_dict = {
            "network_delay_ms": SystemConfig.NETWORK_DELAY_MS,
            "packet_loss_rate": SystemConfig.PACKET_LOSS_RATE,
            "chunk_size": SystemConfig.CHUNK_SIZE,
            "replication_factor": SystemConfig.REPLICATION_FACTOR,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "ip_address": node.ip_address,
                    "port": node.port,
                    "cpu_cores": node.cpu_cores,
                    "memory_gb": node.memory_gb,
                    "storage_gb": node.storage_gb,
                    "bandwidth_mbps": node.bandwidth_mbps
                }
                for node in SystemConfig.NODES
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @staticmethod
    def load_config(path: str = "config.json"):
        """Load configuration from file"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                config_dict = json.load(f)
            
            SystemConfig.NETWORK_DELAY_MS = config_dict.get("network_delay_ms", 50)
            SystemConfig.PACKET_LOSS_RATE = config_dict.get("packet_loss_rate", 0.01)
            SystemConfig.CHUNK_SIZE = config_dict.get("chunk_size", 64 * 1024)
            SystemConfig.REPLICATION_FACTOR = config_dict.get("replication_factor", 3)
            
            SystemConfig.NODES = []
            for node_data in config_dict.get("nodes", []):
                SystemConfig.NODES.append(NodeConfig(**node_data))