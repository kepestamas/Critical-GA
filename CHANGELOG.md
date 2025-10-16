# Critical-GA Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- Contributing guidelines and code of conduct
- Installation guide with multiple setup methods
- API documentation with detailed function descriptions
- Algorithm analysis and theoretical documentation
- Dataset documentation with statistics and sources

### Changed
- Improved code organization and documentation
- Enhanced README with comprehensive project overview
- Better structured file organization

### Fixed
- Documentation formatting and consistency

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