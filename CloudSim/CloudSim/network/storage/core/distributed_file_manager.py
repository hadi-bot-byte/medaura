import time
import random
from typing import Dict, List, Optional
from config import SystemConfig
from storage.virtual_storage import VirtualStorage

class DistributedFileManager:
    """Manages file distribution across multiple nodes (REQUIREMENT #13, #14)"""
    
    def __init__(self):
        self.nodes: Dict[str, VirtualStorage] = {}
        self.file_distribution: Dict[str, List[str]] = {}  # file_id -> [node_ids]
        self.chunk_distribution: Dict[str, Dict[int, List[str]]] = {}  # file_id -> {chunk_id: [node_ids]}
        
    def add_node(self, node_id: str, storage: VirtualStorage):
        """Add a storage node to the system"""
        self.nodes[node_id] = storage
    
    def distribute_file(self, file_path: str, replication_factor: int = 3) -> Optional[str]:
        """
        Distribute file across nodes with replication
        REQUIREMENT: File has to be distributed into different parts
        """
        if not self.nodes:
            print("[Distributor] No nodes available")
            return None
        
        # Split file into chunks
        source_node = list(self.nodes.keys())[0]
        chunks, file_id = self.nodes[source_node].split_file(file_path)
        
        if not chunks:
            return None
        
        print(f"[Distributor] Distributing file {file_id} with {len(chunks)} chunks")
        
        # Distribute each chunk to multiple nodes
        self.chunk_distribution[file_id] = {}
        
        for chunk_id, chunk_data in enumerate(chunks):
            # Select random nodes for replication
            available_nodes = list(self.nodes.keys())
            selected_nodes = random.sample(
                available_nodes, 
                min(replication_factor, len(available_nodes))
            )
            
            self.chunk_distribution[file_id][chunk_id] = selected_nodes
            
            # Store chunk on each selected node
            for node_id in selected_nodes:
                success = self.nodes[node_id].store_chunk(file_id, chunk_id, chunk_data)
                if not success:
                    print(f"[Distributor] Failed to store chunk {chunk_id} on node {node_id}")
        
        print(f"[Distributor] File {file_id} distributed across {len(self.nodes)} nodes")
        return file_id
    
    def retrieve_file(self, file_id: str, destination_path: str) -> bool:
        """Retrieve and reconstruct file from distributed storage"""
        if file_id not in self.chunk_distribution:
            print(f"[Distributor] File {file_id} not found")
            return False
        
        chunks_info = self.chunk_distribution[file_id]
        total_chunks = len(chunks_info)
        retrieved_chunks = [None] * total_chunks
        
        print(f"[Distributor] Retrieving file {file_id} with {total_chunks} chunks")
        
        # Retrieve each chunk from any available node
        for chunk_id, node_ids in chunks_info.items():
            for node_id in node_ids:
                if node_id in self.nodes:
                    chunk_data = self.nodes[node_id].retrieve_chunk(file_id, chunk_id)
                    if chunk_data:
                        retrieved_chunks[chunk_id] = chunk_data
                        break
        
        # Check if all chunks retrieved
        if any(chunk is None for chunk in retrieved_chunks):
            print(f"[Distributor] Failed to retrieve all chunks for file {file_id}")
            return False
        
        # Reconstruct file
        try:
            with open(destination_path, 'wb') as f:
                for chunk_data in retrieved_chunks:
                    f.write(chunk_data)
            
            print(f"[Distributor] File reconstructed at {destination_path}")
            return True
            
        except Exception as e:
            print(f"[Distributor] Error reconstructing file: {e}")
            return False
    
    def get_distribution_info(self, file_id: str) -> Dict:
        """Get information about how a file is distributed"""
        if file_id not in self.chunk_distribution:
            return {}
        
        distribution = {}
        for chunk_id, node_ids in self.chunk_distribution[file_id].items():
            distribution[f"chunk_{chunk_id}"] = node_ids
        
        return distribution