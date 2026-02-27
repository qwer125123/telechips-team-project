import cv2
import numpy as np
import socket
import subprocess
import os

# 영상 대비 개선 (조명 영향 줄이려고 사용)
def enhance_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # CLAHE 적용
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    enhanced = cv2.merge((cl, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


# 기본 전처리 (grayscale → blur → edge)
def preprocess(image):
    image = enhance_contrast(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 노이즈 줄이기
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # edge 검출
    edges = cv2.Canny(blur, 30, 100)
    return edges


# 관심 영역만 사용 (도로 부분만)
def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # 화면 아래쪽 중심 영역
    polygon = np.array([[
        (int(0.1 * width), height),
        (int(0.9 * width), height),
        (int(0.55 * width), int(0.6 * height)),
        (int(0.45 * width), int(0.6 * height))
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    return cv2.bitwise_and(edges, mask)


# Hough Transform으로 차선 후보 검출
def detect_lines(cropped_edges):
    return cv2.HoughLinesP(
        cropped_edges,
        rho=1,
        theta=np.pi / 180,
        threshold=30,
        minLineLength=40,
        maxLineGap=100
    )


# 여러 라인 중에서 좌/우 차선 평균
def average_slope_intercept(lines):
    left_lines, right_lines = [], []

    for line in lines:
        for x1, y1, x2, y2 in line:
            if x1 == x2:  # 수직선 제외
                continue

            slope = (y2 - y1) / (x2 - x1)

            # 너무 평평하거나 이상한 라인 제거
            if abs(slope) < 0.5 or abs(slope) > 2:
                continue

            intercept = y1 - slope * x1

            if slope < 0:
                left_lines.append((slope, intercept))
            else:
                right_lines.append((slope, intercept))

    left_avg = np.mean(left_lines, axis=0) if left_lines else None
    right_avg = np.mean(right_lines, axis=0) if right_lines else None

    return left_avg, right_avg


# 기울기/절편 → 실제 좌표 변환
def make_line_points(y1, y2, line):
    if line is None:
        return None

    slope, intercept = line
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return np.array([x1, y1, x2, y2])


# 차량 중심 vs 차선 중심 차이 계산
def compute_offset_normalized(frame_width, left_line, right_line):
    if left_line is None or right_line is None:
        return None

    # 차선 중앙
    mid_x1 = (left_line[0] + right_line[0]) // 2
    mid_x2 = (left_line[2] + right_line[2]) // 2
    lane_center = (mid_x1 + mid_x2) // 2

    # 카메라 위치 보정 (+30)
    frame_center = frame_width // 2 + 30
    raw_offset = lane_center - frame_center

    # 0~100 범위로 변환 (제어값으로 사용)
    normalized = int(((raw_offset + (frame_width // 2)) / frame_width) * 100)
    normalized = max(0, min(normalized, 100))

    return normalized, lane_center, frame_center


# 화면에 차선/중앙선/offset 표시
def display_lines(image, lines, offset_info=None):
    line_image = np.zeros_like(image)
    left_line, right_line = lines

    if left_line is not None:
        cv2.line(line_image, (left_line[0], left_line[1]), (left_line[2], left_line[3]), (0, 255, 0), 8)

    if right_line is not None:
        cv2.line(line_image, (right_line[0], right_line[1]), (right_line[2], right_line[3]), (0, 255, 0), 8)

    # 중앙선
    if left_line is not None and right_line is not None:
        mid_line = [
            (left_line[0] + right_line[0]) // 2,
            (left_line[1] + right_line[1]) // 2,
            (left_line[2] + right_line[2]) // 2,
            (left_line[3] + right_line[3]) // 2
        ]
        cv2.line(line_image, (mid_line[0], mid_line[1]), (mid_line[2], mid_line[3]), (255, 0, 0), 6)

    output = cv2.addWeighted(image, 0.8, line_image, 1, 1)

    if offset_info is not None:
        offset, lane_center, car_center = offset_info

        direction = "Left" if offset < 50 else "Right" if offset > 50 else "Center"

        # 차량 중심 / 차선 중심 표시
        cv2.line(output, (car_center, output.shape[0]), (car_center, int(output.shape[0] * 0.6)), (255, 255, 0), 3)
        cv2.line(output, (lane_center, output.shape[0]), (lane_center, int(output.shape[0] * 0.6)), (0, 0, 255), 3)

        cv2.putText(output, f"Offset: {offset} ({direction}",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (255, 255, 255),
                    3)

    return output


# 메인 루프
# 차선 검출 → offset 계산 → TCP 전송
def process_video(input_path, output_path=None, display_size=(960, 540)):
    cap = cv2.VideoCapture(input_path)

    # 결과 저장 옵션
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    else:
        out = None

    # STM32 통신용 TCP
    TCP_IP = "192.168.2.5"
    TCP_PORT = 5001

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))

    buzzer_triggered = False
    tcp_enabled = True

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        edges = preprocess(frame)
        roi = region_of_interest(edges)
        lines = detect_lines(roi)

        offset_info = None
        left_line = right_line = None

        if lines is not None:
            left, right = average_slope_intercept(lines)

            y1 = frame.shape[0]
            y2 = int(y1 * 0.6)

            left_line = make_line_points(y1, y2, left)
            right_line = make_line_points(y1, y2, right)

            if left_line is not None and right_line is not None:
                offset_info = compute_offset_normalized(frame.shape[1], left_line, right_line)

                if offset_info and tcp_enabled:
                    offset, _, _ = offset_info

                    # offset STM32로 전송
                    try:
                        sock.sendall(f"{offset}\n".encode())
                    except:
                        pass

        # 차선 못 찾으면 buzzer driver 로드 + LKA off
        if not buzzer_triggered and (left_line is None or right_line is None):
            os.chdir("/home/pi15/buzzer")
            subprocess.run(["sudo", "insmod", "buzzer_driver.ko"])

            try:
                sock.sendall(b"200\n")  # LKA off
            except:
                pass

            buzzer_triggered = True
            tcp_enabled = False
            sock.close()

        lane_frame = display_lines(frame, [left_line, right_line], offset_info)

        if out:
            out.write(lane_frame)

        resized = cv2.resize(lane_frame, display_size)
        cv2.imshow("Lane Detection", resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

    if not buzzer_triggered:
        sock.close()

    if out:
        out.release()

    cv2.destroyAllWindows()


if __name__ == '__main__':
    process_video("video3-4.mp4", "output4-3.avi", display_size=(960, 540))
