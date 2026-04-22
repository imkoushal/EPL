# EPL Learn Package

Scikit-learn like machine learning for EPL (English Programming Language).

## Installation

```bash
epl use epl-learn
```

## Requirements

- Python 3.9+
- Scikit-learn >= 1.0.0
- NumPy >= 1.20.0

## Quick Start

```epl
Use "epl-learn"

-- Load dataset
Set data to load_iris_dataset()
Set X to data["X"]
Set y to data["y"]

-- Split into train/test
Set split to split_data(X, y, 0.2)

-- Create and train classifier
Set classifier to create_random_forest_classifier(100, 10)
train_model(classifier, split["X_train"], split["y_train"])

-- Make predictions
Set predictions to predict(classifier, split["X_test"])

-- Evaluate
Set acc to accuracy_score(split["y_test"], predictions)
Say "Accuracy: " + acc
```

## API Reference

### Preprocessing

| Function | Description |
|----------|-------------|
| `scale_data(data)` | Standardize (zero mean, unit variance) |
| `normalize_data(data)` | Scale to [0, 1] |
| `encode_labels(labels)` | Labels to integers |
| `one_hot_encode(labels)` | One-hot encoding |
| `split_data(X, y, test_size)` | Train/test split |
| `fill_missing(data, strategy)` | Impute missing values |
| `reduce_dimensions(data, n)` | PCA reduction |

### Classification Models

| Function | Description |
|----------|-------------|
| `create_logistic_classifier()` | Logistic regression |
| `create_decision_tree_classifier(depth)` | Decision tree |
| `create_random_forest_classifier(n, depth)` | Random forest |
| `create_svm_classifier(kernel)` | Support vector machine |
| `create_knn_classifier(k)` | K-nearest neighbors |
| `create_naive_bayes_classifier()` | Gaussian Naive Bayes |
| `create_gradient_boost_classifier(n, lr)` | Gradient boosting |

### Regression Models

| Function | Description |
|----------|-------------|
| `create_linear_regressor()` | Linear regression |
| `create_ridge_regressor(alpha)` | Ridge regression |
| `create_lasso_regressor(alpha)` | Lasso regression |
| `create_decision_tree_regressor(depth)` | Decision tree |
| `create_random_forest_regressor(n, depth)` | Random forest |
| `create_svr(kernel)` | Support vector regressor |
| `create_knn_regressor(k)` | K-nearest neighbors |

### Training & Prediction

| Function | Description |
|----------|-------------|
| `train_model(model, X, y)` | Train model |
| `predict(model, X)` | Make predictions |
| `predict_probability(model, X)` | Get probabilities |

### Clustering

| Function | Description |
|----------|-------------|
| `kmeans_cluster(data, k)` | K-means clustering |
| `dbscan_cluster(data, eps, min)` | DBSCAN clustering |
| `hierarchical_cluster(data, k)` | Agglomerative clustering |
| `get_cluster_labels(result)` | Get labels |
| `get_cluster_centers(result)` | Get centers |

### Evaluation - Classification

| Function | Description |
|----------|-------------|
| `accuracy_score(y_true, y_pred)` | Accuracy |
| `precision_score(y_true, y_pred)` | Precision |
| `recall_score(y_true, y_pred)` | Recall |
| `f1_score(y_true, y_pred)` | F1 score |
| `confusion_matrix(y_true, y_pred)` | Confusion matrix |
| `classification_report(y_true, y_pred)` | Full report |
| `roc_auc_score(y_true, y_scores)` | ROC AUC |

### Evaluation - Regression

| Function | Description |
|----------|-------------|
| `mean_squared_error(y_true, y_pred)` | MSE |
| `root_mean_squared_error(y_true, y_pred)` | RMSE |
| `mean_absolute_error(y_true, y_pred)` | MAE |
| `r2_score(y_true, y_pred)` | R² |

### Cross-Validation

| Function | Description |
|----------|-------------|
| `cross_validate(model, X, y, cv)` | K-fold CV |
| `grid_search(model, X, y, params, cv)` | Grid search |

### Built-in Datasets

| Function | Description |
|----------|-------------|
| `load_iris_dataset()` | Iris flowers |
| `load_wine_dataset()` | Wine classification |
| `load_digits_dataset()` | Handwritten digits |
| `make_classification_data(n, f, c)` | Synthetic classification |
| `make_regression_data(n, f)` | Synthetic regression |
| `make_blobs_data(n, centers)` | Clustered blobs |

### Model Persistence

| Function | Description |
|----------|-------------|
| `save_model(model, path)` | Save to file |
| `load_model(path)` | Load from file |

## License

MIT License - Part of the EPL ecosystem.
