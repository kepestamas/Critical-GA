# Dataset Documentation

## Overview

This project includes a comprehensive collection of network datasets from various domains including social networks, biological systems, infrastructure networks, and synthetic graph models. These datasets serve as benchmarks for evaluating the Critical Network Disruption Problem (CNDP) algorithms.

## Dataset Categories

### Social Networks

#### Zachary's Karate Club (`karate.txt`)
- **Nodes**: 34
- **Edges**: 78
- **Description**: Social network of friendships between members of a karate club
- **Source**: Wayne W. Zachary (1977)
- **Properties**: Small-world, community structure
- **Format**: Edge list (space-separated)
- **Use Case**: Algorithm testing, community detection validation

#### Dolphin Social Network (`dolphins.txt`)
- **Nodes**: 62
- **Edges**: 159
- **Description**: Social network of bottlenose dolphins in Doubtful Sound, New Zealand
- **Source**: D. Lusseau et al. (2003)
- **Properties**: Biological social structure, modularity
- **Format**: Edge list
- **Use Case**: Biological network analysis, robustness testing

#### College Football Network (`football.txt`)
- **Nodes**: 115
- **Edges**: 613
- **Description**: Network of American football games between colleges
- **Source**: M. Girvan and M. E. J. Newman (2002)
- **Properties**: Community structure, seasonal patterns
- **Format**: Edge list
- **Use Case**: Community detection, sports network analysis

### Biological Networks

#### Brain Networks
- **Cat Mixed Species** (`bn-cat-mixed-species_brain_1.edges`)
- **Fly Drosophila Medulla** (`bn-fly-drosophila_medulla_1.edges`)
- **Mouse Retina** (`bn-mouse_retina_1.edges`)
- **Mouse Visual Cortex** (`bn-mouse_visual-cortex_2.edges`)

**Common Properties:**
- Neural connectivity patterns
- Hierarchical organization
- Small-world characteristics
- Critical for understanding brain function

**Applications:**
- Neuroscience research
- Brain disorder modeling
- Cognitive network analysis

#### Metabolic Networks

##### E. coli Network (`Ecoli.txt`)
- **Description**: Metabolic pathway network of E. coli bacteria
- **Properties**: Scale-free, modular structure
- **Applications**: Systems biology, drug target identification

##### Bovine Network (`Bovine.txt`)
- **Description**: Protein-protein interaction network in bovine
- **Properties**: Power-law degree distribution
- **Applications**: Comparative genomics, evolutionary biology

#### Disease Networks

##### Human Diseasome (`humanDiseasome.txt`)
- **Description**: Network of human diseases and associated genes
- **Properties**: Bipartite structure, disease clustering
- **Applications**: Medical research, drug discovery

### Infrastructure Networks

#### Transportation Networks

##### European Road Network (`inf-euroroad.edges`)
- **Nodes**: ~1,000
- **Edges**: ~1,300
- **Description**: Major European road connections
- **Properties**: Geographic constraints, hub structure
- **Applications**: Transportation planning, robustness analysis

##### OpenFlights Network (`inf-openflights.edges`)
- **Description**: Global airline route network
- **Properties**: Scale-free, small-world
- **Applications**: Epidemic spreading, transportation efficiency

##### US Air Traffic (`inf-USAir97.mtx`)
- **Description**: US domestic flight network (1997)
- **Format**: Matrix Market format
- **Applications**: Aviation network analysis, hub identification

#### Power Grid Networks

##### Power Grid 494 (`power-494-bus.mtx`)
- **Nodes**: 494
- **Description**: Western States Power Grid topology
- **Properties**: Sparse, geographic constraints
- **Applications**: Power system reliability, cascading failure analysis

##### Power Grid 662 (`power-662-bus.mtx`)
- **Nodes**: 662
- **Description**: Extended power grid network
- **Applications**: Smart grid design, vulnerability assessment

#### Communication Networks

##### Internet AS Graph (`out.as20000102`)
- **Description**: Internet Autonomous System topology (January 2, 2000)
- **Properties**: Heavy-tailed degree distribution, hierarchical
- **Applications**: Internet topology analysis, routing optimization

##### Infection Networks
- **Dublin** (`ia-infect-dublin.mtx`)
- **Hyper** (`ia-infect-hyper.mtx`)

**Properties**: Contact networks for disease transmission modeling
**Applications**: Epidemiology, public health planning

### Synthetic Networks

#### Scale-Free Networks (Barabási-Albert Model)

##### `BarabasiAlbert_n500m1.txt`
- **Nodes**: 500
- **Parameter m**: 1 (each new node connects to 1 existing node)
- **Properties**: Power-law degree distribution, preferential attachment

##### `BarabasiAlbert_n1000m1.txt`
- **Nodes**: 1000
- **Parameter m**: 1
- **Properties**: Larger scale-free network

**Format**: Adjacency list
```
nodes:edges
0: 1 2 3
1: 0 4 5
...
```

**Applications:**
- Social network modeling
- Web graph analysis
- Scale-free network robustness

#### Random Networks (Erdős-Rényi Model)

##### `ErdosRenyi_n250.txt`
- **Nodes**: 250
- **Model**: G(n,p) with specified connection probability

##### `ErdosRenyi_n500.txt`
- **Nodes**: 500
- **Properties**: Binomial degree distribution, random structure

**Applications:**
- Baseline comparisons
- Random network properties
- Phase transition studies

#### Small-World Networks (Watts-Strogatz Model)

##### `WattsStrogatz_n250.txt`
- **Nodes**: 250
- **Properties**: High clustering, short path lengths

##### `WattsStrogatz_n500.txt`
- **Nodes**: 500
- **Properties**: Small-world characteristics

**Applications:**
- Social network modeling
- Information spread analysis
- Network efficiency studies

#### Forest Fire Model

##### `ForestFire_n250.txt`
- **Nodes**: 250
- **Properties**: Heavy-tailed distributions, community structure

##### `ForestFire_n500.txt`
- **Nodes**: 500
- **Properties**: Realistic web graph characteristics

**Applications:**
- Web graph modeling
- Information network analysis
- Dynamic network growth

### Specialized Networks

#### Circuit Networks (`Circuit.txt`)
- **Description**: Electronic circuit connectivity
- **Properties**: Engineered structure, regular patterns
- **Applications**: VLSI design, fault tolerance

#### Animal Networks

##### Hamster Network (`hamster.txt`)
- **Description**: Social interaction network of hamsters
- **Applications**: Animal behavior modeling

##### Zebra Network (`zebra.txt`)
- **Description**: Zebra social group interactions
- **Applications**: Herd behavior analysis

### Geographic Networks

#### Road Networks

##### Minnesota Roads (`road-minnesota.mtx`)
- **Description**: Road network of Minnesota
- **Format**: Matrix Market sparse format
- **Properties**: Planar graph, geographic embedding
- **Applications**: Navigation systems, traffic analysis

## File Formats

### Format 1: Edge List (Space-Separated)
```
1 2
1 3
2 3
4 5
```
**Used by**: Most social and biological networks

### Format 2: Edge List (Tab-Separated)
```
1	2
1	3
2	3
```
**Used by**: Some infrastructure networks

### Format 3: Adjacency List
```
nodes:edges
0: 1 2 3
1: 0 4 5
2: 0 3 6
```
**Used by**: Synthetic networks (BA, ER, WS, FF)

### Format 4: Matrix Market (.mtx)
```
%%MatrixMarket matrix coordinate pattern symmetric
494 494 1080
1 2
1 3
...
```
**Used by**: Power grids, some infrastructure networks

### Format 5: Custom Biological Format
```
node1 neighbors_as_string
node2 neighbors_as_string
```
**Used by**: Some biological networks

## Dataset Statistics

| Network | Nodes | Edges | Avg Degree | Clustering | Diameter | Type |
|---------|-------|-------|------------|------------|-----------|-------|
| karate | 34 | 78 | 4.59 | 0.571 | 5 | Social |
| dolphins | 62 | 159 | 5.13 | 0.259 | 8 | Social |
| football | 115 | 613 | 10.66 | 0.403 | 4 | Social |
| BA_n500 | 500 | 499 | 1.996 | ~0 | ~9 | Synthetic |
| BA_n1000 | 1000 | 999 | 1.998 | ~0 | ~11 | Synthetic |
| ER_n250 | 250 | ~312 | ~2.5 | ~0.01 | ~8 | Synthetic |
| ER_n500 | 500 | ~625 | ~2.5 | ~0.005 | ~9 | Synthetic |
| WS_n250 | 250 | ~500 | ~4 | ~0.5 | ~6 | Synthetic |
| WS_n500 | 500 | ~1000 | ~4 | ~0.5 | ~7 | Synthetic |
| power-494 | 494 | 1080 | 4.37 | 0.107 | 17 | Infrastructure |
| power-662 | 662 | 1648 | 4.98 | 0.103 | 25 | Infrastructure |

## Usage Guidelines

### Dataset Selection

#### For Algorithm Development:
- Start with small networks: `karate.txt`, `dolphins.txt`
- Test scalability: `BA_n500`, `ER_n500`
- Validate on real networks: `football.txt`, `power-494-bus.mtx`

#### For Research Studies:
- **Social Networks**: Use karate, dolphins, football for social phenomena
- **Biological Systems**: Use brain networks, protein networks for bio applications
- **Infrastructure**: Use power grids, transportation for critical infrastructure
- **Synthetic**: Use BA, ER, WS for controlled experiments

### Performance Considerations

#### Small Networks (< 100 nodes):
- All algorithms perform well
- Suitable for parameter tuning
- Good for visualization

#### Medium Networks (100-1000 nodes):
- GA recommended for quality
- Greedy for speed
- Memory usage becomes important

#### Large Networks (> 1000 nodes):
- Prefer greedy algorithm
- Consider parallel processing
- Monitor memory consumption

### Experimental Design

#### Baseline Comparisons:
Use synthetic networks (ER) as baseline due to their random structure.

#### Real-World Validation:
Include networks from target application domain.

#### Scalability Testing:
Use networks of increasing size from same model family.

## Data Quality and Preprocessing

### Data Validation

All datasets have been validated for:
- **Connectivity**: Graphs are connected (single component)
- **Format Consistency**: Proper edge list formatting
- **Duplicate Removal**: No self-loops or multi-edges
- **Node Indexing**: Consistent node labeling

### Preprocessing Steps

1. **Format Standardization**: Convert to consistent edge list format
2. **Node Relabeling**: Ensure sequential integer labeling
3. **Component Analysis**: Verify single connected component
4. **Statistics Computation**: Calculate basic network properties

### Missing Data Handling

- **Isolated Nodes**: Removed from datasets
- **Inconsistent Edges**: Edge direction ignored (undirected graphs)
- **Weight Information**: Weights ignored (unweighted graphs)

## Dataset Sources and Citations

### Social Networks
- Zachary, W. W. (1977). An information flow model for conflict and fission in small groups.
- Lusseau, D., et al. (2003). The bottlenose dolphin community of Doubtful Sound features a large proportion of long-lasting associations.
- Girvan, M. & Newman, M. E. J. (2002). Community structure in social and biological networks.

### Biological Networks
- Various neuroscience databases and research publications
- Protein-protein interaction databases
- Gene regulatory network repositories

### Infrastructure Networks
- KONECT Network Collection
- Stanford Large Network Dataset Collection
- Various transportation and power grid databases

### Synthetic Networks
- Generated using NetworkX implementations of standard models
- Parameters chosen to match real-world network characteristics

## Extending the Dataset Collection

### Adding New Networks

1. **Format Conversion**: Convert to supported format
2. **Validation**: Run connectivity and format checks
3. **Documentation**: Add to this documentation
4. **Testing**: Verify with both algorithms

### Custom Network Generation

```python
import networkx as nx

# Generate Barabási-Albert network
G = nx.barabasi_albert_graph(1000, 2)
nx.write_edgelist(G, "custom_ba_n1000_m2.txt", data=False)

# Generate Erdős-Rényi network  
G = nx.erdos_renyi_graph(500, 0.01)
nx.write_edgelist(G, "custom_er_n500_p001.txt", data=False)
```

### Dataset Contribution Guidelines

1. **Source Attribution**: Provide proper citations
2. **Format Documentation**: Specify exact format used
3. **Quality Assurance**: Validate network properties
4. **Application Context**: Explain intended use cases
5. **Size Considerations**: Consider computational requirements

## Future Dataset Additions

### Planned Additions
- **Temporal Networks**: Time-varying network structures
- **Multilayer Networks**: Networks with multiple relationship types
- **Directed Networks**: Asymmetric relationships
- **Weighted Networks**: Edge importance variations

### Community Contributions
- Submit dataset suggestions via GitHub issues
- Provide networks with clear provenance
- Include application context and use cases
- Follow established format conventions

## Ethical Considerations

### Data Privacy
- Only publicly available datasets included
- No personally identifiable information
- Anonymized social network data

### Research Ethics
- Proper attribution to original data sources
- Respect for data use licenses and restrictions
- Academic and research use emphasis

### Reproducibility
- Complete dataset documentation
- Version control for dataset changes
- Transparent preprocessing procedures