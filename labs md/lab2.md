## Question 1

After installing `mlflow`, `torch`, `torchvision`, and `scikit-learn`, the following files changed:

- `pyproject.toml`: the new libraries were added as project dependencies.
- `uv.lock`: the exact resolved dependency versions and their transitive dependencies were recorded.

`pyproject.toml` describes what the project depends on, while `uv.lock` pins the exact versions used so the same environment can be reproduced.

## Question 4

The first time `mlflow.set_experiment("food11")` is called, MLflow checks whether an experiment with that name already exists.

If it does not exist, MLflow automatically creates a new experiment named `food11` and sets it as the active experiment for subsequent runs.

After running the script, the `food11` experiment appeared in the MLflow UI.

## Question 6

In the MLflow UI, the run contains:

- Parameters such as learning rate, batch size, number of epochs, dataset, model, and device.
- Metric charts for:
  - `train_loss`
  - `val_loss`
  - `val_accuracy`
  - `test_accuracy`
- The trained model under the run artifacts.

The metric charts show how the training and validation values changed across epochs because the metrics were logged with a `step`.

The model artifact is stored locally under the MLflow artifact directory configured when starting the tracking server.

In this lab, the artifact root is:

`./mlruns`

Therefore, the model files are physically stored somewhere under the `mlruns/` directory for that MLflow run.

## Question 7

The learning rate that gave the best validation accuracy was `0.0001`, with a validation accuracy of approximately `0.6953` (69.5%).

A higher learning rate was not always better. In particular, `lr = 0.01` produced the lowest validation accuracy, around `0.1469`.

This shows that increasing the learning rate too much can negatively affect model training and validation performance.

## Question 8

The parallel coordinates plot shows that the learning rate had a strong effect on validation accuracy.

- `lr = 0.0001` with batch size 32 gave the highest validation accuracy, approximately 0.6953.
- `lr = 0.001` gave intermediate validation accuracy.
- `lr = 0.01` gave the lowest validation accuracy, approximately 0.1469.

For `lr = 0.001`, changing the batch size from 32 to 64 caused a smaller change in validation accuracy compared with changing the learning rate.

Therefore, in these runs, the learning rate appears to have had a larger effect on validation performance than the batch size.

## Question 9

After sorting the runs by `val_accuracy` in descending order, the best successful run was:

- Run name: `upset-bass-213`
- Validation accuracy: approximately `0.6953`
- Learning rate: `0.0001`
- Batch size: `32`
- Run ID: `4326428dbd5a4c58a2f751ac1b0a075b`

This Run ID should be kept because it will be needed in the next lab.