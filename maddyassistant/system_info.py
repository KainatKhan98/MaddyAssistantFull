import os
import shutil
import ctypes


def get_cpu_usage():
    # Simple Windows CPU usage using WMIC
    try:
        result = os.popen(
            'wmic cpu get loadpercentage /value'
        ).read()

        for line in result.splitlines():
            if 'LoadPercentage=' in line:
                return int(line.split('=')[1])

    except Exception:
        pass

    return 0


def get_ram_usage():
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]

        memory = MEMORYSTATUSEX()
        memory.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

        ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(memory)
        )

        return memory.dwMemoryLoad

    except Exception:
        return 0


def get_storage_usage():
    try:
        total, used, free = shutil.disk_usage("C:\\")

        return int((used / total) * 100)

    except Exception:
        return 0


def get_battery():
    try:
        class SYSTEM_POWER_STATUS(ctypes.Structure):
            _fields_ = [
                ('ACLineStatus', ctypes.c_byte),
                ('BatteryFlag', ctypes.c_byte),
                ('BatteryLifePercent', ctypes.c_byte),
                ('Reserved', ctypes.c_byte),
                ('BatteryLifeTime', ctypes.c_ulong),
                ('BatteryFullLifeTime', ctypes.c_ulong),
            ]

        status = SYSTEM_POWER_STATUS()

        ctypes.windll.kernel32.GetSystemPowerStatus(
            ctypes.byref(status)
        )

        if status.BatteryLifePercent == 255:
            return None

        return status.BatteryLifePercent

    except Exception:
        return None