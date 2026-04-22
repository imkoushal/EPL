# EPL Plot Package

Matplotlib-like plotting for EPL (English Programming Language).

## Installation

```bash
epl install epl-plot
```

## Requirements

- Python 3.9+
- Matplotlib >= 3.5.0
- NumPy >= 1.20.0

## Quick Start

```epl
Use "epl-plot"

-- Create a simple line plot
Set x to [1, 2, 3, 4, 5]
Set y to [2, 4, 6, 8, 10]

create_figure(10, 6)
plot_line(x, y, "My Data", "blue", "-")
set_title("My First EPL Plot", 16)
set_x_label("X Axis", 12)
set_y_label("Y Axis", 12)
add_legend("upper left")
add_grid(True, "major", "both")
save_plot("my_chart.png", 150)
```

## API Reference

### Figure Management

| Function | Description |
|----------|-------------|
| `create_figure(width, height)` | Create new figure |
| `create_subplots(rows, cols)` | Create subplot grid |
| `select_subplot(fig, row, col)` | Select subplot |
| `show_plot()` | Display plot |
| `save_plot(path, dpi)` | Save to file |
| `close_plot()` | Close plot |
| `clear_plot()` | Clear plot |

### Line Plots

| Function | Description |
|----------|-------------|
| `plot_line(x, y, label, color, style)` | Line plot |
| `plot_lines(datasets)` | Multiple lines |
| `plot_function(func, min, max, n, label)` | Plot function |

### Scatter Plots

| Function | Description |
|----------|-------------|
| `scatter_plot(x, y, label, color, size)` | Scatter |
| `scatter_with_colors(x, y, c, cmap)` | Colored scatter |
| `scatter_with_sizes(x, y, sizes)` | Sized scatter |

### Bar Charts

| Function | Description |
|----------|-------------|
| `bar_chart(cats, vals, label, color)` | Vertical bars |
| `horizontal_bar_chart(cats, vals, ...)` | Horizontal bars |
| `grouped_bar_chart(cats, data, labels)` | Grouped bars |
| `stacked_bar_chart(cats, data, labels)` | Stacked bars |

### Histograms

| Function | Description |
|----------|-------------|
| `histogram(data, bins, label, color, alpha)` | Histogram |
| `histogram_2d(x, y, bins)` | 2D histogram |

### Pie Charts

| Function | Description |
|----------|-------------|
| `pie_chart(vals, labels, colors, explode)` | Pie chart |
| `donut_chart(vals, labels, colors)` | Donut chart |

### Area Plots

| Function | Description |
|----------|-------------|
| `area_plot(x, y, label, color, alpha)` | Area fill |
| `fill_between(x, y1, y2, label, ...)` | Fill between |
| `stacked_area(x, data, labels, colors)` | Stacked area |

### Statistical Plots

| Function | Description |
|----------|-------------|
| `box_plot(data, labels)` | Box plot |
| `violin_plot(data, labels)` | Violin plot |
| `plot_with_error_bars(x, y, err, ...)` | Error bars |

### Heatmaps & Contours

| Function | Description |
|----------|-------------|
| `heatmap(data, x, y, cmap, show_vals)` | Heatmap |
| `contour_plot(x, y, z, levels, cmap)` | Contour |
| `filled_contour(x, y, z, levels, cmap)` | Filled contour |

### Customization - Labels

| Function | Description |
|----------|-------------|
| `set_title(title, fontsize)` | Set title |
| `set_x_label(label, fontsize)` | X-axis label |
| `set_y_label(label, fontsize)` | Y-axis label |
| `add_legend(location)` | Add legend |

### Customization - Axes

| Function | Description |
|----------|-------------|
| `set_x_limits(min, max)` | X-axis limits |
| `set_y_limits(min, max)` | Y-axis limits |
| `set_x_ticks(pos, labels)` | X tick marks |
| `set_y_ticks(pos, labels)` | Y tick marks |
| `set_log_scale(axis)` | Log scale |

### Customization - Style

| Function | Description |
|----------|-------------|
| `add_grid(show, which, axis)` | Grid lines |
| `set_style(style)` | Plot style |
| `set_colormap(cmap)` | Default colormap |

### Annotations

| Function | Description |
|----------|-------------|
| `add_text(x, y, text, size, color)` | Add text |
| `add_annotation(text, xy, xytext, arrow)` | Annotation |
| `add_horizontal_line(y, label, color, style)` | H-line |
| `add_vertical_line(x, label, color, style)` | V-line |
| `add_horizontal_span(ymin, ymax, color, alpha)` | H-span |
| `add_vertical_span(xmin, xmax, color, alpha)` | V-span |

### Colors

| Function | Description |
|----------|-------------|
| `get_color_palette(name, n)` | Get palette |
| `add_colorbar(label)` | Add colorbar |

## Available Styles

- `seaborn`, `ggplot`, `dark_background`, `bmh`, `fivethirtyeight`

## Available Colormaps

- `viridis`, `plasma`, `inferno`, `magma`, `cividis`
- `hot`, `cool`, `spring`, `summer`, `autumn`, `winter`
- `Blues`, `Reds`, `Greens`, `Purples`, `Oranges`

## License

MIT License - Part of the EPL ecosystem.
