## Question 1

The registered model was given version `1`.

A run's logged model artifact is the model file/output saved as part of one specific MLflow training run.

A registered model is a named, versioned model in the MLflow Model Registry. It can point to model artifacts from different runs over time and allows versions and aliases to be managed independently of the original training run.

## Question 2

MLflow now uses model aliases instead of the old built-in stages such as `Staging` and `Production`.

Examples of aliases include:
- `champion`
- `challenger`

A model is versioned separately from the run that produced it because the same registered model name can have multiple versions created from different training runs. This makes it easier to manage the lifecycle of the model independently from the experiment history.

An alias is more flexible than a fixed stage because it is a mutable pointer to a specific model version. For example, the `champion` alias can be reassigned from version 1 to version 2 without renaming or changing the model version itself.

## Question 3

Using the MLflow model URI `models:/food11@champion` decouples the serving code from a specific model file and model version.

The serving application only refers to the registered model name and alias. MLflow resolves the alias to the correct registered model version and loads its artifacts.

To serve a newer model version, I would register the newer version and reassign the `champion` alias to it. The serving code itself would not need to change because it still loads `models:/food11@champion`.

## Question 4

`pyproject.toml` and `uv.lock` are copied before the source code so Docker can cache the dependency-installation layer.

Dependencies usually change less often than application source code. If only `serve.py` changes, Docker can reuse the cached dependency layer and only rebuild the later source-code layers.

If all files were copied before running `uv sync`, even a small source-code change would invalidate the cache and force all dependencies to be installed again.

## Question 6

Without a `.dockerignore`, Docker sends unnecessary files to the build context, which increases build time and can make the image larger if those files are copied into the image.

Folders such as `.venv/`, `data/`, `mlruns/`, and `.git/` are not needed for the application image.

Some of these folders can also cause problems:
- `.venv/` may contain binaries built for the host system and should not be copied into the container.
- `data/` and `mlruns/` can make the build context extremely large.
- `.git/` adds unnecessary metadata.
- `mlflow.db` is local tracking state and should not be bundled into the image.

## Question 5

The built `food11-api:latest` image had:

- Disk usage: approximately `1.87 GB`
- Content size: approximately `386 MB`

Using:

```bash
docker history food11-api:latest
```

## Question 8

After stopping the first container and starting a new container from the same Docker image, the API still worked without rebuilding the image.

The health endpoint returned:

`{"status":"ok"}`

and the prediction endpoint returned:

`{"category":"Bread","confidence":0.9262181520462036}`

This shows that the Docker image contains the serving application and its dependencies, while the model itself is resolved and loaded at runtime through MLflow using:

`models:/food11@champion`

The registered model artifact is therefore not baked directly into the image. The container loads the current `champion` model when it starts.

## Question 9

The `Dockerfile` is versioned in Git, but the Docker image itself is only stored locally on the machine where it was built.

Before another machine, CI runner, or Kubernetes cluster could reliably run the exact same image, the image would need to be pushed to a container registry such as Docker Hub, GitHub Container Registry, or another OCI-compatible registry.

The image should also be tagged with a stable version or immutable digest rather than relying only on the `latest` tag. This would allow other systems to pull and run the exact same built image.