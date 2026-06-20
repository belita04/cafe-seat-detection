# 실시간 카페 빈자리 감지 시스템

## 1. 프로젝트 소개

본 프로젝트는 카페 좌석 영역을 ROI로 지정하고, YOLOv8 객체 탐지 결과를 기반으로 좌석별 EMPTY / OCCUPIED 상태를 분석하는 웹 애플리케이션입니다.

## 2. 주요 기능

- 동영상 파일 업로드 기반 좌석 분석
- YOLOv8 기반 객체 탐지
- ROI 기반 좌석별 EMPTY / OCCUPIED 판단
- Baseline 모델과 Enhanced 모델 선택 기능
- Confidence threshold, NMS IoU, ROI overlap threshold 등 조정 기능
- 프레임 간격 기반 빠른 영상 분석
- 분석 결과 영상 출력 및 다운로드

## 3. 개발 환경 및 의존성

- Python 3.x
- Streamlit
- Ultralytics YOLOv8
- OpenCV
- NumPy
- Pandas
- PyYAML
- gdown

## 4. 설치 및 실행 방법

아래 순서로 코드를 실행합니다.(실행 시 들여쓰기를 주의하세요)

1. 저장소 복제

   %cd /content
   
   !rm -rf cafe-seat-detection
   
   !git clone https://github.com/belita04/cafe-seat-detection.git

3. 프로젝트 폴더로 이동
   

   %cd cafe-seat-detection


4. 패키지 설치

   !pip install -r requirements.txt

5. Streamlit 앱 실행

!pkill -f streamlit || true

!pkill -f cloudflared || true

!pkill -f localtunnel || true

!sleep 2

!fuser -k 8501/tcp || true

!sleep 2

```bash
!streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    > /content/streamlit_test_log.txt 2>&1 &

!sleep 5
!cat /content/streamlit_test_log.txt
```



6. Cloudflare Tunnel 주소 만들기


   Cloudflare Tunnel 설치
   
   !wget -q -O /content/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   
   !chmod +x /content/cloudflared
   
   Streamlit 앱 외부 접속 링크 생성
   
   !/content/cloudflared tunnel --url http://127.0.0.1:8501 --no-autoupdate

## 5. 모델 가중치 처리 방법

GitHub는 100MB를 초과하는 대용량 파일 업로드를 제한하므로 모델 가중치 파일은 Google Drive에 별도로 저장합니다.
- Google Drive 주소: https://drive.google.com/drive/folders/1PKKavRkXLQZrpYc8EPXXjFkbfmKx_f9K?usp=sharing
- Baseline 모델: best_v1_baseline.pt
- Enhanced 모델: best_v2_enhanced.pt

앱 실행 시 models 폴더에 모델 파일이 없으면 config.py의 Google Drive file ID를 이용하여 자동 다운로드됩니다.

직접 다운로드하는 경우 아래 경로에 저장합니다.

models/best_v1_baseline.pt
models/best_v2_enhanced.pt

## 6. 데이터 파이프라인

1. 카페 환경 이미지 수집 및 Roboflow 라벨링
2. YOLOv8 형식 데이터셋 생성
3. Baseline 모델 학습
4. Enhanced 모델 학습
5. mAP50, mAP50-95, FPS, Latency 기반 성능 비교
6. Streamlit 웹 앱 연동
7. 동영상 업로드 기반 좌석 ROI 분석
8. EMPTY / OCCUPIED 결과 영상 생성

## 7. 좌석 판단 기준

좌석 ROI 내부에 탐지된 객체를 기준으로 좌석 상태를 판단합니다.

단, chair, table, dining table은 카페 공간에 기본적으로 존재할 수 있는 객체이므로 좌석 점유 판단에서 제외합니다.

따라서 ROI 내부에 person, cup, bag, tumbler, charger, device, outerwear, stationery 등 기타 객체가 하나라도 탐지되면 OCCUPIED로 판단하고, 제외 객체만 존재하거나 객체가 없으면 EMPTY로 판단합니다.

## 8. 실행 화면

- Streamlit 메인 화면

  <img width="2878" height="1520" alt="Streamlit 메인화면" src="https://github.com/user-attachments/assets/ff5ebd85-9f00-4f50-aadf-07725ec4e2d5" />

- 영상 업로드 화면

  <img width="1034" height="188" alt="영상 업로드 화면" src="https://github.com/user-attachments/assets/11fdebec-e0f5-460e-8b99-013842e18990" />

- 좌석 EMPTY / OCCUPIED 분석 결과 화면

  <img width="2230" height="1498" alt="실행화면" src="https://github.com/user-attachments/assets/8c025496-d93e-406b-b851-318b9cca2f84" />


## 9. 팀원별 역할 분담

- 데이터셋 구축 및 라벨링: 이명진/ 이지민
- Baseline 모델 학습: 이지민
- Enhanced 모델 고도화: 이명진
- Streamlit UI 구현: 이명진
- 성능 평가 및 Failure Case 분석: 이지민
- 보고서 작성: 이명진
- 발표 자료 준비: 이지민
- 발표: 이명진
