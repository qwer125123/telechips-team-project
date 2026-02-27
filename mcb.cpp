<mcb.cpp>

#include <opencv2/opencv.hpp>
#include <dlib/opencv.h>
#include <dlib/image_processing.h>
#include <dlib/image_processing/frontal_face_detector.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <unistd.h>

// CAN 관련
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <cstring>

using namespace std;
using namespace cv;
using namespace dlib;

// ---- GPIO 충격 센서 관련 ----
const std::string gpioNum = "86";
const std::string gpioPath = "/sys/class/gpio/gpio" + gpioNum;

void export_gpio() {
    std::ofstream export_file("/sys/class/gpio/export");
    export_file << gpioNum;
    export_file.close();
    usleep(100000);
}

void set_direction_in() {
    std::ofstream direction(gpioPath + "/direction");
    direction << "in";
    direction.close();
}

bool read_gpio() {
    std::ifstream value(gpioPath + "/value");
    std::string val;
    value >> val;
    return val == "1";
}

// ---- EAR 계산 ----
double eyeAspectRatio(const std::vector<Point>& eye) {
    double A = norm(eye[1] - eye[5]);
    double B = norm(eye[2] - eye[4]);
    double C = norm(eye[0] - eye[3]);
    return (A + B) / (2.0 * C);
}

const int LEFT_EYE_IDX[]  = {36, 37, 38, 39, 40, 41};
const int RIGHT_EYE_IDX[] = {42, 43, 44, 45, 46, 47};

// ---- CAN 전송 ----
int init_can_socket() {
    int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    struct ifreq ifr;
    std::strcpy(ifr.ifr_name, "can0");
    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("ioctl");
        return -1;
    }

    struct sockaddr_can addr{};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return -1;
    }

    return sock;
}

void send_can(int sock, uint8_t code) {
    struct can_frame frame{};
    frame.can_id  = 0x111;  // 예시 CAN ID
    frame.can_dlc = 1;
    frame.data[0] = code;

    if (write(sock, &frame, sizeof(frame)) != sizeof(frame)) {
        perror("CAN write failed");
    }
}

int main() {
    // GPIO 설정
    export_gpio();
    set_direction_in();

    // CAN 소켓 초기화
    int can_sock = init_can_socket();
    if (can_sock < 0) {
        cerr << "CAN 소켓 초기화 실패" << endl;
        return -1;
    }

    // 카메라 초기화
    VideoCapture cap(1, cv::CAP_V4L2);
    cap.set(CAP_PROP_FRAME_WIDTH, 240);
    cap.set(CAP_PROP_FRAME_HEIGHT, 240);

    if (!cap.isOpened()) {
        cerr << "카메라 열기 실패" << endl;
        return -1;
    }

    // 얼굴/눈 감지 준비
    frontal_face_detector detector = get_frontal_face_detector();
    shape_predictor predictor;
    deserialize("shape_predictor_68_face_landmarks.dat") >> predictor;

    bool analysis_enabled = false;
    const double EYE_AR_THRESH = 0.2;
    int COUNTER = 0;
    int last_state = 0;

    cout << "초기화 완료. 충격 감지되면 얼굴 분석 시작..." << endl;

    Mat frame;
    while (true) {
        cap >> frame;
        if (frame.empty()) break;

        // 진동 감지되면 분석 모드 ON
        if (!analysis_enabled && read_gpio()) {
            cout << "충격 감지됨! 눈 분석 시작" << endl;
            analysis_enabled = true;
        }

        int current_state = 0;

        if (analysis_enabled) {
            Mat gray;
            cvtColor(frame, gray, COLOR_BGR2GRAY);
            dlib::cv_image<unsigned char> dlib_img(gray);
            std::vector<dlib::rectangle> faces = detector(dlib_img);

            if (faces.empty()) {
                current_state = 3;
            } else {
                for (size_t i = 0; i < faces.size(); ++i) {
                    full_object_detection shape = predictor(dlib_img, faces[i]);

                    std::vector<Point> leftEye, rightEye;
                    for (int j = 0; j < 6; ++j) {
                        leftEye.push_back(Point(shape.part(LEFT_EYE_IDX[j]).x(), shape.part(LEFT_EYE_IDX[j]).y()));
                        rightEye.push_back(Point(shape.part(RIGHT_EYE_IDX[j]).x(), shape.part(RIGHT_EYE_IDX[j]).y()));
                    }

                    double leftEAR = eyeAspectRatio(leftEye);
                    double rightEAR = eyeAspectRatio(rightEye);
                    double ear = (leftEAR + rightEAR) / 2.0;

                    current_state = (ear < EYE_AR_THRESH) ? 2 : 1;

                    cout << "EAR: " << ear << " | 상태: "
                         << ((current_state == 1) ? "눈뜸" : "눈감음") << endl;

                    std::vector<Point> leftHull, rightHull;
                    convexHull(leftEye, leftHull);
                    convexHull(rightEye, rightHull);
                    polylines(frame, leftHull, true, Scalar(0, 255, 0), 1);
                    polylines(frame, rightHull, true, Scalar(0, 255, 0), 1);
                }
            }

            // 상태 변경 시에만 CAN 전송
            if (current_state != last_state && current_state != 0) {
                send_can(can_sock, current_state);
                last_state = current_state;
            }
        }

        imshow("Webcam", frame);
        if (waitKey(1) == 'q') break;
    }

    cap.release();
    close(can_sock);
    destroyAllWindows();
    return 0;
}
