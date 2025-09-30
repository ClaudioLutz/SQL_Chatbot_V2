"""Test fixtures for analysis feature."""

# Small dataset (typical case)
SMALL_DATASET = {
    "columns": ["ProductID", "Name", "ListPrice"],
    "rows": [
        {"ProductID": 1, "Name": "Product A", "ListPrice": 49.99},
        {"ProductID": 2, "Name": "Product B", "ListPrice": 29.99},
        {"ProductID": 3, "Name": "Product C", "ListPrice": 79.99},
        {"ProductID": 4, "Name": "Product D", "ListPrice": 19.99},
        {"ProductID": 5, "Name": "Product E", "ListPrice": 39.99},
        {"ProductID": 6, "Name": "Product F", "ListPrice": 59.99},
        {"ProductID": 7, "Name": "Product G", "ListPrice": 89.99},
        {"ProductID": 8, "Name": "Product H", "ListPrice": 24.99},
        {"ProductID": 9, "Name": "Product I", "ListPrice": 34.99},
        {"ProductID": 10, "Name": "Product J", "ListPrice": 44.99}
    ]
}

# Large dataset (near limit)
LARGE_DATASET = {
    "columns": ["ID", "Value"],
    "rows": [{"ID": i, "Value": i * 1.5} for i in range(45000)]
}

# Too large dataset (exceeds limit)
TOO_LARGE_DATASET = {
    "columns": ["ID"],
    "rows": [{"ID": i} for i in range(60000)]
}

# Dataset with nulls
NULL_DATASET = {
    "columns": ["A", "B", "C"],
    "rows": [
        {"A": 1, "B": 2, "C": None},
        {"A": 2, "B": None, "C": 3},
        {"A": None, "B": 4, "C": 5},
        {"A": 6, "B": 7, "C": None}
    ]
}

# Mixed types dataset
MIXED_DATASET = {
    "columns": ["ID", "Name", "Price", "Date"],
    "rows": [
        {"ID": 1, "Name": "Item1", "Price": 10.5, "Date": "2024-01-01"},
        {"ID": 2, "Name": "Item2", "Price": 20.0, "Date": "2024-01-02"},
        {"ID": 3, "Name": "Item3", "Price": 15.75, "Date": "2024-01-03"},
        {"ID": 4, "Name": "Item4", "Price": 30.25, "Date": "2024-01-04"}
    ]
}

# Empty dataset
EMPTY_DATASET = {
    "columns": ["A"],
    "rows": []
}

# Single row (insufficient)
SINGLE_ROW_DATASET = {
    "columns": ["A", "B"],
    "rows": [{"A": 1, "B": 2}]
}
