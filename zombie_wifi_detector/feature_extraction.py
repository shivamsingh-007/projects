"""
Feature Extraction Module
Extracts features from network traffic for ML model
"""

import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy
from scapy.all import IP, TCP, UDP, DNS, DNSQR
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from network packets for ML classification"""
    
    def __init__(self):
        self.features = {}
        
    def extract_all_features(self, packets, time_window=300):
        """Extract all features from packet list"""
        
        logger.info(f"Extracting features from {len(packets)} packets...")
        
        # Initialize feature dictionary
        features = {}
        
        # Basic traffic features
        traffic_features = self._extract_traffic_features(packets, time_window)
        features.update(traffic_features)
        
        # DNS features
        dns_features = self._extract_dns_features(packets)
        features.update(dns_features)
        
        # Temporal features
        temporal_features = self._extract_temporal_features(packets)
        features.update(temporal_features)
        
        # Protocol features
        protocol_features = self._extract_protocol_features(packets)
        features.update(protocol_features)
        
        # Behavioral features
        behavioral_features = self._extract_behavioral_features(packets, time_window)
        features.update(behavioral_features)
        
        self.features = features
        logger.info(f"Extracted {len(features)} features")
        
        return features
    
    def _extract_traffic_features(self, packets, time_window):
        """Extract basic traffic volume and connection features"""
        features = {}
        
        if not packets:
            return self._get_default_traffic_features()
        
        # Count packets by type
        ip_packets = [p for p in packets if IP in p]
        tcp_packets = [p for p in packets if TCP in p]
        udp_packets = [p for p in packets if UDP in p]
        
        # Connection tracking
        src_ips = set()
        dst_ips = set()
        src_ports = []
        dst_ports = []
        
        for pkt in ip_packets:
            if IP in pkt:
                src_ips.add(pkt[IP].src)
                dst_ips.add(pkt[IP].dst)
            
            if TCP in pkt:
                src_ports.append(pkt[TCP].sport)
                dst_ports.append(pkt[TCP].dport)
            elif UDP in pkt:
                src_ports.append(pkt[UDP].sport)
                dst_ports.append(pkt[UDP].dport)
        
        # Calculate rates (per second)
        duration = time_window if time_window > 0 else 1
        
        features['outbound_connection_rate'] = len(ip_packets) / duration
        features['unique_dst_ips'] = len(dst_ips)
        features['unique_src_ips'] = len(src_ips)
        features['unique_dst_ports'] = len(set(dst_ports)) if dst_ports else 0
        features['unique_src_ports'] = len(set(src_ports)) if src_ports else 0
        
        # Packet size statistics
        packet_sizes = [len(p) for p in packets]
        if packet_sizes:
            features['avg_packet_size'] = np.mean(packet_sizes)
            features['std_packet_size'] = np.std(packet_sizes)
            features['max_packet_size'] = np.max(packet_sizes)
            features['min_packet_size'] = np.min(packet_sizes)
        else:
            features['avg_packet_size'] = 0
            features['std_packet_size'] = 0
            features['max_packet_size'] = 0
            features['min_packet_size'] = 0
        
        # Protocol distribution
        total = len(packets) if len(packets) > 0 else 1
        features['tcp_ratio'] = len(tcp_packets) / total
        features['udp_ratio'] = len(udp_packets) / total
        
        # Port scan detection
        features['port_scan_score'] = self._calculate_port_scan_score(dst_ips, dst_ports)
        
        return features
    
    def _extract_dns_features(self, packets):
        """Extract DNS-specific features"""
        features = {}
        
        dns_packets = [p for p in packets if DNS in p and DNSQR in p]
        
        if not dns_packets:
            return self._get_default_dns_features()
        
        # Extract domain names
        domains = []
        query_types = []
        query_lengths = []
        
        for pkt in dns_packets:
            if DNSQR in pkt:
                qname = pkt[DNSQR].qname
                if qname:
                    domain = qname.decode() if isinstance(qname, bytes) else str(qname)
                    domains.append(domain)
                    query_lengths.append(len(domain))
                    query_types.append(pkt[DNSQR].qtype)
        
        # DNS query rate
        features['dns_query_rate'] = len(dns_packets)
        
        # Domain entropy (DGA detection)
        if domains:
            features['dga_domain_score'] = np.mean([self._calculate_domain_entropy(d) for d in domains])
            features['avg_domain_length'] = np.mean(query_lengths)
            features['max_domain_length'] = np.max(query_lengths)
        else:
            features['dga_domain_score'] = 0
            features['avg_domain_length'] = 0
            features['max_domain_length'] = 0
        
        # Query type distribution (DNS tunneling indicator)
        query_type_counts = Counter(query_types)
        total_queries = len(query_types) if query_types else 1
        features['txt_record_ratio'] = query_type_counts.get(16, 0) / total_queries  # TXT records
        features['null_record_ratio'] = query_type_counts.get(10, 0) / total_queries  # NULL records
        
        # NXDOMAIN ratio (failed DNS queries)
        features['nxdomain_ratio'] = self._calculate_nxdomain_ratio(dns_packets)
        
        # DNS tunneling score
        features['dns_tunneling_score'] = self._calculate_dns_tunneling_score(domains, query_lengths)
        
        return features
    
    def _extract_temporal_features(self, packets):
        """Extract time-based features"""
        features = {}
        
        if not packets or not hasattr(packets[0], 'time'):
            return self._get_default_temporal_features()
        
        timestamps = [float(p.time) for p in packets if hasattr(p, 'time')]
        
        if len(timestamps) < 2:
            return self._get_default_temporal_features()
        
        # Inter-arrival times
        inter_arrival_times = np.diff(timestamps)
        
        if len(inter_arrival_times) > 0:
            features['avg_inter_arrival_time'] = np.mean(inter_arrival_times)
            features['std_inter_arrival_time'] = np.std(inter_arrival_times)
            
            # Periodicity detection (beaconing)
            features['beaconing_score'] = self._detect_periodicity(inter_arrival_times)
        else:
            features['avg_inter_arrival_time'] = 0
            features['std_inter_arrival_time'] = 0
            features['beaconing_score'] = 0
        
        # Time of day distribution (nighttime activity indicator)
        features['nighttime_activity_ratio'] = self._calculate_nighttime_ratio(timestamps)
        
        # Burst detection
        features['burst_score'] = self._detect_traffic_bursts(timestamps)
        
        return features
    
    def _extract_protocol_features(self, packets):
        """Extract protocol-specific features"""
        features = {}
        
        # TCP flags distribution
        tcp_packets = [p for p in packets if TCP in p]
        
        if tcp_packets:
            flags_counter = Counter()
            for pkt in tcp_packets:
                flags = pkt[TCP].flags
                flags_counter[str(flags)] += 1
            
            total_tcp = len(tcp_packets)
            features['syn_ratio'] = sum(1 for p in tcp_packets if p[TCP].flags & 0x02) / total_tcp
            features['rst_ratio'] = sum(1 for p in tcp_packets if p[TCP].flags & 0x04) / total_tcp
            features['fin_ratio'] = sum(1 for p in tcp_packets if p[TCP].flags & 0x01) / total_tcp
        else:
            features['syn_ratio'] = 0
            features['rst_ratio'] = 0
            features['fin_ratio'] = 0
        
        # Failed connection ratio
        features['failed_connection_ratio'] = self._calculate_failed_connection_ratio(tcp_packets)
        
        return features
    
    def _extract_behavioral_features(self, packets, time_window):
        """Extract behavioral anomaly indicators"""
        features = {}
        
        ip_packets = [p for p in packets if IP in p]
        
        if not ip_packets:
            return self._get_default_behavioral_features()
        
        # Destination IP diversity (scanning behavior)
        dst_ips = [p[IP].dst for p in ip_packets]
        features['dst_ip_entropy'] = self._calculate_entropy(dst_ips)
        
        # Connection attempts distribution
        connection_distribution = Counter(dst_ips)
        if connection_distribution:
            features['max_connections_single_ip'] = connection_distribution.most_common(1)[0][1]
            features['connection_concentration'] = features['max_connections_single_ip'] / len(dst_ips)
        else:
            features['max_connections_single_ip'] = 0
            features['connection_concentration'] = 0
        
        # Vertical scan score (many ports, same IP)
        features['vertical_scan_score'] = self._calculate_vertical_scan_score(ip_packets)
        
        # Horizontal scan score (same port, many IPs)
        features['horizontal_scan_score'] = self._calculate_horizontal_scan_score(ip_packets)
        
        # Suspicious port usage
        features['suspicious_port_count'] = self._count_suspicious_ports(packets)
        
        return features
    
    # Helper methods for feature calculations
    
    def _calculate_domain_entropy(self, domain):
        """Calculate entropy of domain name (DGA detection)"""
        if not domain or len(domain) == 0:
            return 0
        
        # Remove dots for entropy calculation
        domain = domain.replace('.', '')
        
        # Calculate character frequency
        char_freq = Counter(domain)
        length = len(domain)
        
        # Calculate Shannon entropy
        ent = 0
        for count in char_freq.values():
            prob = count / length
            ent -= prob * math.log2(prob)
        
        return ent
    
    def _calculate_nxdomain_ratio(self, dns_packets):
        """Calculate ratio of failed DNS queries"""
        # This would require parsing DNS response codes
        # Simplified version
        return 0.0
    
    def _calculate_dns_tunneling_score(self, domains, query_lengths):
        """Detect DNS tunneling based on query characteristics"""
        if not domains:
            return 0
        
        # Long subdomain labels are suspicious
        avg_length = np.mean(query_lengths) if query_lengths else 0
        
        # High entropy domains
        avg_entropy = np.mean([self._calculate_domain_entropy(d) for d in domains])
        
        # Combine indicators
        tunneling_score = (avg_length / 100) + (avg_entropy / 5)
        
        return min(tunneling_score, 10)  # Cap at 10
    
    def _detect_periodicity(self, inter_arrival_times):
        """Detect periodic beaconing in traffic"""
        if len(inter_arrival_times) < 10:
            return 0
        
        # Calculate coefficient of variation
        mean_iat = np.mean(inter_arrival_times)
        std_iat = np.std(inter_arrival_times)
        
        if mean_iat == 0:
            return 0
        
        cv = std_iat / mean_iat
        
        # Low CV indicates periodicity (beaconing)
        beaconing_score = max(0, 1 - cv)
        
        return beaconing_score
    
    def _calculate_nighttime_ratio(self, timestamps):
        """Calculate ratio of traffic during nighttime hours (2 AM - 6 AM)"""
        from datetime import datetime
        
        nighttime_count = 0
        for ts in timestamps:
            dt = datetime.fromtimestamp(ts)
            if 2 <= dt.hour < 6:
                nighttime_count += 1
        
        return nighttime_count / len(timestamps) if timestamps else 0
    
    def _detect_traffic_bursts(self, timestamps):
        """Detect sudden bursts in traffic"""
        if len(timestamps) < 10:
            return 0
        
        # Calculate packets per second in sliding windows
        window_size = 5  # seconds
        burst_threshold = 50  # packets per second
        
        burst_score = 0
        # Simplified burst detection
        inter_arrival = np.diff(timestamps)
        if len(inter_arrival) > 0:
            min_iat = np.min(inter_arrival)
            if min_iat > 0:
                max_rate = 1 / min_iat
                if max_rate > burst_threshold:
                    burst_score = min(max_rate / burst_threshold, 5)
        
        return burst_score
    
    def _calculate_failed_connection_ratio(self, tcp_packets):
        """Calculate ratio of failed TCP connections (RST packets)"""
        if not tcp_packets:
            return 0
        
        rst_count = sum(1 for p in tcp_packets if p[TCP].flags & 0x04)
        return rst_count / len(tcp_packets)
    
    def _calculate_entropy(self, items):
        """Calculate Shannon entropy of a list"""
        if not items:
            return 0
        
        counts = Counter(items)
        total = len(items)
        
        ent = 0
        for count in counts.values():
            prob = count / total
            ent -= prob * math.log2(prob)
        
        return ent
    
    def _calculate_vertical_scan_score(self, ip_packets):
        """Detect vertical scanning (many ports on same IP)"""
        if not ip_packets:
            return 0
        
        # Group by destination IP, count unique ports
        ip_port_map = defaultdict(set)
        
        for pkt in ip_packets:
            dst_ip = pkt[IP].dst
            if TCP in pkt:
                ip_port_map[dst_ip].add(pkt[TCP].dport)
            elif UDP in pkt:
                ip_port_map[dst_ip].add(pkt[UDP].dport)
        
        # Find max ports contacted on single IP
        max_ports = max(len(ports) for ports in ip_port_map.values()) if ip_port_map else 0
        
        # Normalize score
        return min(max_ports / 20, 5)  # Cap at 5
    
    def _calculate_horizontal_scan_score(self, ip_packets):
        """Detect horizontal scanning (same port on many IPs)"""
        if not ip_packets:
            return 0
        
        # Group by port, count unique IPs
        port_ip_map = defaultdict(set)
        
        for pkt in ip_packets:
            dst_ip = pkt[IP].dst
            if TCP in pkt:
                port_ip_map[pkt[TCP].dport].add(dst_ip)
            elif UDP in pkt:
                port_ip_map[pkt[UDP].dport].add(dst_ip)
        
        # Find max IPs contacted on single port
        max_ips = max(len(ips) for ips in port_ip_map.values()) if port_ip_map else 0
        
        # Normalize score
        return min(max_ips / 50, 5)  # Cap at 5
    
    def _count_suspicious_ports(self, packets):
        """Count connections to commonly exploited ports"""
        suspicious_ports = {
            22, 23, 445, 3389, 5900,  # Remote access
            1433, 3306, 5432,  # Databases
            6667, 6668, 6669,  # IRC (C&C)
            4444, 5555, 8080, 8888  # Common backdoor ports
        }
        
        count = 0
        for pkt in packets:
            if TCP in pkt and pkt[TCP].dport in suspicious_ports:
                count += 1
            elif UDP in pkt and pkt[UDP].dport in suspicious_ports:
                count += 1
        
        return count
    
    def _calculate_port_scan_score(self, dst_ips, dst_ports):
        """Calculate port scanning score"""
        if not dst_ports:
            return 0
        
        unique_ips = len(set(dst_ips)) if dst_ips else 1
        unique_ports = len(set(dst_ports))
        
        # High ratio of ports to IPs suggests scanning
        if unique_ips > 0:
            ratio = unique_ports / unique_ips
            return min(ratio / 10, 5)  # Normalize and cap
        
        return 0
    
    # Default feature values for edge cases
    
    def _get_default_traffic_features(self):
        return {
            'outbound_connection_rate': 0,
            'unique_dst_ips': 0,
            'unique_src_ips': 0,
            'unique_dst_ports': 0,
            'unique_src_ports': 0,
            'avg_packet_size': 0,
            'std_packet_size': 0,
            'max_packet_size': 0,
            'min_packet_size': 0,
            'tcp_ratio': 0,
            'udp_ratio': 0,
            'port_scan_score': 0
        }
    
    def _get_default_dns_features(self):
        return {
            'dns_query_rate': 0,
            'dga_domain_score': 0,
            'avg_domain_length': 0,
            'max_domain_length': 0,
            'txt_record_ratio': 0,
            'null_record_ratio': 0,
            'nxdomain_ratio': 0,
            'dns_tunneling_score': 0
        }
    
    def _get_default_temporal_features(self):
        return {
            'avg_inter_arrival_time': 0,
            'std_inter_arrival_time': 0,
            'beaconing_score': 0,
            'nighttime_activity_ratio': 0,
            'burst_score': 0
        }
    
    def _get_default_behavioral_features(self):
        return {
            'dst_ip_entropy': 0,
            'max_connections_single_ip': 0,
            'connection_concentration': 0,
            'vertical_scan_score': 0,
            'horizontal_scan_score': 0,
            'suspicious_port_count': 0
        }
    
    def get_feature_vector(self):
        """Return feature vector as array"""
        return np.array(list(self.features.values()))
    
    def get_feature_names(self):
        """Return list of feature names"""
        return list(self.features.keys())


if __name__ == "__main__":
    print("=== Feature Extraction Module ===")
    print("This module extracts features from network traffic")
    print("Feature categories:")
    print("  - Traffic volume and connection features")
    print("  - DNS-specific features (DGA detection, tunneling)")
    print("  - Temporal patterns (periodicity, bursts)")
    print("  - Protocol-specific features")
    print("  - Behavioral anomaly indicators")
