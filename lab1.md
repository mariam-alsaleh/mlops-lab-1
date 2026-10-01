# Lab 1 - Git, DVC and Data Preparation

## Question 1
`uv init` created the basic Python project files:
- `.python-version`: stores the Python version used by the project.
- `pyproject.toml`: contains project metadata and dependencies.
- `README.md`: project documentation.
- `main.py`: starter Python script.

## Question 2
DVC created:
- `.dvc/`
- `.dvc/config`
- `.dvc/.gitignore`
- `.dvcignore`

These files contain DVC configuration and metadata. The configuration files should be pushed to Git, while DVC cache/data should not.

## Question 3

### Where are the credentials stored?
When using the `--global` option, the DVC credentials are stored in the global DVC configuration for the current user, outside the project repository.

### What are the options other than `--global`?
DVC can also store configuration at different scopes, including:
- repository-level configuration
- local configuration specific to the current repository

### Should the credentials be pushed to GitHub?
No. Credentials such as usernames, passwords, and access tokens are sensitive information and should not be committed or pushed to GitHub.

Only the non-secret DVC configuration, such as the remote name and remote URL stored in `.dvc/config`, should be tracked with Git.

## Question 4

After running `dvc add data`, DVC modified `.gitignore` so that the actual `data/` directory is ignored by Git.

This prevents the large dataset files from being committed directly to Git. Instead, Git tracks the DVC metadata file while DVC manages the actual dataset.

## Question 5

Yes, a file named `data.dvc` was created.

It contains metadata describing the tracked `data` directory, including information such as its hash/checksum and size. This file acts as a pointer to the version of the dataset managed by DVC.

The `data.dvc` file should be committed to Git, while the actual dataset is stored by DVC.

## DVC Remote Solution

I initially configured DagsHub as the DVC remote and attempted to push the Food-11 dataset. However, the upload failed because a large number of files could not be transferred.

As permitted by the lab instructions, I used a local DVC remote instead.

The local remote was created outside the Git repository:

`/Users/mariam/dvc-storage/mlops-lab-1`

It was configured using:

```bash
dvc remote add -d localremote /Users/mariam/dvc-storage/mlops-lab-1
```

## Question 6

On GitHub, the project code and DVC metadata files are visible, including files such as `data.dvc`, `.dvc/config`, and `.gitignore`.

The actual dataset files are not stored in GitHub because the `data/` folder is ignored by Git and managed by DVC.

The `data.dvc` file acts as a pointer to the version of the dataset being tracked by DVC.

In my setup, the actual dataset is stored in the configured local DVC remote instead of DagsHub because the DagsHub upload failed for the large dataset.

## Question 7

After cloning the GitHub repository into a new folder, the project files and DVC pointer files were present, but the actual dataset was not restored automatically.

The DVC command needed to retrieve the dataset is:

```bash
dvc pull