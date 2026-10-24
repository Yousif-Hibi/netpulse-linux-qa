import pytest

from src.network_chaos import run_udp_stress_test
from src.proc_telemetry import get_system_health, read_network_counters


def test_linux_proc_telemetry_structure():
    """Verify loopback telemetry structure and baseline counter integrity."""
    counters = read_network_counters("lo")

    assert counters["rx_bytes"] >= 0, f"Expected rx_bytes >= 0, got {counters['rx_bytes']}"
    assert counters["tx_bytes"] >= 0, f"Expected tx_bytes >= 0, got {counters['tx_bytes']}"
    assert counters["rx_errors"] == 0, f"Expected rx_errors == 0, got {counters['rx_errors']}"


@pytest.mark.parametrize("packet_count", [500, 2000, 5000])
def test_high_throughput_udp_burst(packet_count):
    """Verify network packet counter increases, loss stays below threshold, and throughput meets minimum target."""
    port = 10000 + packet_count

    # 1. Capture snapshot before the test
    before = read_network_counters("lo")

    # 2. Run stress test
    result = run_udp_stress_test(num_packets=packet_count, port=port)

    # 3. Capture snapshot after the test
    after = read_network_counters("lo")

    # 4. Verify loopback transmitted packet increase
    tx_diff = after["tx_packets"] - before["tx_packets"]
    assert tx_diff >= packet_count, (
        f"Transmitted packet delta ({tx_diff}) was lower than expected packet_count ({packet_count})"
    )

    # 5. Verify packet loss is under 1.0%
    assert result["packet_loss_percentage"] < 1.0, (
        f"Packet loss {result['packet_loss_percentage']}% exceeded threshold of 1.0%"
    )

    # 6. Verify throughput exceeds 1.0 Mbps
    assert result["throughput_mbps"] > 1.0, (
        f"Throughput {result['throughput_mbps']} Mbps was below required 1.0 Mbps"
    )


def test_system_resource_stability_under_load():
    """Ensure available RAM remains sufficient and usage does not jump drastically during load."""
    before_health = get_system_health()

    run_udp_stress_test(num_packets=3000, port=13000)

    after_health = get_system_health()

    # Assert available RAM remains above 100 MB
    assert after_health["memory_available_mb"] > 100, (
        f"Available RAM ({after_health['memory_available_mb']} MB) dropped below minimum 100 MB"
    )

    # Assert RAM percentage increase is not greater than 5%
    ram_usage_jump = after_health["memory"].percent - before_health["memory"].percent
    assert ram_usage_jump <= 5.0, (
        f"RAM usage jumped by {ram_usage_jump:.2f}%, exceeding the 5.0% threshold"
    )