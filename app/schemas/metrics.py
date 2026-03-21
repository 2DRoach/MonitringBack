from pydantic import BaseModel
from typing import List

class CpuInfo(BaseModel):
    load_percent: float
    core_count: int
    frequency_mhz: float

class RamInfo(BaseModel):
    load_percent: float
    used_gb: float
    total_gb: float

class DiskInfo(BaseModel):
    device: str
    mount_point: str
    used_percent: float
    total_gb: float

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    user: str

class DashboardResponse(BaseModel):
    cpu: CpuInfo
    ram: RamInfo
    disks: List[DiskInfo]