# -*- coding: utf-8 -*-
"""Assignment2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IeUHx5fL5Eg2PcCJV0buhjTaLGwovBiB
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Load dataset
df = pd.read_csv('/content/drive/MyDrive/train (1).csv')

# Check for missing values
print(df.isnull().sum())

# Fill missing values in the 'salary' column with the median
df['salary'] = df['salary'].fillna(df['salary'].median())

# Encode categorical features
label_encoder = LabelEncoder()
categorical_columns = ['ssc_b', 'hsc_b', 'hsc_s', 'degree_t', 'workex', 'specialisation', 'status']
for column in categorical_columns:
    df[column] = label_encoder.fit_transform(df[column])

# Display the encoded dataset
print(df.head())

# Splitting the data into features and target variable
X_train = df.drop(columns=['sl_no', 'status', 'salary'])
y_train = df['status']

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Splitting the data into training and validation sets
X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(X_train_scaled, y_train, test_size=0.3, random_state=42)

# Define parameter grids for hyperparameter tuning
param_grid_rf = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}

param_grid_lr = {
    'C': [0.1, 1, 10],
    'solver': ['lbfgs', 'liblinear']
}

param_grid_svc = {
    'C': [0.1, 1, 10],
    'kernel': ['linear', 'rbf']
}

param_grid_dt = {
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}

param_grid_gb = {
    'n_estimators': [100, 200],
    'learning_rate': [0.05, 0.1, 0.2],
    'max_depth': [3, 4, 5]
}

param_grid_ab = {
    'n_estimators': [50, 100, 200],
    'learning_rate': [0.01, 0.1, 1]
}

# Initialize models
rf_model = RandomForestClassifier(random_state=42)
lr_model = LogisticRegression(random_state=42, max_iter=1000)
svc_model = SVC(random_state=42)
dt_model = DecisionTreeClassifier(random_state=42)
gb_model = GradientBoostingClassifier(random_state=42)
ab_model = AdaBoostClassifier(random_state=42)

# Perform hyperparameter tuning using GridSearchCV
rf_grid = GridSearchCV(rf_model, param_grid_rf, cv=5, scoring='f1')
lr_grid = GridSearchCV(lr_model, param_grid_lr, cv=5, scoring='f1')
svc_grid = GridSearchCV(svc_model, param_grid_svc, cv=5, scoring='f1')
dt_grid = GridSearchCV(dt_model, param_grid_dt, cv=5, scoring='f1')
gb_grid = GridSearchCV(gb_model, param_grid_gb, cv=5, scoring='f1')
ab_grid = GridSearchCV(ab_model, param_grid_ab, cv=5, scoring='f1')

# Fit the models with training data
rf_grid.fit(X_train_split, y_train_split)
lr_grid.fit(X_train_split, y_train_split)
svc_grid.fit(X_train_split, y_train_split)
dt_grid.fit(X_train_split, y_train_split)
gb_grid.fit(X_train_split, y_train_split)
ab_grid.fit(X_train_split, y_train_split)

# Get the best estimators from GridSearchCV
rf_best = rf_grid.best_estimator_
lr_best = lr_grid.best_estimator_
svc_best = svc_grid.best_estimator_
dt_best = dt_grid.best_estimator_
gb_best = gb_grid.best_estimator_
ab_best = ab_grid.best_estimator_

# Define a function to evaluate models on validation data
def evaluate_model(model, X_val, y_val):
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)
    cm = confusion_matrix(y_val, y_pred)
    return accuracy, precision, recall, f1, cm

# Evaluate each model on validation set and print metrics
models = {
    'Random Forest': rf_best,
    'Logistic Regression': lr_best,
    'SVC': svc_best,
    'Decision Tree': dt_best,
    'Gradient Boosting': gb_best,
    'AdaBoost': ab_best
}

results = {}
for model_name, model in models.items():
    accuracy, precision, recall, f1, cm = evaluate_model(model, X_val_split, y_val_split)
    results[model_name] = (accuracy, precision, recall, f1, cm)
    print(f"{model_name}: Accuracy={accuracy}, Precision={precision}, Recall={recall}, F1-score={f1}")
    print(f"Confusion Matrix:\n{cm}")

# Visualize the results using bar plots
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-score']
for metric in metrics:
    metric_values = [results[model_name][metrics.index(metric)] for model_name in models]
    plt.figure(figsize=(10, 5))
    plt.bar(models.keys(), metric_values, color=['blue', 'green', 'red', 'purple', 'orange', 'cyan'])
    plt.title(f'Model Comparison - {metric}')
    plt.xlabel('Models')
    plt.ylabel(metric)
    plt.ylim(0, 1)
    for i, v in enumerate(metric_values):
        plt.text(i, v + 0.02, f'{v:.2f}', ha='center')
    plt.show()

# Voting Classifier
# Ensemble model using VotingClassifier
voting_clf = VotingClassifier(estimators=[
    ('rf', rf_best),
    ('lr', lr_best),
    ('svc', svc_best),
    ('dt', dt_best),
    ('gb', gb_best),
    ('ab', ab_best)
], voting='hard')

# Fit the Voting Classifier on training data
voting_clf.fit(X_train_split, y_train_split)

# Evaluate the Voting Classifier on validation data and print metrics
voting_accuracy, voting_precision, voting_recall, voting_f1, voting_cm = evaluate_model(voting_clf, X_val_split, y_val_split)
print(f"Voting Classifier: Accuracy={voting_accuracy}, Precision={voting_precision}, Recall={voting_recall}, F1-score={voting_f1}")
print(f"Confusion Matrix:\n{voting_cm}")

# Visualize the performance of the Voting Classifier
voting_metrics = [voting_accuracy, voting_precision, voting_recall, voting_f1]
plt.figure(figsize=(10, 5))
plt.bar(metrics, voting_metrics, color='magenta')
plt.title('Voting Classifier Performance')
plt.xlabel('Metrics')
plt.ylabel('Score')
plt.ylim(0, 1)
for i, v in enumerate(voting_metrics):
    plt.text(i, v + 0.02, f'{v:.2f}', ha='center')
plt.show()

# Prepare the final model for deployment (assuming X_test is available separately)
final_model = voting_clf
# Predict on the entire dataset (as test set is not provided separately)
final_predictions = final_model.predict(X_scaled)

# Prepare submission format if needed
submission_df = pd.DataFrame({
    'Id': df['sl_no'],
    'Status': final_predictions
})

# Save the submission file
submission_df.to_csv('submission.csv', index=False)
print("Submission file created successfully!")