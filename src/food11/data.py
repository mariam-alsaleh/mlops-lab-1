from pathlib import Path
from PIL import Image
import shutil

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100

CLASS_NAMES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

SPLITS = ["training", "evaluation", "validation"]


def reset_folder(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def process():
    reset_folder(PROCESSED_DIR)
    reset_folder(MINI_DIR)

    for split in SPLITS:
        source_dir = RAW_DIR / split

        if not source_dir.exists():
            print(f"Missing split: {source_dir}")
            continue

        mini_counts = {name: 0 for name in CLASS_NAMES.values()}

        for image_path in source_dir.iterdir():
            if not image_path.is_file():
                continue

            class_id = image_path.name.split("_")[0]

            if class_id not in CLASS_NAMES:
                print(f"Skipping unknown file: {image_path.name}")
                continue

            class_name = CLASS_NAMES[class_id]

            processed_class = PROCESSED_DIR / split / class_name
            mini_class = MINI_DIR / split / class_name

            processed_class.mkdir(parents=True, exist_ok=True)
            mini_class.mkdir(parents=True, exist_ok=True)

            try:
                with Image.open(image_path) as img:
                    img = img.convert("RGB")
                    img = img.resize(IMAGE_SIZE)

                    img.save(processed_class / image_path.name)

                    if mini_counts[class_name] < MINI_LIMIT:
                        img.save(mini_class / image_path.name)
                        mini_counts[class_name] += 1

            except Exception as e:
                print(f"Error processing {image_path.name}: {e}")

        print(f"Finished {split}")

    print("Processing complete.")


if __name__ == "__main__":
    process()