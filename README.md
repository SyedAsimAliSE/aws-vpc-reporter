# VPC Reporter 🚀

**Comprehensive AWS VPC network documentation tool with beautiful CLI output**

Generate detailed reports of your AWS VPC network infrastructure with **19 comprehensive sections** covering every aspect of your VPC configuration - from basic networking to advanced hybrid connectivity.

## ✨ Features

- 🎯 **Complete Coverage** - All 19 VPC sections with 350+ fields captured
- 🎨 **Beautiful Output** - Rich terminal UI with color-coded status indicators
- 📝 **Multiple Formats** - Console (Rich), Markdown, JSON, or YAML
- ⚡ **Blazing Fast** - Async mode (16.7x faster) with smart caching
- 💰 **Cost Analysis** - Monthly cost estimates with optimization recommendations
- 📊 **Network Diagrams** - Generate Python diagram code for visualization
- ⚙️ **Configuration** - YAML config file support for defaults
- 🔒 **Read-Only** - Safe to run in production (no mutations)
- 🏗️ **Type-Safe** - Built with Pydantic and strict mypy
- 🧪 **Battle-Tested** - 95 tests with 83% coverage

## 📦 Installation

```bash
# Clone and install with UV
cd vpc-reporter
uv sync
uv sync --extra dev

# Run directly
uv run awsvpc --help
```

## 🚀 Quick Start

### Basic Usage

```bash
# List all VPCs in a region
uv run awsvpc --region us-east-1 list-vpcs

# Generate full report (all 19 sections)
uv run awsvpc --region us-east-1 report --vpc-id vpc-0abc123

# Use async mode for 16.7x faster collection
uv run awsvpc --region us-east-1 report --vpc-id vpc-0abc123 --async

# Output to markdown file
uv run awsvpc report --vpc-id vpc-123 --format markdown -o vpc-report.md

# Analyze VPC costs
uv run awsvpc --region us-east-1 cost --vpc-id vpc-123

# Generate network diagram code
uv run awsvpc --region us-east-1 diagram --vpc-id vpc-123 --output diagram.py
```

### Configuration Management

```bash
# Create default configuration file
uv run awsvpc config --init

# View current configuration
uv run awsvpc config --show

# Use custom configuration file
uv run awsvpc --config /path/to/config.yaml config --show
```

## 📋 Complete Section Coverage (19/19 - 100%)

### Core VPC Components
✅ **VPC Overview** - CIDR blocks, IPv6, tenancy, DNS settings  
✅ **VPC Attributes** - DNS support, DNS hostnames, network metrics  
✅ **Subnets** - AZs, CIDR blocks, IPv6, auto-assign IPs, Outpost support  
✅ **Route Tables** - Routes (10 target types), associations, propagation  

### Security & Access Control
✅ **Security Groups** - Inbound/outbound rules with ports, protocols, sources  
✅ **Network ACLs** - Inbound/outbound rules with rule numbers, allow/deny  

### Internet & NAT
✅ **Internet Gateways** - IGW attachments and state  
✅ **NAT Gateways** - Public IPs, subnet placement, connectivity type  
✅ **Elastic IPs** - Allocations, associations, network border groups  

### VPC Connectivity
✅ **VPC Endpoints** - Gateway/Interface endpoints, service connections  
✅ **VPC Peering** - Peering connections, requester/accepter info, status  
✅ **Transit Gateway Attachments** - TGW connections, DNS/IPv6 support  

### Hybrid Connectivity (⭐ Advanced)
✅ **VPN Connections** - ⭐ Tunnel status (UP/DOWN), telemetry, IPSec config  
✅ **Customer Gateways** - CGW details, BGP ASN, IP addresses  
✅ **VPN Gateways** - VGW attachments, Amazon-side ASN  
✅ **Direct Connect VIFs** - ⭐ BGP session status, virtual interface types  

### Network Management
✅ **DHCP Options** - Domain name, DNS servers, NTP servers  
✅ **VPC Flow Logs** - Traffic logging, destinations, status  
✅ **Network Interfaces** - ⭐ ENI types (20+ types), attachments, IPs  

## 🎮 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list-vpcs` | List all VPCs in region | `awsvpc list-vpcs --region us-east-1` |
| `report` | Generate VPC report | `awsvpc report --vpc-id vpc-123` |
| `cost` | Analyze VPC costs | `awsvpc cost --vpc-id vpc-123` |
| `diagram` | Generate diagram code | `awsvpc diagram --vpc-id vpc-123` |
| `config` | Manage configuration | `awsvpc config --init` |

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov --cov-report=term

# Run only unit tests
uv run pytest tests/unit/ -v
```

## 📖 Documentation

For comprehensive documentation and examples, see **[README-detailed.md](README-detailed.md)** which contains:
- Complete usage examples and workflows
- Detailed information about all 19 VPC sections
- Output format examples (Console, Markdown, JSON, YAML)
- Testing guides and project architecture

## 🏗️ Technology Stack

- **CLI Framework**: Click 8.1+
- **Terminal UI**: Rich 13.7+ (tables, colors, progress)
- **AWS SDK**: boto3 1.34+ (EC2 + DirectConnect)
- **Data Validation**: Pydantic 2.5+
- **Logging**: loguru 0.7+
- **Testing**: pytest 7.4+ with moto mocking
- **Type Checking**: mypy (strict mode)
- **Package Manager**: UV

## 📊 Statistics

| Metric | Count | Status |
|--------|-------|--------|
| **VPC Sections** | 19 | ✅ Complete |
| **Fields Captured** | 350+ | ✅ Complete |
| **Operations Files** | 19 | ✅ Complete |
| **Integration Tests** | 8 | ✅ Passing |
| **Test Success Rate** | 100% | ✅ Verified |

## 🔒 Security

VPC Reporter is designed with security in mind:

- **Read-Only Operations**: The tool only performs read-only AWS API calls
- **No Data Storage**: No AWS data is stored or transmitted externally
- **Local Processing**: All data processing happens locally on your machine
- **Credential Safety**: Uses standard AWS credential management

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🔗 Links

- **GitHub Repository**: https://github.com/SyedAsimAliSE/aws-vpc-reporter
- **Issues**: https://github.com/SyedAsimAliSE/aws-vpc-reporter/issues
- **Detailed Documentation**: [README-detailed.md](README-detailed.md)

---

**VPC Reporter** - Your comprehensive VPC documentation solution! 🚀
