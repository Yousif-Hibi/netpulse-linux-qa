import socket 
import threading
import time

def run_udp_stress_test(port =9999, num_packets=1000, payload_size=512):
    received_packets = 0
    stop_event = threading.Event()
    all_packets_received = threading.Event()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    buffer_size = 4*1024*1024  # 4MB buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
    sock.bind(("127.0.0.1", port))
    sock.settimeout(0.2) 

    def receiver_worker():
        nonlocal received_packets
        while not stop_event.is_set():
            try:
                data, _ = sock.recvfrom(65535)
                if data:
                    received_packets += 1
                    if received_packets >= num_packets:
                        all_packets_received.set()
            except socket.timeout:
                continue

    recv_thread = threading.Thread(target=receiver_worker, daemon=True)
    recv_thread.start()
    
    try:
        payload = b"A" * payload_size
        start_time = time.perf_counter()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for _ in range(num_packets):
                sender.sendto(payload, ("127.0.0.1", port))

        if num_packets > 0:
            all_packets_received.wait(timeout=1.0)
    finally:
        stop_event.set()
        recv_thread.join()
        sock.close()

    elapsed_time = time.perf_counter() - start_time
    total_megabits = (received_packets * payload_size * 8) / 1_000_000
    throughput_mbps = (total_megabits / elapsed_time) if elapsed_time > 0 else 0.0
    packet_loss_pct = (((num_packets - received_packets) / num_packets) * 100) if num_packets > 0 else 0.0

    return {
        "sent_packets": num_packets,
        "received_packets": received_packets,
        "payload_size_bytes": payload_size,
        "elapsed_seconds": round(elapsed_time, 6),
        "total_megabits": round(total_megabits, 4),
        "throughput_mbps": round(throughput_mbps, 4),
        "packet_loss_percentage": round(packet_loss_pct, 2)
    }