import os
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class FileChunk:
    chunk_id: int
    file_id: str
    size: int
    checksum: str
    storage_path: str
    node_id: str
    created_at: float = time.time()

class VirtualStorage:
    """Manages virtual storage across multiple nodes"""
    
    def __init__(self, node_id: str, storage_path: str = "storage/nodes"):
        self.node_id = node_id
        self.storage_path = os.path.join(storage_path, node_id)
        self.chunk_size = 64 * 1024  # 64KB as required
        
        # Create storage directory
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Track stored chunks: file_id -> list of chunks
        self.stored_chunks: Dict[str, List[FileChunk]] = {}
        
        # Storage metrics
        self.total_capacity = 500 * 1024 * 1024 * 1024  # 500GB
        self.used_capacity = 0
        
    def store_chunk(self, file_id: str, chunk_id: int, data: bytes) -> bool:
        """Store a chunk of data"""
        if self.used_capacity + len(data) > self.total_capacity:
            return False
        
        # Generate checksum
        checksum = hashlib.md5(data).hexdigest()
        
        # Create chunk file
        chunk_filename = f"{file_id}_chunk_{chunk_id}.bin"
        chunk_path = os.path.join(self.storage_path, chunk_filename)
        
        try:
            with open(chunk_path, 'wb') as f:
                f.write(data)
            
            # Update tracking
            chunk = FileChunk(
                chunk_id=chunk_id,
                file_id=file_id,
                size=len(data),
                checksum=checksum,
                storage_path=chunk_path,
                node_id=self.node_id
            )
            
            if file_id not in self.stored_chunks:
                self.stored_chunks[file_id] = []
            self.stored_chunks[file_id].append(chunk)
            
            self.used_capacity += len(data)
            
            print(f"[Storage {self.node_id}] Stored chunk {chunk_id} of file {file_id}")
            return True
            
        except Exception as e:
            print(f"[Storage {self.node_id}] Error storing chunk: {e}")
            return False
    
    def retrieve_chunk(self, file_id: str, chunk_id: int) -> Optional[bytes]:
        """Retrieve a chunk of data"""
        if file_id not in self.stored_chunks:
            return None
        
        for chunk in self.stored_chunks[file_id]:
            if chunk.chunk_id == chunk_id:
                try:
                    with open(chunk.storage_path, 'rb') as f:
                        data = f.read()
                    
                    # Verify checksum
                    if hashlib.md5(data).hexdigest() != chunk.checksum:
                        print(f"[Storage {self.node_id}] Checksum mismatch for chunk {chunk_id}")
                        return None
                    
                    return data
                except Exception as e:
                    print(f"[Storage {self.node_id}] Error reading chunk: {e}")
                    return None
        
        return None
    
    def split_file(self, file_path: str) -> Tuple[List[bytes], str]:
        """Split file into 64KB chunks (REQUIREMENT #14)"""
        file_id = hashlib.md5(f"{file_path}_{time.time()}".encode()).hexdigest()
        chunks = []
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk_data = f.read(self.chunk_size)
                    if not chunk_data:
                        break
                    chunks.append(chunk_data)
            
            print(f"[Storage] Split file into {len(chunks)} chunks of {self.chunk_size} bytes each")
            return chunks, file_id
            
        except Exception as e:
            print(f"[Storage] Error splitting file: {e}")
            return [], ""
    
    def get_storage_info(self) -> Dict:
        """Get storage utilization information"""
        return {
            "node_id": self.node_id,
            "total_capacity_gb": self.total_capacity / (1024**3),
            "used_capacity_gb": self.used_capacity / (1024**3),
            "available_capacity_gb": (self.total_capacity - self.used_capacity) / (1024**3),
            "utilization_percent": (self.used_capacity / self.total_capacity) * 100,
            "stored_files": len(self.stored_chunks),
            "total_chunks": sum(len(chunks) for chunks in self.stored_chunks.values())
        }