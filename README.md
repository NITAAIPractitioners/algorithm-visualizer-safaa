# algorithm-visualizer-safaa

An interactive web-based platform for visualizing algorithms, built with Python and Streamlit. Perfect for graduate-level students learning algorithms.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Multiple Algorithm Categories** - Network Flow, Graph Traversal, Shortest Path, MST, Sorting
- **Step-by-step execution** - Walk through each iteration of algorithms
- **Dual visualization** - View both the main graph and auxiliary structures
- **Interactive controls** - Next, Previous, First, Last, and Auto-run options
- **Detailed explanations** - Understand what's happening at each step
- **Pre-loaded examples** - Start with sample graphs or create your own
- **Real-time metrics** - Track algorithm progress

## Available Algorithms

### Network Flow
-  **Ford-Fulkerson Algorithm** - Maximum flow computation

### Bin-Packing Problem
- 🚧 **First Fit** - Sequential bin packing
- 🚧 **Best Fit** - Optimized bin selection

### Euclidean Traveling Salesman
- 🚧 **MST-Based TSP** - Using minimum spanning tree
- 🚧 **MST with Minimum Matching** - MST + minimum matching approximation

### Vertex Cover
- 🚧 **Vertex Cover Approximation** - 2-approximation algorithm

### Approximation Algorithms
- 🚧 **Las Vegas Algorithm** - Randomized algorithm with guaranteed correctness
- 🚧 **Randomized Selection** - Quick select with randomization
- 🚧 **Random Sampling** - Sampling-based approximation

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Conda (recommended) or pip

### Installation with Conda

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/algorithm-visualizer.git
   cd algorithm-visualizer
   ```

2. **Create conda environment**
   ```bash
   conda create -n algo-viz python=3.10
   conda activate algo-viz
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

## 📖 How to Use

### 1. Select Algorithm Category

In the sidebar, choose from:
- Network Flow
- Bin-Packing Problem
- Euclidean Traveling Salesman
- Vertex Cover
- Approximation Algorithms

### 2. Choose Specific Algorithm

Pick the algorithm you want to visualize.

### 3. Configure Input

- Load example graphs or create custom inputs
- Set algorithm-specific parameters

### 4. Step Through Execution

Use the control buttons:
- **⏮️ First** - Jump to initial state
- **◀️ Previous** - Go back one step
- **▶️ Next** - Advance one step
- **⏭️ Last** - Jump to final result
- **🎬 Auto Run** - See complete solution

## Educational Use

This platform is designed for:
- **Graduate-level algorithm courses**
- **Self-study and practice**
- **Algorithm research and analysis**
- **Teaching and demonstrations**

## Docker Deployment

### Build and run locally:

```bash
# Build image
docker build -t algorithm-visualizer .

# Run container
docker run -p 8501:8501 algorithm-visualizer

# Access at http://localhost:8501
```

### Deploy to Azure:

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Azure deployment instructions.

##  Project Structure

```
algorithm-visualizer/
├── app.py                          # Main application with algorithm selector
├── algorithms/                     # Algorithm implementations
│   ├── __init__.py
│   ├── ford_fulkerson.py          # Ford-Fulkerson algorithm
│   └── ... (other algorithms)
├── utils/                          # Shared utilities
│   ├── __init__.py
│   └── graph_utils.py             # Graph visualization helpers
├── assets/                         # Images, logos, etc.
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── README.md                       # This file
├── DEPLOYMENT.md                   # Azure deployment guide
└── .gitignore                      # Git ignore rules
```

## Technology Stack

- **Streamlit** - Web framework for data apps
- **NetworkX** - Graph algorithms and structures
- **Matplotlib** - Graph rendering
- **Python 3.10+** - Core language

##  Contributing

Contributions are welcome! To add a new algorithm:

1. Create a new file in `algorithms/` folder
2. Implement the algorithm with a `render_<algorithm>()` function
3. Add it to the selector in `app.py`
4. Update this README

## Algorithm Implementation Guide

Each algorithm module should follow this structure:

```python
import streamlit as st

def render_algorithm_name():
    """Main rendering function for Algorithm Name"""
    
    # Initialize session state
    # Create input controls
    # Implement algorithm logic
    # Create visualization
    # Add step controls
```

## References

- Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.)
- Kleinberg, J., & Tardos, É. (2005). *Algorithm Design*

## License

This project is licensed under the MIT License.

## Author

Created for graduate-level algorithm education.

---

**If you find this useful, please star the repository!**

