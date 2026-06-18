MODEL_REGISTRY = {
    "Baseline YOLOv8n 640": "models/best_v1_baseline.pt",
    "Enhanced YOLOv8s 640": "models/best_v2_enhanced.pt"
}

# Google Drive 공유 링크에서 file id만 넣기
# 예: https://drive.google.com/file/d/1ABCDEF12345/view?usp=sharing
# file id = 1ABCDEF12345
MODEL_FILE_IDS = {
    "models/best_v1_baseline.pt": "1norbFUQwlGKDEu-3YKkMMOCcAK0u4tyF",
    "models/best_v2_enhanced.pt": "1AUGkHjhjBSDTofv5kpZ2HpDtzAh5eEDg"
}

DEFAULT_SEAT_ROIS = {
    "seat_1":  (90, 400, 270, 530),
    "seat_2":  (280, 350, 600, 580),
    "seat_3":  (660, 500, 840, 600),
    "seat_4":  (60, 540, 270, 820),
    "seat_5":  (280, 600, 460, 820),
    "seat_6":  (660, 620, 950, 850),
    "seat_7":  (820, 570, 1000, 700),
    "seat_8":  (950, 450, 1220, 820),
    "seat_9":  (1300, 300, 1900, 900),
}
