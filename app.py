import tempfile
from pathlib import Path

import streamlit as st

from config import MODEL_REGISTRY, DEFAULT_SEAT_ROIS
from inference import process_video
from utils import convert_video


st.set_page_config(
    page_title="카페 빈자리 감지 시스템",
    layout="wide"
)

st.title("실시간 카페 빈자리 감지 시스템")
st.write("YOLOv8 객체 탐지 결과를 내부적으로 활용하고, 좌석 ROI와 EMPTY / OCCUPIED 결과를 시각화합니다.")

st.sidebar.header("설정")

model_label = st.sidebar.selectbox(
    "파인튜닝 모델 선택",
    list(MODEL_REGISTRY.keys()),
    help="Baseline과 고도화 모델 중 사용할 커스텀 탐지 모델을 선택합니다."
)

base_conf = st.sidebar.slider(
    "Base YOLO Confidence",
    0.01,
    1.0,
    0.25,
    0.01,
    help="기본 YOLO 객체 탐지 confidence threshold입니다."
)

custom_conf = st.sidebar.slider(
    "Custom YOLO Confidence",
    0.01,
    1.0,
    0.05,
    0.01,
    help="커스텀 객체 탐지 confidence threshold입니다."
)

nms_iou = st.sidebar.slider(
    "NMS IoU Threshold",
    0.10,
    0.90,
    0.60,
    0.05,
    help="중복 Bounding Box 제거 기준입니다."
)

min_overlap = st.sidebar.slider(
    "ROI Overlap Threshold",
    0.05,
    0.80,
    0.20,
    0.05,
    help="객체 박스가 ROI와 얼마나 겹쳐야 좌석 포함으로 볼지 결정합니다."
)

frame_interval = st.sidebar.slider(
    "Frame Analysis Interval",
    1,
    10,
    5,
    1,
    help="몇 프레임마다 한 번씩 YOLO 분석을 수행할지 정합니다. 값이 클수록 빠르지만 상태 변화 반응이 느려집니다."
)

use_custom_model = st.sidebar.checkbox(
    "커스텀 모델 사용",
    value=True,
    help="끄면 기본 YOLO만 사용하므로 더 빠르지만, cup/tumbler/bag 같은 커스텀 객체 반영이 줄어듭니다."
)

st.sidebar.write("현재 좌석 ROI 개수:", len(DEFAULT_SEAT_ROIS))
st.sidebar.caption("좌석 판단 기준: chair/table 제외, 그 외 객체가 ROI 안에 있으면 OCCUPIED")

uploaded_video = st.file_uploader(
    "분석할 영상을 업로드하세요",
    type=["mp4", "avi", "mov", "mkv"]
)

if uploaded_video is None:
    st.info("영상을 업로드하면 좌석 EMPTY / OCCUPIED 분석을 실행할 수 있습니다.")
    st.stop()

try:
    suffix = Path(uploaded_video.name).suffix

    if suffix == "":
        suffix = ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_video.read())
        input_path = tmp.name

    output_raw = input_path + "_result.mp4"
    output_converted = input_path + "_result_converted.mp4"

    with st.spinner("영상 분석 중입니다. 영상 길이에 따라 시간이 걸릴 수 있습니다."):
        result = process_video(
            video_path=input_path,
            output_path=output_raw,
            custom_model_path=MODEL_REGISTRY[model_label],
            model_label=model_label,
            seat_rois=DEFAULT_SEAT_ROIS,
            base_conf=base_conf,
            custom_conf=custom_conf,
            base_iou=nms_iou,
            custom_iou=nms_iou,
            min_overlap=min_overlap,
            frame_interval=frame_interval,
            use_custom_model=use_custom_model
        )

        convert_video(output_raw, output_converted)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("EMPTY", result["empty_count"])
    col2.metric("OCCUPIED", result["occupied_count"])
    col3.metric("Analyzed Frames", result["analyzed_frame_count"])
    col4.metric("FPS", f"{result['processing_fps']:.2f}")

    st.video(output_converted)

    with open(output_converted, "rb") as f:
        st.download_button(
            "결과 영상 다운로드",
            data=f,
            file_name="seat_detection_result.mp4",
            mime="video/mp4"
        )

except Exception as e:
    st.error("영상 처리 중 오류가 발생했습니다. 파일 형식 또는 모델 경로를 확인하세요.")
    st.exception(e)
