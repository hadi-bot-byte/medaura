import json
import os
from dataclasses import dataclass
from typing import List, Dict

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
    # Network simulation
    NETWORK_DELAY_MS = 50
    PACKET_LOSS_RATE = 0.01
    HEARTBEAT_INTERVAL = 5
    HEARTBEAT_TIMEOUT = 15
    
    # Storage configuration
    CHUNK_SIZE = 64 * 1024  # 64KB chunks as required
    REPLICATION_FACTOR = 3
    SIMULATION_FILE_SIZE = 64 * 1024  # 64KB for timing
    
    # 5 nodes as required with IP addresses you assign
    NODES: List[NodeConfig] = [
        NodeConfig("node1", "192.168.1.101", 8001, 4, 16, 500, 1000),
        NodeConfig("node2", "192.168.1.102", 8002, 4, 16, 500, 1000),
        NodeConfig("node3", "192.168.1.103", 8003, 4, 16, 500, 1000),
        NodeConfig("node4", "192.168.1.104", 8004, 4, 16, 500, 1000),
        NodeConfig("node5", "192.168.1.105", 8005, 4, 16, 500, 1000),
    ]
    
    @classmethod
    def get_node_by_id(cls, node_id: str) -> NodeConfig:
        for node in cls.NODES:
            if node.node_id == node_id:
                return node
        return None

# Save config
def save_config():
    config_data = {
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
    
    with open("system_config.json", "w") as f:
        json.dump(config_data, f, indent=2)

save_config()