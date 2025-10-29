# Critical-GA Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Dual-Constraint Model Implementation** (October 28, 2025)
  - New constraint system: fixed node count + weight budget
  - Both GA and Greedy algorithms support dual constraints
  - Fallback strategies for generating feasible solutions
  - Weight budget parameter in GA command line (5th parameter)
  - Documentation: `DUAL_CONSTRAINT_MODEL.md`
  
- Comprehensive documentation suite
- Contributing guidelines and code of conduct
- Installation guide with multiple setup methods
- API documentation with detailed function descriptions
- Algorithm analysis and theoretical documentation
- Dataset documentation with statistics and sources

### Changed
- **Breaking Change**: GA command line parameter order
  - Added `weight_budget` parameter at position 5
  - Shifted all subsequent parameters (pop_size, tournament_size, etc.)
  - New format: `python connectivity_ga.py <input> <run_id> <node_frac> <edge_frac> <weight_budget> <pop_size> <tournament_size> <p_cross> <p_mut> [payoff]`
  
- **Genetic Algorithm (`connectivity_ga.py`)**:
  - `k_nodes` calculated as node count (not weight target)
  - `k_weight_budget` as constraint on total weight
  - `generate_one_pair()`: Random sampling with fallback to lightest nodes
  - `mutate()`: Respects weight budget, keeps original if no valid replacement
  - `split_node_lists()`: Crossover maintains both constraints
  - Output filename includes `_wb_<weight_budget>` suffix
  
- **Greedy Algorithm (`connectivity_greedy.py`)**:
  - Config uses K1 (count) and K1_weight_budget (constraint)
  - Fixed 5% node count, 10% weight budget
  - Main loop checks both constraints before adding nodes
  - Candidate evaluation filters by weight budget
  
- Updated documentation:
  - README.md: New command line format and dual-constraint explanation
  - ALGORITHMS.md: Updated with dual-constraint algorithms
  - All examples updated with weight_budget parameter
  
- Improved code organization and documentation
- Enhanced README with comprehensive project overview
- Better structured file organization

### Fixed
- Documentation formatting and consistency
- Syntax errors in greedy algorithm from incomplete replacement

## [1.0.0] - 2025-10-16

### Added
- Initial release of Critical Network Disruption Problem implementation
- Genetic Algorithm with tournament selection and adaptive mutation
- Greedy Algorithm with multiprocessing support
- Network analysis tool for comprehensive graph statistics
- Interactive network visualization using PyVis
- Batch processing system for multiple experiments
- Support for multiple network file formats
- Comprehensive dataset collection (34 networks)
- Output directory structure and result logging
- Git ignore configuration

### Core Features
- **Genetic Algorithm (`connectivity_ga.py`)**:
  - Tournament selection with configurable size
  - Union-based crossover operator
  - Descending mutation strategy
  - Elitist selection for population management
  - Configurable population size and generation count
  - Fitness evaluation with pairwise connectivity
  
- **Greedy Algorithm (`connectivity_greedy.py`)**:
  - Iterative best-choice selection
  - Multiprocessing support for parallel execution
  - Multiple run capability for solution diversity
  - Configurable iteration count and debug levels
  
- **Network Analysis (`network_analyzer.py`)**:
  - Basic graph properties (nodes, edges, connectivity)
  - Distance metrics (diameter, average path length)
  - Centrality measures (betweenness, clustering)
  - Spectral analysis (Laplacian eigenvalues)
  - Efficiency and robustness metrics
  
- **Visualization (`network_painter.py`)**:
  - Interactive HTML network visualization
  - Support for highlighting removed elements
  - PyVis-based rendering with zoom and pan
  
- **Batch Processing (`connectivity_runner.py`)**:
  - Automated multi-network experiments
  - Timing measurements and performance logging
  - Configurable parameter sets
  - Result aggregation

### Supported Networks
- **Social Networks**: Karate Club, Dolphins, College Football
- **Biological Networks**: Brain networks, Protein interactions, Disease networks
- **Infrastructure**: Power grids, Transportation networks, Internet topology
- **Synthetic Networks**: Barabási-Albert, Erdős-Rényi, Watts-Strogatz, Forest Fire

### File Format Support
- Edge list (space and tab separated)
- Adjacency list format
- Matrix Market (.mtx) format
- Custom biological network formats

### Documentation
- Comprehensive README with usage examples
- API documentation for all functions
- Algorithm implementation details
- Dataset descriptions and statistics
- Installation and setup instructions

### Performance Features
- Fitness evaluation caching
- Memory-efficient graph operations
- Configurable multiprocessing support
- Scalable to networks with 1000+ nodes

## Development Notes

### Known Limitations
- Single-objective optimization only
- Limited to undirected, unweighted graphs
- No real-time parameter adjustment
- Command-line interface only

### Future Enhancements
- Multi-objective optimization (Pareto fronts)
- GUI interface for interactive parameter tuning
- Support for directed and weighted networks
- GPU acceleration for large-scale problems
- Online algorithm adaptation
- Advanced visualization features

### Technical Debt
- Some global variable usage in GA implementation
- Hardcoded file format detection logic
- Limited error handling in file I/O operations
- No configuration file support

## Release Process

### Version Numbering
- **Major** (X.y.z): Breaking changes, major new features
- **Minor** (x.Y.z): New features, significant improvements
- **Patch** (x.y.Z): Bug fixes, documentation updates

### Release Checklist
- [ ] Update version numbers in relevant files
- [ ] Update CHANGELOG.md with release notes
- [ ] Run full test suite
- [ ] Update documentation if needed
- [ ] Tag release in git
- [ ] Create GitHub release with notes

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code contribution process
- Documentation standards
- Testing requirements
- Issue reporting procedures

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

For questions about releases or to suggest improvements, please open an issue on GitHub.