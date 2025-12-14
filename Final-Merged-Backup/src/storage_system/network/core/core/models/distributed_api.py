from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import time
from typing import Dict, List
from core.virtual_machine import VirtualMachine
from core.file_distributor import FileDistributor
from config import SystemConfig

app = FastAPI(title="Distributed Storage API", version="1.0.0")

class DistributedAPI:
    def __init__(self):
        self.virtual_machines: Dict[str, VirtualMachine] = {}
        self.file_distributor: Optional[FileDistributor] = None
        self.distributed_files: Dict[str, 'DistributedFile'] = {}
        
    def initialize_system(self):
        """Initialize the distributed system with nodes"""
        print("[dAPI] Initializing distributed system...")
        
        # Create virtual machines for each node
        for node_config in SystemConfig.NODES:
            vm = VirtualMachine(node_config)
            self.virtual_machines[node_config.node_id] = vm
        
        # Connect nodes to each other
        for i, node1 in enumerate(SystemConfig.NODES):
            for j, node2 in enumerate(SystemConfig.NODES):
                if i != j:
                    self.virtual_machines[node1.node_id].add_known_node(
                        node2.node_id, node2.ip_address, node2.port
                    )
        
        # Initialize file distributor
        self.file_distributor = FileDistributor(self.virtual_machines)
        
        print(f"[dAPI] System initialized with {len(self.virtual_machines)} nodes")
    
    def upload_file(self, file_path: str) -> Dict:
        """Upload and distribute a file"""
        if not self.file_distributor:
            raise RuntimeError("System not initialized")
        
        start_time = time.time()
        
        # Distribute file
        distributed_file = self.file_distributor.distribute_file(file_path)
        
        if not distributed_file:
            raise RuntimeError("Failed to distribute file")
        
        # Store file metadata
        self.distributed_files[distributed_file.file_id] = distributed_file
        
        end_time = time.time()
        upload_time = end_time - start_time
        
        return {
            "file_id": distributed_file.file_id,
            "total_chunks": distributed_file.total_chunks,
            "total_size": distributed_file.total_size,
            "upload_time": upload_time,
            "chunk_distribution": distributed_file.get_chunk_distribution()
        }
    
    def get_system_status(self) -> Dict:
        """Get status of entire distributed system"""
        node_statuses = {}
        total_storage = 0
        used_storage = 0
        
        for node_id, vm in self.virtual_machines.items():
            node_info = vm.get_node_info()
            node_statuses[node_id] = node_info
            
            total_storage += node_info['storage']['total']
            used_storage += node_info['storage']['used']
        
        return {
            "total_nodes": len(self.virtual_machines),
            "active_nodes": len([n for n in node_statuses.values() if n['is_alive']]),
            "storage": {
                "total": total_storage,
                "used": used_storage,
                "available": total_storage - used_storage,
                "utilization_percentage": (used_storage / total_storage) * 100 if total_storage > 0 else 0
            },
            "files_stored": len(self.distributed_files),
            "nodes": node_statuses
        }

# Global API instance
dapi = DistributedAPI()

@app.on_event("startup")
async def startup_event():
    dapi.initialize_system()

@app.get("/")
async def root():
    return {"message": "Distributed Storage API", "status": "running"}

@app.get("/status")
async def get_status():
    return dapi.get_system_status()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the distributed system"""
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = dapi.upload_file(temp_path)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get information about a distributed file"""
    if file_id not in dapi.distributed_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file = dapi.distributed_files[file_id]
    return {
        "file_id": file.file_id,
        "original_path": file.original_path,
        "total_size": file.total_size,
        "total_chunks": file.total_chunks,
        "created_at": file.created_at,
        "chunk_distribution": file.get_chunk_distribution()
    }

@app.get("/nodes")
async def get_nodes():
    """Get all nodes information"""
    nodes_info = {}
    for node_id, vm in dapi.virtual_machines.items():
        nodes_info[node_id] = vm.get_node_info()
    return nodes_info

@app.get("/simulate/transfer")
async def simulate_transfer(source: str, target: str, size_kb: int = 64):
    """Simulate file transfer and measure time"""
    if source not in dapi.virtual_machines or target not in dapi.virtual_machines:
        raise HTTPException(status_code=404, detail="Node not found")
    
    chunk_size = size_kb * 1024
    transfer_time = dapi.file_distributor.measure_transfer_time(source, target, chunk_size)
    
    return {
        "source": source,
        "target": target,
        "size_bytes": chunk_size,
        "transfer_time_seconds": transfer_time,
        "throughput_mbps": (chunk_size * 8) / (transfer_time * 1000000)
    }