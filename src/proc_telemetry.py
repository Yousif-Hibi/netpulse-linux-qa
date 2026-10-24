import time
import psutil

def read_network_counters(interface="lo"):
    with open("/proc/net/dev", "r") as f:
        lines = f.readlines()[2:]
    stats = {}
    for line in lines:
        iface , data = line.split(":", 1)
        fields = data.split()
        if iface.strip() != interface:
                    continue
        
        return {
           "rx_bytes":   int(fields[0]),
            "rx_packets": int(fields[1]),
            "rx_errors":  int(fields[2]),
            "rx_dropped": int(fields[3]),
            "tx_bytes":   int(fields[8]),
            "tx_packets": int(fields[9]),
            "tx_errors":  int(fields[10]),
            "tx_dropped": int(fields[11]),
        }
        
    raise ValueError(f"Interface '{interface}' not found.")    


def get_system_health():
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    memory_available = memory.available / (1024 * 1024)
    return {
        "cpu_percent": cpu,
        "memory_available_mb": memory_available,
        "memory" : memory
    }
    
if __name__ == "__main__":
    print(read_network_counters())  # loopback by default
    print("System Health:", get_system_health())
    try:
        print(read_network_counters("eth0"))
    except ValueError as e:
        print(e)
    