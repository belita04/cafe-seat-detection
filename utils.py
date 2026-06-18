def get_box_center(x1, y1, x2, y2):
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def point_in_roi(point, roi):
    px, py = point
    rx1, ry1, rx2, ry2 = roi
    return rx1 <= px <= rx2 and ry1 <= py <= ry2


def box_overlap_ratio(box, roi):
    x1, y1, x2, y2 = box
    rx1, ry1, rx2, ry2 = roi

    inter_x1 = max(x1, rx1)
    inter_y1 = max(y1, ry1)
    inter_x2 = min(x2, rx2)
    inter_y2 = min(y2, ry2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)

    inter_area = inter_w * inter_h
    box_area = max(1, (x2 - x1) * (y2 - y1))

    return inter_area / box_area


def is_object_in_roi(box, roi, min_overlap=0.2):
    x1, y1, x2, y2 = box
    center = get_box_center(x1, y1, x2, y2)

    if point_in_roi(center, roi):
        return True

    return box_overlap_ratio(box, roi) >= min_overlap


IGNORED_SEAT_CLASSES = [
    "chair",
    "table",
    "dining table"
]


def judge_seat_status(objects):
    valid_objects = []

    for obj in objects:
        if obj not in IGNORED_SEAT_CLASSES:
            valid_objects.append(obj)

    if len(valid_objects) > 0:
        return "OCCUPIED"

    return "EMPTY"


def ensure_model_file(model_path, file_id=None):
    import os
    import gdown

    if os.path.exists(model_path):
        return model_path

    if file_id is None or file_id == "" or "여기에_넣기" in file_id:
        raise FileNotFoundError(
            f"모델 파일이 없습니다: {model_path}\n"
            "config.py의 MODEL_FILE_IDS에 Google Drive file id를 넣거나, "
            "models 폴더에 모델 파일을 직접 넣어주세요."
        )

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    url = f"https://drive.google.com/uc?id={file_id}"

    print(f"모델 파일을 다운로드합니다: {model_path}")
    gdown.download(url, model_path, quiet=False)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"모델 다운로드 실패: {model_path}")

    return model_path


def convert_video(input_path, output_path):
    import subprocess

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path
