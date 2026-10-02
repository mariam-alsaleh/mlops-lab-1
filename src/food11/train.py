import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights


# ---------------------------------------------------------
# MLflow setup
# ---------------------------------------------------------

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("food11")


# ---------------------------------------------------------
# Command-line arguments
# ---------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        choices=["processed", "mini"],
        default="mini",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
    )

    return parser.parse_args()


# ---------------------------------------------------------
# Dataset
# ---------------------------------------------------------

def get_dataloaders(dataset_name, batch_size):
    if dataset_name == "mini":
        data_dir = Path("data/food11_processed_mini")
    else:
        data_dir = Path("data/food11_processed")

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    train_dataset = datasets.ImageFolder(
        data_dir / "training",
        transform=transform,
    )

    val_dataset = datasets.ImageFolder(
        data_dir / "validation",
        transform=transform,
    )

    test_dataset = datasets.ImageFolder(
        data_dir / "evaluation",
        transform=transform,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    return train_loader, val_loader, test_loader


# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

def build_model():
    weights = ResNet18_Weights.DEFAULT

    model = resnet18(weights=weights)

    # ResNet18 normally outputs 1000 ImageNet classes.
    # Food-11 requires 11 output classes.
    model.fc = nn.Linear(
        model.fc.in_features,
        11,
    )

    return model


# ---------------------------------------------------------
# Training
# ---------------------------------------------------------

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()

    total_loss = 0.0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)

    return total_loss / len(loader.dataset)


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    avg_loss = total_loss / len(loader.dataset)
    accuracy = correct / total

    return avg_loss, accuracy


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    args = parse_args()

    # Device selection
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    train_loader, val_loader, test_loader = get_dataloaders(
        args.dataset,
        args.batch_size,
    )

    model = build_model().to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    with mlflow.start_run():

        # -----------------------------
        # Log parameters once
        # -----------------------------

        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "num_classes": 11,
                "device": str(device),
            }
        )

        # -----------------------------
        # Training loop
        # -----------------------------

        for epoch in range(args.epochs):

            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Accuracy: {val_accuracy:.4f}"
            )

            # Log metrics every epoch
            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

        # -----------------------------
        # Final test evaluation
        # -----------------------------

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        print(f"Test Accuracy: {test_accuracy:.4f}")

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        # -----------------------------
        # Save model to MLflow
        # -----------------------------

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle",
        )


if __name__ == "__main__":
    main()