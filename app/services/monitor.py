import psutil
import shutil
from app.schemas.metrics import CpuInfo, RamInfo, DiskInfo, ProcessInfo


class MonitorService:
    def get_cpu_info(self) -> CpuInfo:
        load = psutil.cpu_percent(interval=0.1)
        cores = psutil.cpu_count()
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0

        return CpuInfo(
            load_percent=load,
            core_count=cores,
            frequency_mhz=freq
        )

    def get_ram_info(self) -> RamInfo:
        mem = psutil.virtual_memory()
        return RamInfo(
            load_percent=mem.percent,
            used_gb=round(mem.used / (1024 ** 3), 2),
            total_gb=round(mem.total / (1024 ** 3), 2)
        )

    def get_disks_info(self) -> list[DiskInfo]:
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append(DiskInfo(
                    device=part.device,
                    mount_point=part.mountpoint,
                    used_percent=usage.percent,
                    total_gb=round(usage.total / (1024 ** 3), 2)
                ))
            except PermissionError:
                continue
        return disks

    def get_processes(self, name_filter: str = None, user_filter: str = None) -> list[ProcessInfo]:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                p_info = proc.info
                p_name = p_info['name'] or ""
                p_user = p_info['username'] or ""

                # 1. Фильтр по имени (если передан)
                # lower() делает поиск регистронезависимым (python найдет и Python, и python)
                if name_filter and name_filter.lower() not in p_name.lower():
                    continue  # Если имя не совпадает, пропускаем процесс

                # 2. Фильтр по пользователю (если передан)
                if user_filter and user_filter.lower() not in p_user.lower():
                    continue  # Если пользователь не совпадает, пропускаем

                processes.append(ProcessInfo(
                    pid=p_info['pid'],
                    name=p_name,
                    cpu_percent=p_info['cpu_percent'] or 0.0,
                    memory_percent=p_info['memory_percent'] or 0.0,
                    user=p_user
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda x: x.cpu_percent, reverse=True)

        return processes
    def kill_process(self, pid: int):
        if pid <= 100:
            raise ValueError("Cannot kill system process")

        try:
            p = psutil.Process(pid)
            p.terminate()
            return True
        except psutil.NoSuchProcess:
            return False