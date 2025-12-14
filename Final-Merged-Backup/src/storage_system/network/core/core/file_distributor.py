import hashlib
import time
import os
from typing import Dict, List, Tuple, Optional
from config import SystemConfig
from models.distributed_file import DistributedFile, FileChunk

class FileDistributor:
    def __init__(self, nodes: Dict[str, 'VirtualMachine']):
        self.nodes = nodes
        self.chunk_size = SystemConfig.CHUNK_SIZE
        self.replication_factor = SystemConfig.REPLICATION_FACTOR
        
    def split_file_into_chunks(self, file_path: str) -> Tuple[List[FileChunk], str]:
        """Split file into chunks for distribution"""
        file_id = hashlib.md5(f"{file_path}_{time.time()}".encode()).hexdigest()
        chunks = []
        
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'rb') as f:
                chunk_id = 0
                while True:
                    chunk_data = f.read(self.chunk_size)
                    if not chunk_data:
                        break
                    
                    chunk = FileChunk(
                        chunk_id=chunk_id,
                        file_id=file_id,
                        size=len(chunk_data),
                        checksum=hashlib.md5(chunk_data).hexdigest(),
                        nodes_assigned=[],
                        created_at=time.time()
                    )
                    chunks.append(chunk)
                    chunk_id += 1
            
            return chunks, file_id
            
        except Exception as e:
            print(f"Error splitting file: {e}")
            return [], ""
    
    def select_nodes_for_chunk(self, chunk: FileChunk, exclude_nodes: List[str] = None) -> List[str]:
        """Select nodes to store a chunk (with replication)"""
        available_nodes = list(self.nodes.keys())
        
        if exclude_nodes:
            available_nodes = [n for n in available_nodes if n not in exclude_nodes]
        
        # Sort nodes by available storage (most available first)
        sorted_nodes = sorted(
            available_nodes,
            key=lambda n: self.nodes[n].storage_node.total_storage - self.nodes[n].storage_node.used_storage,
            reverse=True
        )
        
        # Select nodes for replication
        selected_nodes = sorted_nodes[:min(self.replication_factor, len(sorted_nodes))]
        return selected_nodes
    
    def distribute_file(self, file_path: str) -> Optional[DistributedFile]:
        """Distribute file across nodes"""
        chunks, file_id = self.split_file_into_chunks(file_path)
        
        if not chunks:
            return None
        
        distributed_file = DistributedFile(
            file_id=file_id,
            original_path=file_path,
            total_size=sum(chunk.size for chunk in chunks),
            total_chunks=len(chunks),
            created_at=time.time()
        )
        
        # Distribute each chunk
        for chunk in chunks:
            selected_nodes = self.select_nodes_for_chunk(chunk)
            chunk.nodes_assigned = selected_nodes
            distributed_file.chunks.append(chunk)
            
            print(f"[Distributor] Chunk {chunk.chunk_id} assigned to nodes: {selected_nodes}")
        
        return distributed_file
    
    def measure_transfer_time(self, source_node: str, target_node: str, chunk_size: int) -> float:
        """Measure transfer time between nodes"""
        start_time = time.time()
        
        # Simulate transfer based on bandwidth
        source_bandwidth = self.nodes[source_node].config.bandwidth_mbps
        target_bandwidth = self.nodes[target_node].config.bandwidth_mbps
        
        # Use minimum bandwidth
        effective_bandwidth = min(source_bandwidth, target_bandwidth)
        
        # Calculate transfer time (size in bits / bandwidth in bits per second)
        transfer_time_seconds = (chunk_size * 8) / (effective_bandwidth * 1000000)
        
        # Add network delay
        transfer_time_seconds += SystemConfig.NETWORK_DELAY_MS / 1000.0
        
        time.sleep(transfer_time_seconds)  # Simulate transfer
        
        end_time = time.time()
        actual_time = end_time - start_time
        
        print(f"[Distributor] Transfer time: {actual_time:.4f}s for {chunk_size} bytes")
        return actual_time