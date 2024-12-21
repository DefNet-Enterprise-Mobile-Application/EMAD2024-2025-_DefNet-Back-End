from fastapi import APIRouter, HTTPException
import os, subprocess

router = APIRouter()

def get_wireless_interfaces():
    try:
        result = subprocess.run(['iwinfo'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        interfaces = []
        for line in lines:
            if 'ESSID' in line:
                interface = line.split()[0]
                interfaces.append(interface)
        return interfaces
    except Exception as e:
        print(f"Error getting wireless interfaces: {e}")
        return []

def get_connected_devices():
    devices = []
    try:
        result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                device = {
                    "ip": parts[0],
                    "mac": parts[4],
                    "interface": parts[2]
                }
                devices.append(device)
    except Exception as e:
        print(f"Error getting connected devices: {e}")
    return devices

def parse_dhcp_leases(file_path="/tmp/dhcp.leases"):
    leases = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    lease = {
                        "lease_time": parts[0],
                        "mac": parts[1],
                        "ip": parts[2],
                        "hostname": parts[3]
                    }
                    leases.append(lease)
    return leases

def get_network_stats():
    network_stats = {}
    for interface in os.listdir('/sys/class/net/'):
        stats_path = f"/sys/class/net/{interface}/statistics"
        if os.path.exists(stats_path):
            with open(os.path.join(stats_path, "tx_bytes"), "r") as f:
                tx_bytes = f.read().strip()
            with open(os.path.join(stats_path, "rx_bytes"), "r") as f:
                rx_bytes = f.read().strip()
            network_stats[interface] = {
                "tx_bytes": tx_bytes,
                "rx_bytes": rx_bytes
            }
    return network_stats

@router.get("/devices")
async def get_connected_devices_controller():
    try:
        # Ottieni le interfacce wireless
        wireless_interfaces = get_wireless_interfaces()

        # Leggere i lease DHCP
        dhcp_devices = parse_dhcp_leases()

        # Ottenere i dispositivi connessi
        arp_devices = get_connected_devices()

        # Ottenere statistiche di rete
        network_stats = get_network_stats()

        # Combinare le informazioni
        devices = []
        for dhcp_device in dhcp_devices:
            device_info = {
                "ip": dhcp_device["ip"],
                "mac": dhcp_device["mac"],
                "hostname": dhcp_device["hostname"],
                "interface": "unknown",
                "tx_bytes": "N/A",
                "rx_bytes": "N/A"
            }
            for arp_device in arp_devices:
                if dhcp_device["mac"] == arp_device["mac"]:
                    device_info["interface"] = arp_device["interface"]
                    break
            if device_info["interface"] in network_stats:
                device_info["tx_bytes"] = network_stats[device_info["interface"]].get("tx_bytes", "N/A")
                device_info["rx_bytes"] = network_stats[device_info["interface"]].get("rx_bytes", "N/A")
            devices.append(device_info)

        return {"connected_devices": devices}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
