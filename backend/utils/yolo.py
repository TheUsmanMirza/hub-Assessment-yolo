import os

def parse_yolo_annotations(root_path):
    images = []
    for sub in ["labels/train", "labels/val", "labels", 'train/labels', 'valid/labels']:
        dirpath = os.path.join(root_path, sub)
        if not os.path.isdir(dirpath): continue
        for txt in os.listdir(dirpath):
            if not txt.endswith(".txt"): continue
            img = txt.replace(".txt", ".jpg")
            labels = []
            with open(os.path.join(dirpath, txt)) as f:
                for ln in f:
                    cls, x, y, w, h = ln.strip().split()
                    labels.append({"class": int(cls), "bbox": [float(x), float(y), float(w), float(h)]})
            images.append({"image_name": img, "labels": labels})
    return images