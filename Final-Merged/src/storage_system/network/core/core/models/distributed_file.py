from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class FileChunk:
    chunk_id: int
    file_id: str
    size: int  # in bytes
    checksum: str
    nodes_assigned: List[str]  # Nodes where this chunk is stored
    created_at: float = time.time()
    retrieved_count: int = 0

@dataclass
class DistributedFile:
    file_id: str
    original_path: str
    total_size: int
    total_chunks: int
    chunks: List[FileChunk] = None
    created_at: float = time.time()
    last_accessed: Optional[float] = None
    
    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []
    
    def get_chunk_distribution(self) -> Dict[int, List[str]]:
        """Get which nodes store each chunk"""
        return {chunk.chunk_id: chunk.nodes_assigned for chunk in self.chunks}
    
    def verify_integrity(self, chunk_data: bytes, chunk_id: int) -> bool:
        """Verify chunk integrity using checksum"""
        chunk = next((c for c in self.chunks if c.chunk_id == chunk_id), None)
        if not chunk:
            return False
        
        calculated_checksum = hashlib.md5(chunk_data).hexdigest()
        return calculated_checksum == chunk.checksum