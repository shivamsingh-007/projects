"""
Real WiFi Network Scanner
Detects actual networks using Windows netsh command
"""

import subprocess
import re
import random

def scan_real_networks():
    """
    Scan for real WiFi networks using Windows netsh
    Returns list of network dictionaries
    """
    try:
        # Run netsh command to get WiFi networks
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"Error running netsh: {result.stderr}")
            return []
        
        output = result.stdout
        networks = []
        current_network = {}
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # New network starts with SSID
            if line.startswith('SSID'):
                if current_network and current_network.get('ssid'):
                    networks.append(current_network)
                
                # Extract SSID (everything after "SSID X : ")
                match = re.search(r'SSID \d+ : (.+)', line)
                if match:
                    ssid = match.group(1).strip()
                    current_network = {'ssid': ssid, 'bssids': []}
            
            # Network type
            elif 'Network type' in line:
                current_network['network_type'] = line.split(':')[1].strip()
            
            # Authentication
            elif 'Authentication' in line:
                auth = line.split(':')[1].strip()
                current_network['encryption'] = auth
            
            # Signal strength
            elif 'Signal' in line and 'BSSID' not in line:
                signal_match = re.search(r'(\d+)%', line)
                if signal_match:
                    signal_percent = int(signal_match.group(1))
                    # Convert percentage to dBm (approximate)
                    signal_dbm = -100 + (signal_percent * 0.7)
                    current_network['signal_percent'] = signal_percent
                    current_network['signal'] = int(signal_dbm)
            
            # BSSID (MAC address)
            elif 'BSSID' in line:
                bssid_match = re.search(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', line)
                if bssid_match:
                    bssid = bssid_match.group(1)
                    if 'bssids' in current_network:
                        current_network['bssids'].append(bssid)
                    else:
                        current_network['bssid'] = bssid
            
            # Channel
            elif 'Channel' in line:
                channel_match = re.search(r'(\d+)', line)
                if channel_match:
                    current_network['channel'] = int(channel_match.group(1))
        
        # Add last network
        if current_network and current_network.get('ssid'):
            networks.append(current_network)
        
        # Process networks
        processed_networks = []
        for net in networks:
            if not net.get('ssid'):
                continue
            
            # Use first BSSID if multiple
            if 'bssids' in net and net['bssids']:
                net['bssid'] = net['bssids'][0]
            
            # Set defaults if missing
            if 'signal_percent' not in net:
                net['signal_percent'] = 50
                net['signal'] = -65
            
            if 'channel' not in net:
                net['channel'] = random.randint(1, 11)
            
            if 'encryption' not in net:
                net['encryption'] = 'Unknown'
            elif 'WPA3' in net['encryption']:
                net['encryption'] = 'WPA3'
            elif 'WPA2' in net['encryption']:
                net['encryption'] = 'WPA2'
            elif 'WPA' in net['encryption']:
                net['encryption'] = 'WPA'
            elif 'WEP' in net['encryption']:
                net['encryption'] = 'WEP'
            elif 'Open' in net['encryption']:
                net['encryption'] = 'OPEN'
            
            # Analyze threat level based on real factors
            threat_level = analyze_threat(net)
            net['threat_level'] = threat_level
            net['threat_name'] = ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][threat_level]
            net['is_zombie'] = threat_level >= 3
            
            processed_networks.append(net)
        
        print(f"\n✓ Found {len(processed_networks)} real networks")
        return processed_networks
        
    except Exception as e:
        print(f"Error scanning networks: {e}")
        import traceback
        traceback.print_exc()
        return []


def analyze_threat(network):
    """
    Analyze network threat level based on real security factors
    Returns 0-4 (SAFE to CRITICAL)
    """
    threat_score = 0
    
    # Factor 1: Encryption type (most important)
    encryption = network.get('encryption', '').upper()
    
    if encryption == 'OPEN' or encryption == 'NONE':
        threat_score += 3  # Open networks are high risk
    elif 'WEP' in encryption:
        threat_score += 2  # WEP is broken, high risk
    elif 'WPA' in encryption and 'WPA2' not in encryption and 'WPA3' not in encryption:
        threat_score += 1  # Old WPA is medium risk
    elif 'WPA2' in encryption:
        threat_score += 0  # WPA2 is acceptable
    elif 'WPA3' in encryption:
        threat_score -= 1  # WPA3 is most secure
    
    # Factor 2: Signal strength (very strong signals from unknown networks)
    signal_percent = network.get('signal_percent', 50)
    if signal_percent > 80:
        # Unusually strong signal might be a rogue AP
        threat_score += 1
    
    # Factor 3: Suspicious SSID patterns
    ssid = network.get('ssid', '').lower()
    suspicious_keywords = ['free', 'guest', 'public', 'open', 'wifi', 'internet']
    
    for keyword in suspicious_keywords:
        if keyword in ssid:
            threat_score += 1
            break
    
    # Factor 4: Hidden SSID
    if not ssid or ssid == '' or 'hidden' in ssid.lower():
        threat_score += 1
    
    # Factor 5: Generic/default names
    default_names = ['linksys', 'netgear', 'dlink', 'tplink', 'default']
    for name in default_names:
        if name in ssid:
            threat_score += 1
            break
    
    # Convert score to threat level (0-4)
    if threat_score <= 0:
        return 0  # SAFE
    elif threat_score == 1:
        return 1  # LOW
    elif threat_score == 2:
        return 2  # MEDIUM
    elif threat_score == 3:
        return 3  # HIGH
    else:
        return 4  # CRITICAL


def get_connected_network():
    """Get currently connected network info"""
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Extract SSID
            ssid_match = re.search(r'SSID\s+:\s+(.+)', output)
            if ssid_match:
                return ssid_match.group(1).strip()
        
        return None
    except:
        return None


if __name__ == '__main__':
    print("Testing Real WiFi Scanner...")
    print("="*70)
    
    networks = scan_real_networks()
    
    print(f"\nFound {len(networks)} networks:\n")
    
    for i, net in enumerate(networks, 1):
        print(f"{i}. {net['ssid']}")
        print(f"   Signal: {net['signal']} dBm ({net['signal_percent']}%)")
        print(f"   Encryption: {net['encryption']}")
        print(f"   Channel: {net['channel']}")
        print(f"   Threat: {net['threat_name']}")
        if net.get('bssid'):
            print(f"   BSSID: {net['bssid']}")
        print()
    
    connected = get_connected_network()
    if connected:
        print(f"Currently connected to: {connected}")
