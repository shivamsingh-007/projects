from scapy.all import sniff, IP
import pandas as pd
import os

# Your Wi-Fi interface
iface = r" \\Device\\NPF_{EE7698FF-D1CA-4422-B7F3-91904DA59428}"

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

# Capture 200 packets
packets = sniff(iface=iface, count=200)

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
df.to_csv("data/my_normal_traffic.csv", index=False)

print("Normal traffic CSV saved at data/my_normal_traffic.csv")
# Save to CSV