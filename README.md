#  텔레칩스 부트캠프 프로젝트
사고 예방 운전 보조 시스템 (ADAS Prototype)

- 1차: STM32 + Raspberry Pi 기반 구현
--  STM32: 센서 데이터 수집 및 제어 처리
-- Raspberry Pi: 영상 처리 및 상위 제어 로직 수행
---
- 2차: Telechips 보드 기반 포팅 및 최적화

---

#  1차 프로젝트 — STM32 + Raspberry Pi 기반 구현

## 1. 유스케이스 시나리오
<img width="985" height="388" src="https://github.com/user-attachments/assets/bc462d2a-0c2e-4e81-8014-6973a5c854c2" />

---

## 2. 요구사항 정의
<img width="1090" height="465" src="https://github.com/user-attachments/assets/593c3bc7-1fc3-4fc5-8737-0d059109f232" />

---

## 3. 시스템 아키텍처 (직접 개발 영역 표시)
<img width="1058" height="498" src="https://github.com/user-attachments/assets/b823b7ef-0880-43d5-949d-f5e5d37a5ceb" />

- 빨간 박스 영역 직접 구현
- 센서 데이터 수집 및 처리 구조 설계
- 시스템 간 데이터 흐름 구성

---

## 4. 데모 환경
<img width="1026" height="465" src="https://github.com/user-attachments/assets/7f6f1c3c-b405-4f92-8b03-c440828151b2" />

---

## 5. 세부 개발 내용

### 5-1. 차로 유지 기능
- Hardware: Raspberry Pi 4
- 기술: OpenCV, Ethernet TCP Protocol
- 영상 기반 차선 인식 및 제어 로직 구현

### 5-2. 1602 LCD Display
- 센서 수집 데이터 실시간 표시
- LCD 제어 코드 작성

### 5-3. Button Driver
- Raspberry Pi GPIO 기반 버튼 드라이버 구현

---

## 6. 시스템 동작 플로우차트
<img width="305" height="582" src="https://github.com/user-attachments/assets/39ea70e2-78ef-4507-9a7b-d8cb1aa1b0b8" />

---

## 7. 실행 결과
<img width="1003" height="477" src="https://github.com/user-attachments/assets/34fa37fb-2f47-4681-b25a-f8c56eec86aa" />
<img width="760" height="392" src="https://github.com/user-attachments/assets/9fb62614-5cd2-44c5-af6b-e69632899ec7" />

---

### 8.1 lane_detection 코드 설명 - 카메라 영상 처리도 가능하나 시연을 위해 도로 주행 동영상 사용 

차량 주행 시 카메라 영상을 입력받아 차선을 검출하고 차량이 차로 중앙을 유지하도록 보조하는 기능을 구현하였다.

영상 처리 과정은 다음 순서로 동작한다.

- 카메라 영상 입력
- Grayscale 변환 및 Gaussian Blur 적용
- Canny Edge Detection 수행
- 관심 영역(ROI) 설정
- Hough Transform을 이용한 차선 검출
- 좌/우 차선 기울기 계산 후 중심선 추정

검출된 차선 정보를 기반으로 차량 위치 편차를 계산하도록 설계하였다.


### 8.2 button 드라이버 코드 설명

Raspberry Pi GPIO를 이용한 버튼 입력 드라이버를 구현하였다.

- GPIO 인터럽트 기반 입력 처리
- 버튼 입력에 따른 시스템 동작 제어
- 디바운싱 처리 적용으로 오동작 방지

센서 데이터 표시 및 기능 ON/OFF 제어에 사용된다.


---

### 8.3 실행 방법

```bash
python lane_detection.py
```

#  2차 프로젝트 — Telechips  보드 포팅 및 최적화

1차 프로젝트에서 구현한 시스템을
차량용 AI 플랫폼 환경으로 이식하고 실시간 성능을 개선했습니다.

---

## 1. 시스템 아키텍처 (직접 개발 영역 표시)
<img width="1072" height="491" src="https://github.com/user-attachments/assets/00399124-4fde-41c9-8195-0f54f66ec349" />

- 기존 구조 → Telechips AI 보드 환경 포팅
- AI 추론 구조 개선
- 실시간 처리 성능 최적화

---

## 2. 세부 개발 내용

### 2-1. 충돌 방지 자동 제동 시스템 (MCB)
- 웹캠 기반 영상 처리
- 충돌 상황 판단 및 제동 로직 구현

### 2-2. UFLD 딥러닝 모델 기반 차선 인식
- 딥러닝 기반 차선 검출
- 실시간 영상 처리 구조 개선

---

## 3. 실행 결과
<img width="802" height="382" src="https://github.com/user-attachments/assets/b144487e-60d1-42e6-b66f-0bcd417984fc" />
<img width="808" height="378" src="https://github.com/user-attachments/assets/615b5d0e-10fd-4f8c-8408-901698831cbf" />
<img width="810" height="390" src="https://github.com/user-attachments/assets/ccafcd57-7cd1-48c0-ad2c-39bd15068a08" />

---

## 4. MCB (충돌 방지 시스템)

- `mcb.cpp` : 운전자 상태 분석 기반 충돌 방지 시스템

### 주요 기능

- 충격 센서(GPIO) 입력 기반 이벤트 트리거 방식 동작
- 카메라 영상 기반 운전자 얼굴 및 눈 상태 분석
- Eye Aspect Ratio(EAR) 알고리즘을 이용한 눈 깜빡임 / 졸음 상태 판단
- 상태 변화 발생 시 CAN 통신으로 차량 제어 시스템에 전달

### 동작 흐름

1. GPIO 충격 센서 입력 대기
2. 충격 감지 시 운전자 상태 분석 모드 활성화
3. 카메라 영상에서 얼굴 검출
4. 얼굴 landmark 기반 눈 영역 추출
5. EAR(Eye Aspect Ratio) 계산
6. 눈 상태 판단 후 CAN 메시지 전송

### 상태 정의

- `1` : 정상 상태 (눈 뜸)
- `2` : 눈 감음 / 졸음 상태 감지
- `3` : 얼굴 미검출 (운전자 부재 가능)

### 기술 요소

- OpenCV 기반 영상 처리
- Dlib facial landmark 검출
- EAR 알고리즘 기반 눈 상태 분석
- GPIO 충격 센서 인터페이스
- Linux SocketCAN 기반 CAN 통신
- 실시간 운전자 상태 모니터링

### 구현 특징

- 충격 발생 시에만 영상 분석 수행하여 시스템 부하 최소화
- 상태 변경 시에만 CAN 메시지 전송하도록 설계
- 임베디드 환경에서 동작 가능한 경량 영상 처리 구조

## 5. lane_detection 설명 (UFLD 기반 차선 인식)

- Telechips AI SDK 환경에서 제공된 UFLD(Ultra Fast Lane Detection) 모델을 사용하여
  딥러닝 기반 차선 인식 기능을 구현

- 카메라 입력 영상 전처리, 모델 추론 실행, 결과 후처리 및 차량 제어 시스템 연동 과정 구현

- NPU 가속 환경에서 실시간 추론 파이프라인 구성 및 성능 테스트 수행

※ 코드 미첨부 사유  
- Telechips 사내 AI SDK 및 실행 환경을 기반으로 동작하는 구조로  
  모델 내부 구현 코드 수정 없이 제공된 툴 환경에서 모델 적용 및 최적화를 수행함

참고 자료  
- 노션 정리: https://halved-engine-6fb.notion.site/AI-G-UFLD-Ultra-Fast-Lane-Detection-28fa6ecfd83980e1850ae089ab9b20dd

---

# 🧠 프로젝트 성과

- 임베디드 시스템 설계 및 구현 경험 확보
- 영상 기반 차선 인식 알고리즘 구현
- 시스템 포팅 및 성능 개선 경험
- 실시간 처리 시스템 구조 이해

---

# 🛠 기술 스택

- C/C++/Python
- Embedded System
- Linux
- OpenCV
- TCP/IP 통신
- GPIO Driver
- 영상 처리
- 딥러닝 기반 차선 인식
- Can 통신

 
