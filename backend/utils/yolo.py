import os, shutil
from typing import List, Dict, Tuple

def validate_yolo_structure(base_path: str):
    def exists(p): return os.path.isdir(os.path.join(base_path, p))

    groups = {
        "train": exists("train/images") and exists("train/labels"),
        "valid": exists("valid/images") and exists("valid/labels"),
        "test": exists("test/images") and exists("test/labels"),
    }

    if not any(groups.values()):
        raise ValueError(
            "At least one of the following directory groups must exist:\n"
            "- train/images + train/labels\n"
            "- valid/images + valid/labels\n"
            "- test/images + test/labels"
        )


def parse_labels(base_path: str, dataset_name: str) -> Tuple[List[str], Dict[str, List[Dict[str, str]]]]:
    groups = ["train", "valid", "test"]
    image_extensions = (".jpg", ".jpeg", ".png")

    all_images: List[str] = []
    label_dict: Dict[str, List[Dict[str, str]]] = {}

    output_dir = os.path.join("datasets", "images", dataset_name)
    os.makedirs(output_dir, exist_ok=True)

    for group in groups:
        images_path = os.path.join(base_path, group, "images")
        labels_path = os.path.join(base_path, group, "labels")

        if not os.path.isdir(images_path) or not os.path.isdir(labels_path):
            continue

        for img_file in os.listdir(images_path):
            if not img_file.lower().endswith(image_extensions):
                continue

            img_path = os.path.join(images_path, img_file)
            label_file = os.path.join(labels_path, os.path.splitext(img_file)[0] + ".txt")

            # Add label data
            label_data = []
            if os.path.exists(label_file):
                with open(label_file, "r") as lf:
                    for line in lf:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            cls, x, y, w, h = parts
                            label_data.append({"class": cls, "bbox": [x, y, w, h]})

            all_images.append(img_path)
            label_dict[os.path.basename(img_path)] = label_data

            dest_img_path = os.path.join(output_dir, img_file)
            if not os.path.exists(dest_img_path):
                shutil.copy(img_path, dest_img_path)

    return all_images, label_dict
