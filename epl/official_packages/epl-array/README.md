# EPL Array Package

NumPy-like array operations for EPL (English Programming Language).

## Installation

```bash
epl use epl-array
```

## Requirements

- Python 3.9+
- NumPy >= 1.20.0

## Quick Start

```epl
Use "epl-array"

-- Create arrays
Set my_array to create_array([1, 2, 3, 4, 5])
Set zeros to array_of_zeros([3, 3])
Set ones to array_of_ones([2, 4])

-- Array operations
Set result to add_arrays(my_array, my_array)
Say "Sum: " + sum_of_array(result)
Say "Mean: " + mean_of_array(result)

-- Linear algebra
Set matrix to create_array([[1, 2], [3, 4]])
Set inv to inverse_of(matrix)
Set det to determinant_of(matrix)
Say "Determinant: " + det
```

## API Reference

### Array Creation

| Function | Description | Example |
|----------|-------------|---------|
| `create_array(data)` | Create array from list | `create_array([1, 2, 3])` |
| `array_of_zeros(shape)` | Array filled with zeros | `array_of_zeros([3, 3])` |
| `array_of_ones(shape)` | Array filled with ones | `array_of_ones([2, 4])` |
| `array_range(start, stop, step)` | Evenly spaced values | `array_range(0, 10, 2)` |
| `array_linspace(start, stop, count)` | Linear spacing | `array_linspace(0, 1, 50)` |
| `random_array(shape)` | Random values [0, 1) | `random_array([5, 5])` |
| `random_integers(low, high, shape)` | Random integers | `random_integers(1, 100, [10])` |
| `identity_matrix(size)` | Identity matrix | `identity_matrix(4)` |

### Array Properties

| Function | Description |
|----------|-------------|
| `shape_of(array)` | Get dimensions |
| `size_of(array)` | Total elements |
| `dimensions_of(array)` | Number of dimensions |
| `data_type_of(array)` | Element data type |

### Array Manipulation

| Function | Description |
|----------|-------------|
| `reshape_array(array, shape)` | Change shape |
| `flatten_array(array)` | Convert to 1D |
| `transpose_array(array)` | Swap rows/columns |
| `concatenate_arrays(arrays, axis)` | Join arrays |
| `stack_arrays(arrays, axis)` | Stack on new axis |
| `split_array(array, sections, axis)` | Split into parts |
| `slice_array(array, start, end)` | Get subset |

### Math Operations

| Function | Description |
|----------|-------------|
| `add_arrays(a, b)` | Element-wise addition |
| `subtract_arrays(a, b)` | Element-wise subtraction |
| `multiply_arrays(a, b)` | Element-wise multiplication |
| `divide_arrays(a, b)` | Element-wise division |
| `power_array(array, exp)` | Raise to power |
| `sqrt_array(array)` | Square root |
| `exp_array(array)` | Exponential |
| `log_array(array)` | Natural logarithm |
| `abs_array(array)` | Absolute value |
| `sin_array(array)` | Sine |
| `cos_array(array)` | Cosine |
| `tan_array(array)` | Tangent |

### Statistics

| Function | Description |
|----------|-------------|
| `sum_of_array(array)` | Sum of elements |
| `mean_of_array(array)` | Mean (average) |
| `median_of_array(array)` | Median |
| `std_of_array(array)` | Standard deviation |
| `variance_of_array(array)` | Variance |
| `min_of_array(array)` | Minimum |
| `max_of_array(array)` | Maximum |
| `argmin_of_array(array)` | Index of minimum |
| `argmax_of_array(array)` | Index of maximum |
| `percentile_of_array(array, q)` | q-th percentile |

### Linear Algebra

| Function | Description |
|----------|-------------|
| `dot_product(a, b)` | Dot product |
| `matrix_multiply(a, b)` | Matrix multiplication |
| `inverse_of(matrix)` | Matrix inverse |
| `determinant_of(matrix)` | Determinant |
| `eigenvalues_of(matrix)` | Eigenvalues |
| `eigenvectors_of(matrix)` | Eigenvalues & vectors |
| `solve_linear_system(A, b)` | Solve Ax = b |
| `norm_of(array)` | Euclidean norm |
| `trace_of(matrix)` | Matrix trace |
| `rank_of(matrix)` | Matrix rank |

### Comparison & Sorting

| Function | Description |
|----------|-------------|
| `arrays_equal(a, b)` | Check equality |
| `where_in_array(cond, x, y)` | Conditional select |
| `all_true(array)` | Check if all true |
| `any_true(array)` | Check if any true |
| `sort_array(array)` | Sort ascending |
| `argsort_array(array)` | Sort indices |
| `unique_in_array(array)` | Unique elements |

## License

MIT License - Part of the EPL ecosystem.
