# Payoff Functions Implementation Plan

## Overview
This document outlines the plan to add two new payoff functions to the Critical Network Disruption Problem (CNDP) implementation, making them interchangeable with the existing pairwise connectivity function.

## Current State Analysis

### Existing Pairwise Connectivity Function

**In `connectivity_ga.py`:**
```python
def pairwise(lst):
    global fitness_count
    fitness_count = fitness_count + 1
    summa = sum([len(c)*(len(c)-1)/2 if (len(c)>1) else 0 for c in lst])
    return summa
```

**In `connectivity_greedy.py`:**
```python
def f_pairwise(lst):
    global fitness_count
    fitness_count = fitness_count + 1
    summa = sum([len(c)*(len(c)-1)/2 if (len(c)>1) else 0 for c in lst])
    return summa
```

**Common Pattern:**
- Input: List/iterator of connected components from `nx.connected_components()`
- Output: Numeric fitness score (float/int)
- Side effect: Increments global `fitness_count`
- Objective: **Minimize** the returned value (lower = better disruption)

## Planned Payoff Functions

### 1. Number of Components Function

**Objective:** Maximize the number of connected components
- **Logic:** More components = better network disruption
- **Optimization:** Since algorithms minimize, return negative count
- **Formula:** `-len(list(components))`

**Function Design:**
```python
def number_of_components(lst):
    global fitness_count
    fitness_count = fitness_count + 1
    # Convert to list to count components
    components = list(lst)
    # Return negative count (more components = lower fitness = better)
    return -len(components)
```

### 2. Largest Component Size Function

**Objective:** Minimize the size of the largest connected component
- **Logic:** Smaller largest component = better fragmentation
- **Optimization:** Return size directly (smaller = better)
- **Formula:** `max(len(c) for c in components) if components else 0`

**Function Design:**
```python
def largest_component_size(lst):
    global fitness_count
    fitness_count = fitness_count + 1
    # Convert to list to find maximum
    components = list(lst)
    if not components:
        return 0
    # Return size of largest component (smaller = better)
    return max(len(c) for c in components)
```

## Implementation Architecture

### 1. Payoff Function Interface

**Standard Interface:**
```python
def payoff_function(components_iterator):
    """
    Standard payoff function interface.
    
    Args:
        components_iterator: Iterator of connected components from nx.connected_components()
        
    Returns:
        float: Fitness score (lower values indicate better network disruption)
        
    Side Effects:
        Increments global fitness_count variable
    """
    global fitness_count
    fitness_count += 1
    # Implementation-specific logic here
    return fitness_score
```

### 2. Function Registry

**Payoff Function Dictionary:**
```python
PAYOFF_FUNCTIONS = {
    'pairwise': pairwise_connectivity,
    'components': number_of_components, 
    'largest': largest_component_size
}
```

### 3. Configuration Parameter

**Command Line Parameter:**
- Add new parameter: `payoff_function` (default: 'pairwise')
- Update argument parsing to include payoff function selection
- Validate function name against available options

**Usage Examples:**
```bash
# Existing behavior (default)
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05

# With explicit pairwise (same as default)
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05 pairwise

# Using number of components
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05 components

# Using largest component size
python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05 largest
```

## Implementation Checklist

### Phase 1: Core Function Implementation
- [ ] Create `payoff_functions.py` module with all three functions
- [ ] Implement standard interface with proper documentation
- [ ] Add comprehensive docstrings with examples
- [ ] Include input validation and error handling
- [ ] Add unit tests for each function

### Phase 2: Integration with Genetic Algorithm
- [ ] Modify `connectivity_ga.py` to import payoff functions
- [ ] Add command-line parameter parsing for payoff function selection
- [ ] Replace hardcoded `pairwise()` calls with configurable function
- [ ] Update fitness evaluation to use selected payoff function
- [ ] Maintain backward compatibility (default to pairwise)

### Phase 3: Integration with Greedy Algorithm
- [ ] Modify `connectivity_greedy.py` to import payoff functions
- [ ] Add command-line parameter parsing for payoff function selection
- [ ] Replace hardcoded `f_pairwise()` calls with configurable function
- [ ] Update all fitness evaluations in greedy algorithm
- [ ] Maintain backward compatibility

### Phase 4: Update Supporting Scripts
- [ ] Modify `connectivity_runner.py` to handle new parameter
- [ ] Update batch processing to test different payoff functions
- [ ] Ensure timing and logging work with all functions
- [ ] Add configuration options for experimental studies

### Phase 5: Documentation Updates
- [ ] Update `README.md` with new usage examples
- [ ] Update `docs/API.md` with payoff function documentation
- [ ] Update `docs/ALGORITHMS.md` with theoretical background
- [ ] Add performance comparison between payoff functions
- [ ] Update command-line help text

### Phase 6: Testing and Validation
- [ ] Create comprehensive test suite for payoff functions
- [ ] Test with small networks (karate, dolphins)
- [ ] Test with medium networks (Barabási-Albert 500)
- [ ] Validate mathematical correctness of each function
- [ ] Compare results across different payoff functions

## Technical Considerations

### 1. Performance Implications

**Number of Components:**
- **Complexity:** O(k) where k = number of components
- **Performance:** Fastest of the three functions
- **Memory:** Minimal additional memory usage

**Largest Component Size:**
- **Complexity:** O(k) where k = number of components  
- **Performance:** Fast, similar to component counting
- **Memory:** Minimal additional memory usage

**Pairwise Connectivity:**
- **Complexity:** O(k) where k = number of components
- **Performance:** Most computationally intensive (multiplication/division)
- **Memory:** Minimal additional memory usage

### 2. Mathematical Properties

**Optimization Characteristics:**
- **Pairwise:** Quadratic growth with component size
- **Components:** Linear with number of splits
- **Largest:** Linear with largest component size

**Sensitivity to Changes:**
- **Pairwise:** Highly sensitive to component size changes
- **Components:** Only sensitive to splitting/merging events
- **Largest:** Only sensitive to changes in largest component

### 3. Backward Compatibility

**Requirements:**
- Default behavior must remain unchanged (pairwise connectivity)
- Existing scripts and batch jobs must continue to work
- Output file formats should remain consistent
- Parameter positions must be preserved

**Migration Strategy:**
- New parameter is optional (default: 'pairwise')
- Existing command-line calls work without modification
- Output includes payoff function type in filename/logs

## File Modifications Required

### Core Algorithm Files
- `connectivity_ga.py`: Update fitness function, parameter parsing
- `connectivity_greedy.py`: Update fitness function, parameter parsing
- `payoff_functions.py`: New module with all payoff functions

### Support Files
- `connectivity_runner.py`: Add payoff function parameter to batch runs
- `network_analyzer.py`: Consider adding payoff function analysis

### Documentation Files
- `README.md`: Update usage examples and feature descriptions
- `docs/API.md`: Document new payoff functions
- `docs/ALGORITHMS.md`: Add theoretical background
- `CHANGELOG.md`: Document new features

## Expected Benefits

### 1. Research Flexibility
- Compare different disruption objectives on same networks
- Study how different objectives affect optimal solutions
- Enable multi-objective analysis in future

### 2. Practical Applications
- **Pairwise:** Information flow disruption
- **Components:** Network fragmentation analysis  
- **Largest:** Targeted infrastructure protection

### 3. Code Quality
- More modular and extensible architecture
- Separation of concerns (algorithm vs. objective)
- Easier to add new payoff functions in future

## Risk Assessment

### Low Risk Items
- Adding new payoff functions (self-contained)
- Updating documentation
- Creating test cases

### Medium Risk Items  
- Modifying command-line parameter parsing
- Ensuring backward compatibility
- Performance impact assessment

### High Risk Items
- Modifying core algorithm logic in both GA and Greedy
- Maintaining global fitness_count behavior
- Integration testing across all combinations

## Success Criteria

1. **Functional:** All three payoff functions work correctly
2. **Compatible:** Existing usage continues to work unchanged  
3. **Tested:** Comprehensive test coverage for new functionality
4. **Documented:** Clear documentation for new features
5. **Performant:** No significant performance regression
6. **Extensible:** Easy to add more payoff functions in future

---

**Next Steps:** Begin with Phase 1 (Core Function Implementation) and proceed systematically through each phase, ensuring thorough testing at each step.