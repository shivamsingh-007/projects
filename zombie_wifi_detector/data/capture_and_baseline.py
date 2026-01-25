from scapy.all import get_if_list, get_if_addr, sniff, IP
import pandas as pd
import os

# Step 1: auto-detect active interface
iface = None
for i in get_if_list():
    try:
        ip = get_if_addr(i)
        # skip loopback or disconnected adapters
        if ip not in ("0.0.0.0", "127.0.0.1"):
            iface = i
            break
    except:
        continue

if not iface:
    raise Exception("No active network interface found!")

print(f"Using interface: {iface} with IP {get_if_addr(iface)}")

# Step 2: make sure 'data/' folder exists
os.makedirs("data", exist_ok=True)

# Step 3: capture normal traffic
print("Capturing 200 packets...")
packets = sniff(iface=iface, count=200)
print("Capture complete!")

# Step 4: convert to DataFrame
data = []
for pkt in packets:
    if IP in pkt:
        data.append({
            "src": pkt[IP].src,
            "dst": pkt[IP].dst,
            "len": len(pkt),
            "proto": pkt[IP].proto
        })

df = pd.DataFrame(data)

# Step 5: save CSV
csv_path = "data/my_normal_traffic.csv"
df.to_csv(csv_path, index=False)
print(f"Normal traffic CSV saved at {csv_path}")

# Step 6: create models folder if missing
os.makedirs("models", exist_ok=True)

# Step 7: run baseline creation
from real_time_detection import create_baseline_profile
create_baseline_profile(csv_path, "models/my_baseline.pkl")
print("Baseline profile created at models/my_baseline.pkl")
