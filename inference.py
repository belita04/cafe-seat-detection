import time
import cv2
import streamlit as st
import torch
from ultralytics import YOLO

from config import MODEL_FILE_IDS
from utils import is_object_in_roi, judge_seat_status, ensure_model_file


@st.cache_resource
def load_base_model():
    return YOLO("yolov8n.pt")


@st.cache_resource
def load_custom_model(model_path):
    file_id = MODEL_FILE_IDS.get(model_path)
    model_path = ensure_model_file(model_path, file_id)
    return YOLO(model_path)


def process_video(
    video_path,
    output_path,
    custom_model_path,
    model_label,
    seat_rois,
    base_conf=0.25,
    custom_conf=0.05,
    base_iou=0.60,
    custom_iou=0.60,
    min_overlap=0.2,
    frame_interval=5,
    use_custom_model=True
):
    base_model = load_base_model()

    if use_custom_model:
        custom_model = load_custom_model(custom_model_path)
    else:
        custom_model = None

    device = 0 if torch.cuda.is_available() else "cpu"
    use_half = True if torch.cuda.is_available() else False

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("영상을 열 수 없습니다. 파일 형식을 확인하세요.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        fps = 30

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    analyzed_frame_count = 0
    start = time.time()

    last_empty = 0
    last_occupied = 0

    last_status_by_seat = {
        seat_id: "EMPTY" for seat_id in seat_rois.keys()
    }

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        should_analyze = (frame_count == 1) or (frame_count % frame_interval == 0)

        if should_analyze:
            analyzed_frame_count += 1
            seat_objects = {seat_id: [] for seat_id in seat_rois.keys()}

            base_results = base_model.predict(
                frame,
                imgsz=640,
                conf=base_conf,
                iou=base_iou,
                device=device,
                half=use_half,
                verbose=False
            )

            for result in base_results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    cls_name = base_model.names[cls_id]

                    object_box = (x1, y1, x2, y2)

                    for seat_id, roi in seat_rois.items():
                        if is_object_in_roi(object_box, roi, min_overlap):
                            seat_objects[seat_id].append(cls_name)

            if use_custom_model and custom_model is not None:
                custom_results = custom_model.predict(
                    frame,
                    imgsz=640,
                    conf=custom_conf,
                    iou=custom_iou,
                    device=device,
                    half=use_half,
                    verbose=False
                )

                for result in custom_results:
                    if result.boxes is None:
                        continue

                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls_id = int(box.cls[0])
                        cls_name = custom_model.names[cls_id]

                        object_box = (x1, y1, x2, y2)

                        for seat_id, roi in seat_rois.items():
                            if is_object_in_roi(object_box, roi, min_overlap):
                                seat_objects[seat_id].append(cls_name)

            for seat_id in seat_rois.keys():
                last_status_by_seat[seat_id] = judge_seat_status(
                    seat_objects[seat_id]
                )

        empty_count = 0
        occupied_count = 0

        for seat_id, roi in seat_rois.items():
            status = last_status_by_seat[seat_id]

            x1, y1, x2, y2 = roi

            if status == "OCCUPIED":
                color = (0, 0, 255)
                occupied_count += 1
            else:
                color = (0, 255, 0)
                empty_count += 1

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)

            cv2.putText(
                frame,
                f"{seat_id}: {status}",
                (x1, min(y2 + 22, height - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2
            )

        last_empty = empty_count
        last_occupied = occupied_count

        summary = (
            f"{model_label} | EMPTY: {empty_count}  OCCUPIED: {occupied_count} "
            f"| Analyze every {frame_interval} frames"
        )

        cv2.putText(
            frame,
            summary,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        out.write(frame)

    cap.release()
    out.release()

    elapsed = time.time() - start
    processing_fps = frame_count / elapsed if elapsed > 0 else 0
    latency_ms = elapsed / frame_count * 1000 if frame_count > 0 else 0

    return {
        "output_path": output_path,
        "frame_count": frame_count,
        "analyzed_frame_count": analyzed_frame_count,
        "processing_fps": processing_fps,
        "latency_ms_per_frame": latency_ms,
        "empty_count": last_empty,
        "occupied_count": last_occupied
    }
