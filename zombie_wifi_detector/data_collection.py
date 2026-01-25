"""
Data Collection Module
Captures network traffic and stores it for analysis
"""

import time
import logging
from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR, DNSRR, ARP
from collections import defaultdict, Counter
from datetime import datetime
import pickle
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PacketCapture:
    """Captures and stores network packets for analysis"""
    
    def __init__(self, interface="eth0", duration=300):
        self.interface = interface
        self.duration = duration
        self.packets = []
        self.start_time = None
        self.end_time = None
        
    def capture_packets(self, packet_count=None, timeout=None):
        """Capture network packets"""
        logger.info(f"Starting packet capture on {self.interface}")
        self.start_time = time.time()
        
        try:
            self.packets = sniff(
                iface=self.interface,
                timeout=timeout or self.duration,
                count=packet_count,
                store=True
            )
            self.end_time = time.time()
            logger.info(f"Captured {len(self.packets)} packets in {self.end_time - self.start_time:.2f} seconds")
            return self.packets
        except Exception as e:
            logger.error(f"Error capturing packets: {e}")
            return []
    
    def save_capture(self, filename):
        """Save captured packets to file"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'packets': self.packets,
                    'start_time': self.start_time,
                    'end_time': self.end_time,
                    'interface': self.interface
                }, f)
            logger.info(f"Saved capture to {filename}")
        except Exception as e:
            logger.error(f"Error saving capture: {e}")
    
    def load_capture(self, filename):
        """Load packets from file"""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.packets = data['packets']
                self.start_time = data['start_time']
                self.end_time = data['end_time']
                self.interface = data.get('interface', 'unknown')
            logger.info(f"Loaded {len(self.packets)} packets from {filename}")
            return self.packets
        except Exception as e:
            logger.error(f"Error loading capture: {e}")
            return []


class TrafficAnalyzer:
    """Analyzes captured traffic for basic statistics"""
    
    def __init__(self, packets):
        self.packets = packets
        self.stats = {}
        
    def analyze(self):
        """Perform basic traffic analysis"""
        self.stats = {
            'total_packets': len(self.packets),
            'ip_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'dns_packets': 0,
            'arp_packets': 0,
            'unique_src_ips': set(),
            'unique_dst_ips': set(),
            'src_ports': Counter(),
            'dst_ports': Counter(),
            'protocols': Counter(),
            'packet_sizes': [],
            'timestamps': []
        }
        
        for pkt in self.packets:
            # Timestamp
            if hasattr(pkt, 'time'):
                self.stats['timestamps'].append(float(pkt.time))
            
            # IP layer
            if IP in pkt:
                self.stats['ip_packets'] += 1
                self.stats['unique_src_ips'].add(pkt[IP].src)
                self.stats['unique_dst_ips'].add(pkt[IP].dst)
                self.stats['packet_sizes'].append(len(pkt))
                
                # TCP
                if TCP in pkt:
                    self.stats['tcp_packets'] += 1
                    self.stats['src_ports'][pkt[TCP].sport] += 1
                    self.stats['dst_ports'][pkt[TCP].dport] += 1
                    self.stats['protocols']['TCP'] += 1
                
                # UDP
                elif UDP in pkt:
                    self.stats['udp_packets'] += 1
                    self.stats['src_ports'][pkt[UDP].sport] += 1
                    self.stats['dst_ports'][pkt[UDP].dport] += 1
                    self.stats['protocols']['UDP'] += 1
                    
                    # DNS
                    if DNS in pkt:
                        self.stats['dns_packets'] += 1
            
            # ARP
            elif ARP in pkt:
                self.stats['arp_packets'] += 1
                self.stats['protocols']['ARP'] += 1
        
        # Convert sets to counts
        self.stats['unique_src_ips'] = len(self.stats['unique_src_ips'])
        self.stats['unique_dst_ips'] = len(self.stats['unique_dst_ips'])
        
        return self.stats
    
    def print_summary(self):
        """Print traffic summary"""
        if not self.stats:
            self.analyze()
        
        print("\n=== Traffic Summary ===")
        print(f"Total Packets: {self.stats['total_packets']}")
        print(f"IP Packets: {self.stats['ip_packets']}")
        print(f"TCP Packets: {self.stats['tcp_packets']}")
        print(f"UDP Packets: {self.stats['udp_packets']}")
        print(f"DNS Packets: {self.stats['dns_packets']}")
        print(f"ARP Packets: {self.stats['arp_packets']}")
        print(f"Unique Source IPs: {self.stats['unique_src_ips']}")
        print(f"Unique Destination IPs: {self.stats['unique_dst_ips']}")
        
        if self.stats['dst_ports']:
            print("\nTop 10 Destination Ports:")
            for port, count in self.stats['dst_ports'].most_common(10):
                print(f"  Port {port}: {count} packets")


class DNSAnalyzer:
    """Specialized analyzer for DNS traffic"""
    
    def __init__(self, packets):
        self.packets = [pkt for pkt in packets if DNS in pkt]
        self.queries = []
        self.responses = []
        
    def extract_dns_data(self):
        """Extract DNS queries and responses"""
        for pkt in self.packets:
            if DNSQR in pkt:
                # DNS Query
                query_data = {
                    'timestamp': float(pkt.time) if hasattr(pkt, 'time') else 0,
                    'src_ip': pkt[IP].src if IP in pkt else None,
                    'dst_ip': pkt[IP].dst if IP in pkt else None,
                    'qname': pkt[DNSQR].qname.decode() if pkt[DNSQR].qname else '',
                    'qtype': pkt[DNSQR].qtype,
                    'query_length': len(pkt[DNSQR].qname) if pkt[DNSQR].qname else 0
                }
                self.queries.append(query_data)
            
            if DNSRR in pkt:
                # DNS Response
                response_data = {
                    'timestamp': float(pkt.time) if hasattr(pkt, 'time') else 0,
                    'src_ip': pkt[IP].src if IP in pkt else None,
                    'rdata': pkt[DNSRR].rdata if hasattr(pkt[DNSRR], 'rdata') else None,
                    'rrname': pkt[DNSRR].rrname.decode() if pkt[DNSRR].rrname else ''
                }
                self.responses.append(response_data)
        
        return self.queries, self.responses
    
    def get_dns_summary(self):
        """Get summary of DNS traffic"""
        if not self.queries:
            self.extract_dns_data()
        
        return {
            'total_queries': len(self.queries),
            'total_responses': len(self.responses),
            'unique_domains': len(set(q['qname'] for q in self.queries)),
            'query_types': Counter(q['qtype'] for q in self.queries),
            'queried_domains': [q['qname'] for q in self.queries]
        }


def generate_synthetic_data(output_dir="data/", num_normal=1000, num_attack=200):
    """Generate synthetic training data for testing"""
    import numpy as np
    import pandas as pd
    
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("Generating synthetic training data...")
    
    # Normal traffic patterns
    normal_data = {
        'outbound_connection_rate': np.random.normal(50, 15, num_normal),
        'unique_dst_ips': np.random.poisson(30, num_normal),
        'dns_query_rate': np.random.normal(40, 10, num_normal),
        'failed_connection_ratio': np.random.beta(2, 50, num_normal),
        'nighttime_activity_ratio': np.random.beta(2, 10, num_normal),
        'port_scan_score': np.random.exponential(0.1, num_normal),
        'nxdomain_ratio': np.random.beta(1, 50, num_normal),
        'dga_domain_score': np.random.normal(2.5, 0.5, num_normal),
        'http_injection_indicators': np.random.poisson(0.5, num_normal),
        'cpu_usage_variance': np.random.normal(10, 3, num_normal),
        'label': [0] * num_normal
    }
    
    # Attack traffic patterns (zombie WiFi)
    attack_data = {
        'outbound_connection_rate': np.random.normal(150, 40, num_attack),
        'unique_dst_ips': np.random.poisson(100, num_attack),
        'dns_query_rate': np.random.normal(200, 50, num_attack),
        'failed_connection_ratio': np.random.beta(5, 10, num_attack),
        'nighttime_activity_ratio': np.random.beta(8, 3, num_attack),
        'port_scan_score': np.random.exponential(2.5, num_attack),
        'nxdomain_ratio': np.random.beta(10, 20, num_attack),
        'dga_domain_score': np.random.normal(4.5, 0.8, num_attack),
        'http_injection_indicators': np.random.poisson(5, num_attack),
        'cpu_usage_variance': np.random.normal(40, 10, num_attack),
        'label': [1] * num_attack
    }
    
    # Combine and shuffle
    df_normal = pd.DataFrame(normal_data)
    df_attack = pd.DataFrame(attack_data)
    df_combined = pd.concat([df_normal, df_attack], ignore_index=True)
    df_combined = df_combined.sample(frac=1).reset_index(drop=True)
    
    # Save to CSV
    train_file = os.path.join(output_dir, "training_data.csv")
    df_combined.to_csv(train_file, index=False)
    logger.info(f"Generated {len(df_combined)} samples saved to {train_file}")
    
    return train_file


if __name__ == "__main__":
    # Example usage
    print("=== Zombie WiFi Detection - Data Collection Module ===\n")
    
    # Generate synthetic data for testing
    print("Generating synthetic training data...")
    data_file = generate_synthetic_data()
    print(f"Training data saved to: {data_file}\n")
    
    # Note: Live packet capture requires root/admin privileges
    print("Note: Live packet capture requires root/admin privileges")
    print("For testing, you can use the synthetic data generated above")
