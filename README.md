# 🚗 텔레칩스 부트캠프 프로젝트
사고 예방 운전 보조 시스템 (ADAS Prototype)

본 프로젝트는 차량 센서 데이터와 영상 처리를 기반으로
차로 유지 및 충돌 방지 기능을 구현하고,
범용 보드 환경에서 차량용 AI 플랫폼으로 포팅 및 최적화한 프로젝트입니다.

- 1차: STM32 + Raspberry Pi 기반 구현
- 2차: Telechips AI 보드 기반 포팅 및 최적화

---

# 📌 1차 프로젝트 — STM32 + Raspberry Pi 기반 구현

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

## 8. 코드
- `lane_detection` : 차로 유지 기능
- `button` : 버튼 드라이버

---

# 🚀 2차 프로젝트 — Telechips AI 보드 포팅 및 최적화

1차 프로젝트에서 구현한 시스템을
차량용 AI 플랫폼 환경으로 이식하고 실시간 성능을 개선했습니다.

---

## 1. 시스템 아키텍처 (직접 개발 영역 표시)
<img width="1072" height="491" src="https://github.com/user-attachments/assets/00399124-4fde-41c9-8195-0f54f66ec349" />

- 기존 구조 → Telechips 보드 환경 포팅
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

## 4. 코드
- `mcb` : 충돌 방지 시스템
- `lane_detection_v2` : 딥러닝 기반 차선 인식

---

# 🧠 프로젝트 성과

- 임베디드 시스템 설계 및 구현 경험 확보
- 영상 기반 차선 인식 알고리즘 구현
- 시스템 포팅 및 성능 개선 경험
- 실시간 처리 시스템 구조 이해

---

# 🛠 기술 스택

- Embedded System
- Linux
- OpenCV
- TCP/IP 통신
- GPIO Driver
- 영상 처리
- 딥러닝 기반 차선 인식



 
