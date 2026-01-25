# Zombie WiFi Detection System

A comprehensive machine learning-based system for detecting compromised WiFi routers (zombie WiFi) through network traffic analysis.

## 🎯 Overview

This system uses machine learning to identify compromised WiFi routers by analyzing network traffic patterns, DNS behavior, temporal anomalies, and other indicators of malicious activity.

### Key Features

- **Multiple ML Algorithms**: Random Forest, XGBoost, and Isolation Forest
- **Real-time Detection**: Continuous monitoring of network traffic
- **Comprehensive Feature Extraction**: 30+ features including:
  - DNS tunneling and DGA detection
  - Port scanning detection
  - Beaconing/periodic traffic analysis
  - Behavioral anomaly detection
- **Baseline Profiling**: Compares traffic against normal behavior
- **PCAP Analysis**: Analyze saved packet captures
- **Detailed Reporting**: Classification metrics and feature importance

## 📋 Requirements

- Python 3.8+
- Root/Administrator privileges (for packet capture)
- Linux/macOS (Windows with Npcap for packet capture)

## 🚀 Installation

### 1. Clone or Download

```bash
cd zombie_wifi_detector
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On Linux, you may need to install additional system packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libpcap-dev

# CentOS/RHEL
sudo yum install python3-devel libpcap-devel
```

### 3. Verify Installation

```bash
python main.py --help
```

## 🎮 Quick Start

### Step 1: Initial Setup

Run the setup wizard to generate training data and train the model:

```bash
python main.py setup
```

This will:
1. Generate synthetic training data (1000 normal + 200 attack samples)
2. Train a machine learning model
3. Create a baseline profile for normal behavior

### Step 2: Run Detection

**Single scan** (analyze current traffic):

```bash
sudo python main.py detect --interface eth0 --duration 60
```

**Continuous monitoring**:

```bash
sudo python main.py monitor --interface eth0 --duration 300
```

## 📚 Usage Guide

### Commands

#### Setup
```bash
python main.py setup
```
Initialize the system, generate training data, and train the model.

#### Train Model
```bash
# Train with default settings
python main.py train

# Train with specific algorithm
python main.py train --model-type xgboost

# Train with custom data
python main.py train --data-file custom_data.csv
```

#### Compare Models
```bash
python main.py compare
```
Train and compare all three model types (Random Forest, XGBoost, Isolation Forest).

#### Detect (Single Scan)
```bash
sudo python main.py detect --interface eth0 --duration 60
```
Run a single detection scan on current network traffic.

Parameters:
- `--interface` or `-i`: Network interface to monitor (default: eth0)
- `--duration` or `-d`: Capture duration in seconds (default: 60)

#### Monitor (Continuous)
```bash
sudo python main.py monitor --interface eth0 --duration 300
```
Continuously monitor network traffic with specified interval.

#### Analyze PCAP
```bash
python main.py analyze capture.pcap
```
Analyze a saved packet capture file.

### Network Interface Names

Common interface names:
- **Linux**: `eth0`, `wlan0`, `enp0s3`
- **macOS**: `en0`, `en1`
- **Windows**: `\Device\NPF_{GUID}`

Find your interface:

```bash
# Linux/macOS
ifconfig
# or
ip addr show

# Windows
ipconfig
```

## 🧠 How It Works

### 1. Data Collection
The system captures network packets using Scapy:
- IP, TCP, UDP traffic
- DNS queries and responses
- Packet timing and sizes

### 2. Feature Extraction
Extracts 30+ features across 5 categories:

**Traffic Features**:
- Connection rates
- Unique destination IPs/ports
- Packet size statistics
- Protocol distribution

**DNS Features**:
- Domain entropy (DGA detection)
- DNS tunneling indicators
- NXDOMAIN ratios
- Query type distribution

**Temporal Features**:
- Inter-arrival times
- Beaconing detection
- Nighttime activity ratios
- Traffic burst detection

**Protocol Features**:
- TCP flag distributions
- Failed connection ratios
- SYN/RST/FIN ratios

**Behavioral Features**:
- Port scanning scores
- Connection concentration
- Suspicious port usage
- IP entropy

### 3. Machine Learning Detection

Three algorithms available:

**Random Forest** (Default):
- Ensemble of decision trees
- Good balance of accuracy and speed
- Provides feature importance

**XGBoost**:
- Gradient boosting
- High accuracy
- Handles imbalanced data well

**Isolation Forest**:
- Unsupervised anomaly detection
- Doesn't require labeled attack data
- Good for novel attack detection

### 4. Alert Levels

The system classifies traffic into five alert levels:

- **NORMAL**: Clean traffic (confidence < 50%)
- **LOW**: Slight suspicion (50-65% confidence)
- **MEDIUM**: Suspicious activity (65-85% confidence)
- **HIGH**: Likely zombie WiFi (85%+ confidence)
- **CRITICAL**: Definite zombie WiFi (high confidence + baseline deviation)

## 📊 Training Data Format

Training data should be a CSV file with the following structure:

```csv
outbound_connection_rate,unique_dst_ips,dns_query_rate,...,label
50.2,30,42.1,...,0
148.7,95,215.3,...,1
```

- Features: Numeric values for each extracted feature
- Label: 0 = Normal, 1 = Zombie WiFi

### Generate Custom Training Data

You can modify `data_collection.py` to generate custom synthetic data:

```python
from data_collection import generate_synthetic_data

generate_synthetic_data(
    output_dir="data/",
    num_normal=2000,
    num_attack=500
)
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
# Capture settings
data_collection:
  capture_duration: 300
  interface: "eth0"

# Detection thresholds
thresholds:
  high_confidence: 0.85
  medium_confidence: 0.65
  anomaly_score: 2.5

# Model settings
model:
  algorithm: "random_forest"
  random_forest:
    n_estimators: 200
    max_depth: 20
```

## 📈 Model Performance

Expected performance on synthetic data:

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Random Forest | 95%+ | 93%+ | 91%+ | 92%+ |
| XGBoost | 96%+ | 94%+ | 93%+ | 93%+ |
| Isolation Forest | 88%+ | 85%+ | 80%+ | 82%+ |

**Note**: Real-world performance will vary based on:
- Quality of training data
- Network environment complexity
- Attack sophistication

## 🐛 Troubleshooting

### Permission Denied
**Problem**: `PermissionError` when capturing packets

**Solution**: Run with elevated privileges:
```bash
sudo python main.py detect
```

### No Packets Captured
**Problem**: Capture returns 0 packets

**Solutions**:
1. Check interface name: `ifconfig` or `ip addr`
2. Verify interface is up and connected
3. Try promiscuous mode (requires root)

### Model Not Found
**Problem**: `Model not found` error

**Solution**: Run setup first:
```bash
python main.py setup
```

### Import Errors
**Problem**: `ModuleNotFoundError`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
zombie_wifi_detector/
├── main.py                    # Main entry point
├── data_collection.py         # Packet capture and data generation
├── feature_extraction.py      # Feature engineering
├── model_training.py          # ML model training
├── real_time_detection.py     # Real-time detection system
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
├── data/                      # Training data directory
├── models/                    # Trained models directory
└── logs/                      # Detection logs directory
```

## 🔬 Advanced Usage

### Custom Feature Engineering

Modify `feature_extraction.py` to add custom features:

```python
def _extract_custom_features(self, packets):
    features = {}
    
    # Your custom feature logic here
    features['my_feature'] = calculate_something(packets)
    
    return features
```

### Real-world Data Collection

For production use, collect real traffic:

```python
from data_collection import PacketCapture

# Collect normal traffic
capture = PacketCapture(interface='eth0', duration=3600)
normal_packets = capture.capture_packets()
capture.save_capture('data/normal_traffic.pkl')

# Extract features and label as normal (0)
```

### Baseline Profiling

Create a baseline from your network's normal behavior:

```python
from real_time_detection import create_baseline_profile

create_baseline_profile(
    data_file='data/my_normal_traffic.csv',
    output_file='models/my_baseline.pkl'
)
```

## 🎯 Detection Indicators

The system looks for these zombie WiFi indicators:

1. **High Outbound Connection Rate**: Unusual number of outbound connections
2. **DNS Anomalies**: 
   - High-entropy domains (DGA)
   - Excessive DNS queries
   - DNS tunneling patterns
3. **Port Scanning**: Sequential port probing
4. **Beaconing**: Periodic C&C communication
5. **Nighttime Activity**: Unusual activity during 2-6 AM
6. **Failed Connections**: High ratio of RST packets
7. **Suspicious Ports**: Connections to known malicious ports

## 🛡️ Security Best Practices

If zombie WiFi is detected:

1. **Immediate Actions**:
   - Disconnect from the network
   - Change router admin password
   - Update router firmware

2. **Investigation**:
   - Check router logs
   - Scan all connected devices for malware
   - Review DHCP/DNS settings

3. **Prevention**:
   - Use strong, unique passwords
   - Enable WPA3 encryption
   - Disable WPS
   - Keep firmware updated
   - Disable remote management
   - Use network segmentation

## 📝 License

This project is provided for educational and research purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional feature engineering
- Support for more protocols
- Better visualization
- Integration with threat intelligence feeds

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always ensure you have permission to monitor network traffic. Unauthorized network monitoring may be illegal in your jurisdiction.

## 📧 Support

For issues, questions, or contributions, please refer to the project documentation.

---

**Happy Detecting! Stay safe online! 🔒**
