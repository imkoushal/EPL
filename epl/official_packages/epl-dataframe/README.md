# EPL DataFrame Package

Pandas-like DataFrame operations for EPL (English Programming Language).

## Installation

```bash
epl use epl-dataframe
```

## Requirements

- Python 3.9+
- Pandas >= 1.3.0

## Quick Start

```epl
Use "epl-dataframe"

-- Create a DataFrame
Set data to {"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "city": ["NYC", "LA", "NYC"]}
Set df to create_dataframe(data)

-- Basic operations
Say "Columns: " + columns_of(df)
Say "Rows: " + rows_of(df)

-- Filter data
Set adults to filter_where(df, "age", ">=", 30)
Say "Adults: " + print_dataframe(adults)

-- Group and aggregate
Set by_city to group_and_count(df, "city")
Say "Count by city: " + print_dataframe(by_city)

-- Save results
save_to_csv(df, "output.csv")
```

## API Reference

### DataFrame Creation

| Function | Description | Example |
|----------|-------------|---------|
| `create_dataframe(data)` | Create from dict | `create_dataframe({"col": [1,2]})` |
| `dataframe_from_records(records)` | Create from list of dicts | `dataframe_from_records([{...}])` |
| `read_csv(path)` | Read CSV file | `read_csv("data.csv")` |
| `read_json(path)` | Read JSON file | `read_json("data.json")` |
| `read_excel(path)` | Read Excel file | `read_excel("data.xlsx")` |

### Properties

| Function | Description |
|----------|-------------|
| `columns_of(df)` | Get column names |
| `rows_of(df)` | Get row count |
| `shape_of_dataframe(df)` | Get (rows, cols) |
| `data_types_of(df)` | Get column types |
| `describe_dataframe(df)` | Statistical summary |
| `head_of(df, n)` | First n rows |
| `tail_of(df, n)` | Last n rows |

### Column Operations

| Function | Description |
|----------|-------------|
| `select_column(df, name)` | Get single column |
| `select_columns(df, names)` | Get multiple columns |
| `drop_column(df, name)` | Remove column |
| `rename_column(df, old, new)` | Rename column |
| `add_column(df, name, values)` | Add new column |

### Filtering

| Function | Description |
|----------|-------------|
| `filter_where(df, col, op, val)` | Filter with operator (>, <, ==, etc.) |
| `filter_equals(df, col, val)` | Filter equals |
| `filter_in(df, col, values)` | Filter in list |
| `filter_not_null(df, col)` | Filter non-null |
| `filter_contains(df, col, substr)` | Filter string contains |
| `sample_rows(df, n)` | Random sample |

### Sorting

| Function | Description |
|----------|-------------|
| `sort_by(df, col, ascending)` | Sort by column |
| `sort_by_columns(df, cols, asc)` | Sort by multiple |

### Grouping & Aggregation

| Function | Description |
|----------|-------------|
| `group_and_sum(df, group, sum)` | Group and sum |
| `group_and_mean(df, group, mean)` | Group and mean |
| `group_and_count(df, group)` | Group and count |
| `aggregate(df, groups, agg)` | Multiple aggregations |
| `value_counts(df, col)` | Count unique values |

### Statistics

| Function | Description |
|----------|-------------|
| `sum_of_column(df, col)` | Column sum |
| `mean_of_column(df, col)` | Column mean |
| `median_of_column(df, col)` | Column median |
| `min_of_column(df, col)` | Column min |
| `max_of_column(df, col)` | Column max |
| `std_of_column(df, col)` | Column std dev |

### Merging

| Function | Description |
|----------|-------------|
| `merge_dataframes(df1, df2, on, how)` | Merge on column |
| `join_dataframes(df1, df2, how)` | Join by index |
| `concatenate_dataframes(dfs, axis)` | Concatenate |

### Export

| Function | Description |
|----------|-------------|
| `save_to_csv(df, path)` | Save as CSV |
| `save_to_json(df, path)` | Save as JSON |
| `save_to_excel(df, path)` | Save as Excel |
| `to_dict(df)` | Convert to dict |
| `to_records(df)` | Convert to records |
| `print_dataframe(df)` | Display |

## License

MIT License - Part of the EPL ecosystem.
