import time
import threading
from typing import Dict, List
from config import SystemConfig, NodeConfig
from network.simulated_tcp import SimulatedTCP
from storage.virtual_storage import VirtualStorage
from core.distributed_file_manager import DistributedFileManager

class DistributedSystem:
    """Main distributed system that coordinates everything"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.file_manager = DistributedFileManager()
        self.heartbeat_threads = []
        
        # Initialize 5 nodes as required
        self.initialize_nodes()
    
    def initialize_nodes(self):
        """Initialize 5 nodes with IP addresses (REQUIREMENT #7)"""
        print("[System] Initializing 5 distributed nodes...")
        
        for node_config in SystemConfig.NODES:
            # Create virtual storage for each node
            storage = VirtualStorage(node_config.node_id)
            
            # Create TCP/IP simulation for each node
            tcp_sim = SimulatedTCP(node_config.ip_address, node_config.port)
            
            # Store node information
            self.nodes[node_config.node_id] = {
                "config": node_config,
                "storage": storage,
                "tcp": tcp_sim,
                "is_alive": True,
                "last_heartbeat": time.time()
            }
            
            # Add to file manager
            self.file_manager.add_node(node_config.node_id, storage)
            
            print(f"[System] Node {node_config.node_id} initialized at "
                  f"{node_config.ip_address}:{node_config.port}")
        
        print(f"[System] {len(self.nodes)} nodes initialized successfully")
    
    def start_heartbeat_monitor(self):
        """Monitor node health (REQUIREMENT: VM should determine if node is alive)"""
        def monitor():
            while True:
                current_time = time.time()
                for node_id, node_info in self.nodes.items():
                    if current_time - node_info["last_heartbeat"] > SystemConfig.HEARTBEAT_TIMEOUT:
                        node_info["is_alive"] = False
                        print(f"[Heartbeat] Node {node_id} is DEAD")
                    else:
                        # Simulate sending heartbeat
                        node_info["last_heartbeat"] = time.time()
                
                time.sleep(SystemConfig.HEARTBEAT_INTERVAL)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.heartbeat_threads.append(monitor_thread)
    
    def upload_file(self, file_path: str) -> Dict:
        """Upload and distribute a file (REQUIREMENT #15, #16)"""
        start_time = time.time()
        
        print(f"[System] Uploading file: {file_path}")
        
        # Distribute file across nodes
        file_id = self.file_manager.distribute_file(file_path, SystemConfig.REPLICATION_FACTOR)
        
        if not file_id:
            return {"success": False, "error": "Failed to distribute file"}
        
        # Simulate 64KB file transfer timing (REQUIREMENT #10)
        if len(self.nodes) >= 2:
            node_ids = list(self.nodes.keys())
            source_node = node_ids[0]
            target_node = node_ids[1]
            
            # Create 64KB test data
            test_data = b"X" * SystemConfig.SIMULATION_FILE_SIZE
            
            # Measure transfer time
            transfer_time = self.nodes[source_node]["tcp"].send_data(
                self.nodes[target_node]["config"].ip_address,
                self.nodes[target_node]["config"].port,
                test_data
            )
            
            print(f"[System] 64KB transfer simulation: {transfer_time:.4f} seconds")
        
        end_time = time.time()
        upload_time = end_time - start_time
        
        return {
            "success": True,
            "file_id": file_id,
            "upload_time": upload_time,
            "distribution": self.file_manager.get_distribution_info(file_id)
        }
    
    def download_file(self, file_id: str, destination_path: str) -> Dict:
        """Download file from distributed storage"""
        start_time = time.time()
        
        print(f"[System] Downloading file: {file_id}")
        
        success = self.file_manager.retrieve_file(file_id, destination_path)
        
        end_time = time.time()
        download_time = end_time - start_time
        
        return {
            "success": success,
            "download_time": download_time,
            "destination": destination_path
        }
    
    def get_system_status(self) -> Dict:
        """Get status of entire distributed system"""
        node_statuses = {}
        total_storage_gb = 0
        used_storage_gb = 0
        alive_nodes = 0
        
        for node_id, node_info in self.nodes.items():
            storage_info = node_info["storage"].get_storage_info()
            node_statuses[node_id] = {
                "ip_address": node_info["config"].ip_address,
                "port": node_info["config"].port,
                "is_alive": node_info["is_alive"],
                "storage": storage_info
            }
            
            total_storage_gb += storage_info["total_capacity_gb"]
            used_storage_gb += storage_info["used_capacity_gb"]
            
            if node_info["is_alive"]:
                alive_nodes += 1
        
        return {
            "total_nodes": len(self.nodes),
            "alive_nodes": alive_nodes,
            "total_storage_gb": total_storage_gb,
            "used_storage_gb": used_storage_gb,
            "available_storage_gb": total_storage_gb - used_storage_gb,
            "storage_utilization_percent": (used_storage_gb / total_storage_gb) * 100 if total_storage_gb > 0 else 0,
            "nodes": node_statuses
        }