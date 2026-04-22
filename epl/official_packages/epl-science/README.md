# EPL Science Package

SciPy-like scientific computing for EPL (English Programming Language).

## Installation

```bash
epl use epl-science
```

## Requirements

- Python 3.9+
- SciPy >= 1.7.0
- NumPy >= 1.20.0

## Quick Start

```epl
Use "epl-science"

-- Optimization: Find minimum of x² + 2x + 1
Define my_func Takes x
    Return x[0] * x[0] + 2 * x[0] + 1
End
Set result to minimize_function(my_func, [0], "BFGS")
Say "Minimum at: " + result["x"]

-- Integration
Define f Takes x
    Return x * x
End
Set integral to integrate(f, 0, 1)
Say "Integral of x² from 0 to 1: " + integral["value"]

-- Statistical test
Set group_a to [23, 25, 28, 24, 26]
Set group_b to [30, 32, 29, 31, 33]
Set test_result to t_test(group_a, group_b)
Say "T-test p-value: " + test_result["pvalue"]
```

## API Reference

### Optimization

| Function | Description |
|----------|-------------|
| `minimize_function(func, x0, method)` | Find function minimum |
| `maximize_function(func, x0, method)` | Find function maximum |
| `find_root(func, x0)` | Find function root |
| `solve_equation(func, x0)` | Solve equations |
| `linear_least_squares(A, b)` | Least squares |
| `curve_fit(func, x, y)` | Fit curve to data |

### Integration

| Function | Description |
|----------|-------------|
| `integrate(func, a, b)` | Definite integral |
| `integrate_trapezoid(y, x)` | Trapezoidal rule |
| `integrate_simpson(y, x)` | Simpson's rule |
| `double_integrate(func, x_range, y_range)` | Double integral |
| `solve_ode(func, y0, t_span)` | Solve ODE |

### Interpolation

| Function | Description |
|----------|-------------|
| `interpolate_linear(x, y)` | Linear interpolation |
| `interpolate_cubic(x, y)` | Cubic spline |
| `interpolate_at(interp, x)` | Evaluate interpolation |
| `spline_fit(x, y, smooth)` | Smoothing spline |

### Signal Processing

| Function | Description |
|----------|-------------|
| `fourier_transform(signal)` | FFT |
| `inverse_fourier(spectrum)` | Inverse FFT |
| `frequency_spectrum(signal, rate)` | Frequency spectrum |
| `convolve_signals(a, b)` | Convolution |
| `correlate_signals(a, b)` | Cross-correlation |
| `filter_signal(sig, type, cutoff, rate)` | Apply filter |
| `find_peaks(signal, height, dist)` | Find peaks |
| `smooth_signal(signal, window)` | Smooth signal |

### Statistical Tests

| Function | Description |
|----------|-------------|
| `t_test(a, b)` | Two-sample t-test |
| `t_test_one_sample(data, mean)` | One-sample t-test |
| `paired_t_test(a, b)` | Paired t-test |
| `chi_square_test(obs, exp)` | Chi-square test |
| `anova_test(groups)` | One-way ANOVA |
| `correlation_test(x, y)` | Pearson correlation |
| `spearman_correlation(x, y)` | Spearman correlation |
| `normality_test(data)` | Shapiro-Wilk test |

### Distributions

| Function | Description |
|----------|-------------|
| `normal_pdf(x, mean, std)` | Normal PDF |
| `normal_cdf(x, mean, std)` | Normal CDF |
| `normal_random(mean, std, n)` | Normal samples |
| `uniform_random(low, high, n)` | Uniform samples |
| `exponential_random(scale, n)` | Exponential samples |
| `poisson_random(mu, n)` | Poisson samples |
| `binomial_random(n, p, size)` | Binomial samples |

### Distance

| Function | Description |
|----------|-------------|
| `euclidean_distance(a, b)` | Euclidean distance |
| `cosine_similarity(a, b)` | Cosine similarity |
| `manhattan_distance(a, b)` | Manhattan distance |
| `distance_matrix(points)` | Pairwise distances |

## License

MIT License - Part of the EPL ecosystem.
