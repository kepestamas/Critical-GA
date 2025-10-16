# Installation and Setup Guide

## System Requirements

### Operating System Support
- **Windows**: Windows 10/11 (tested with PowerShell)
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 1 GB free space
- **Network**: Internet connection for installation

#### Recommended Requirements
- **CPU**: 4+ cores, 2.5+ GHz (for multiprocessing)
- **RAM**: 8+ GB (for large networks)
- **Storage**: 5+ GB free space (for outputs)
- **GPU**: Optional (for future GPU acceleration)

### Software Prerequisites

#### Python Environment
```bash
Python 3.6+ (tested with Python 3.7, 3.8, 3.9)
pip (Python package installer)
```

#### Optional Tools
- **Git**: For cloning repository
- **Jupyter**: For interactive analysis
- **VS Code**: Recommended IDE

## Installation Methods

### Method 1: Quick Installation (Recommended)

#### Step 1: Clone Repository
```bash
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
```

#### Step 2: Install Dependencies
```bash
pip install networkx numpy matplotlib pyvis
```

#### Step 3: Verify Installation
```bash
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```

### Method 2: Virtual Environment Installation

#### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv critical_ga_env
critical_ga_env\Scripts\activate

# macOS/Linux
python3 -m venv critical_ga_env
source critical_ga_env/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install networkx numpy matplotlib pyvis
```

#### Step 3: Clone and Test
```bash
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```

### Method 3: Conda Installation

#### Step 1: Create Conda Environment
```bash
conda create -n critical_ga python=3.8
conda activate critical_ga
```

#### Step 2: Install Dependencies
```bash
conda install networkx numpy matplotlib
pip install pyvis  # Not available in conda
```

#### Step 3: Clone and Test
```bash
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```

## Dependency Details

### Core Dependencies

#### NetworkX
```bash
pip install networkx>=2.0
```
**Purpose**: Graph algorithms and data structures
**Features Used**: Graph creation, connectivity analysis, component detection

#### NumPy
```bash
pip install numpy>=1.15
```
**Purpose**: Numerical computations and matrix operations
**Features Used**: Eigenvalue computation, array operations

#### Python Standard Library
**Modules Used**:
- `random`: Random number generation
- `copy`: Deep copying of objects
- `sys`: System parameters and command-line arguments
- `time`: Timing measurements
- `math`: Mathematical functions
- `multiprocessing`: Parallel processing
- `subprocess`: Process management

### Optional Dependencies

#### Matplotlib
```bash
pip install matplotlib>=3.0
```
**Purpose**: Static plotting and visualization
**Usage**: Currently commented out, available for future visualization features

#### PyVis
```bash
pip install pyvis>=0.1.8
```
**Purpose**: Interactive network visualization
**Usage**: Used by `network_painter.py` for HTML output

### Development Dependencies

#### Testing Framework
```bash
pip install pytest  # For future testing
```

#### Code Quality
```bash
pip install black flake8  # For code formatting and linting
```

#### Documentation
```bash
pip install sphinx  # For generating documentation
```

## Configuration

### Environment Variables

#### Optional Settings
```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;C:\path\to\Critical-GA

# macOS/Linux
export PYTHONPATH=$PYTHONPATH:/path/to/Critical-GA
```

### Directory Structure Setup

#### Default Directory Layout
```
Critical-GA/
├── inputs/          # Input network files
├── outputs/         # Generated output files
│   ├── ga/         # Genetic algorithm results
│   ├── greedy/     # Greedy algorithm results
│   └── networks/   # Network analysis results
├── docs/           # Documentation files
└── *.py           # Python scripts
```

#### Creating Output Directories
```bash
mkdir -p outputs/ga
mkdir -p outputs/greedy  
mkdir -p outputs/networks
mkdir -p outputs/timing
mkdir -p outputs/descending_mutation/ga
mkdir -p outputs/reruns/greedy
mkdir -p outputs/reruns/networks
```

## Verification and Testing

### Basic Functionality Test

#### Test 1: Genetic Algorithm
```bash
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```
**Expected**: Output file created in `outputs/descending_mutation/ga/`

#### Test 2: Greedy Algorithm
```bash
python connectivity_greedy.py karate.txt 1
```
**Expected**: Output file created in `outputs/reruns/greedy/`

#### Test 3: Network Analysis
```bash
python network_analyzer.py karate.txt
```
**Expected**: Network statistics displayed and output file created

#### Test 4: Visualization
```bash
python network_painter.py karate.txt
```
**Expected**: `nx3.html` file created with interactive visualization

### Performance Test

#### Small Network Test
```bash
python connectivity_ga.py karate.txt test 0.1 0.05 20 3 0.8 0.05
```
**Expected Runtime**: < 30 seconds

#### Medium Network Test
```bash
python connectivity_ga.py BarabasiAlbert_n500m1.txt test 0.05 0.03 50 3 0.8 0.05
```
**Expected Runtime**: 2-5 minutes

### Troubleshooting Installation

#### Common Issues and Solutions

##### ImportError: No module named 'networkx'
```bash
# Solution
pip install networkx
# or
conda install networkx
```

##### Permission Denied Errors
```bash
# Windows - Run as Administrator
# macOS/Linux - Use sudo or virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

##### Memory Errors on Large Networks
```bash
# Reduce population size
python connectivity_ga.py large_network.txt 1 0.05 0.03 20 3 0.8 0.05
#                                                    ↑ Smaller population
```

##### File Not Found Errors
```bash
# Ensure you're in the correct directory
pwd  # Check current directory
ls inputs/  # Verify input files exist
```

#### Python Version Issues

##### Python 2.x Compatibility
This project requires Python 3.6+. If you have Python 2.x:
```bash
python3 --version  # Check Python 3 availability
python3 connectivity_ga.py ...  # Use python3 explicitly
```

##### Multiple Python Versions
```bash
# Use specific Python version
python3.8 connectivity_ga.py ...
# or create version-specific virtual environment
python3.8 -m venv venv38
```

## IDE Setup

### Visual Studio Code

#### Recommended Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-toolsai.jupyter"
  ]
}
```

#### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

#### Project Setup
1. Open PyCharm
2. File → Open → Select Critical-GA directory
3. Configure Python interpreter (virtual environment recommended)
4. Mark `inputs/` as Resource Root

### Jupyter Notebook

#### Installation
```bash
pip install jupyter
```

#### Usage
```bash
jupyter notebook
# Create new notebook and import modules
import sys
sys.path.append('/path/to/Critical-GA')
from connectivity_ga import *
```

## Advanced Setup

### Multiprocessing Configuration

#### CPU Core Detection
```python
import multiprocessing
print(f"Available CPU cores: {multiprocessing.cpu_count()}")
```

#### Optimal Process Count
```python
# In connectivity_greedy.py, modify:
self.pool_size = multiprocessing.cpu_count() - 1  # Leave one core free
```

### Memory Optimization

#### Large Network Handling
```python
# Reduce memory usage for large networks
pop_size = 20  # Instead of default 100
max_generations = 1000  # Instead of default 5000
```

### Performance Monitoring

#### Enable Timing Output
```bash
# Modify connectivity_runner.py to log detailed timing
python connectivity_runner.py > timing_log.txt 2>&1
```

#### Memory Profiling
```bash
pip install memory-profiler
python -m memory_profiler connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```

## Docker Setup (Optional)

### Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "connectivity_ga.py", "karate.txt", "1", "0.05", "0.03", "50", "3", "0.8", "0.05"]
```

### Docker Commands
```bash
docker build -t critical-ga .
docker run -v $(pwd)/outputs:/app/outputs critical-ga
```

## Cloud Setup

### Google Colab
```python
# Install dependencies
!pip install networkx pyvis

# Clone repository
!git clone https://github.com/kepestamas/Critical-GA.git
%cd Critical-GA

# Run algorithms
!python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
```

### AWS EC2
```bash
# Launch EC2 instance with Python 3
sudo yum update -y
sudo yum install python3 git -y
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
pip3 install --user networkx numpy matplotlib pyvis
```

## Backup and Recovery

### Configuration Backup
```bash
# Save current environment
pip freeze > requirements.txt

# Restore environment
pip install -r requirements.txt
```

### Data Backup
```bash
# Backup results
tar -czf critical_ga_results_$(date +%Y%m%d).tar.gz outputs/

# Restore results
tar -xzf critical_ga_results_20251016.tar.gz
```

## Updates and Maintenance

### Updating the Project
```bash
git pull origin main
pip install --upgrade networkx numpy matplotlib pyvis
```

### Version Management
```bash
# Check current versions
pip list | grep -E "(networkx|numpy|matplotlib|pyvis)"

# Update specific package
pip install --upgrade networkx
```

### Cleaning Up
```bash
# Remove virtual environment
deactivate  # If in virtual environment
rm -rf critical_ga_env/

# Clean output files
rm -rf outputs/*
```

## Getting Help

### Documentation
- **README.md**: Project overview and basic usage
- **docs/API.md**: Detailed API documentation
- **docs/ALGORITHMS.md**: Algorithm implementation details
- **docs/DATASETS.md**: Dataset descriptions and formats

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Pull Requests**: Contribute improvements

### Technical Support
For installation issues:
1. Check this installation guide
2. Search existing GitHub issues
3. Create new issue with system details and error messages
4. Include Python version, OS, and dependency versions

---

**Next Steps**: After successful installation, proceed to the main [README.md](../README.md) for usage instructions and examples.