import subprocess  # 외부 명령 실행을 위한 모듈
import cv2         # OpenCV 라이브러리 (이미지 처리 및 GUI)

click_pos = None  # 클릭한 화면상의 좌표를 저장할 변수
clicked   = False # 클릭이 발생했는지 여부 플래그

def capture_screenshot(path="screen.png"):
    """
    ADB를 통해 연결된 Android 기기에서
    화면을 캡처하여 로컬 파일로 저장합니다.
    """
    with open(path, "wb") as f:
        # adb exec-out screencap -p: PNG 형식으로 스크린샷을 stdout으로 출력
        subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=f,    # 표준 출력을 파일에 기록
            check=True   # 에러 발생 시 예외 발생
        )
    print(f"[✔] Screenshot saved to {path}")

def mouse_callback(event, x, y, flags, param):
    """
    OpenCV 마우스 이벤트 콜백 함수.
    첫 번째 왼쪽 클릭 시 클릭 좌표를 저장하고 클릭 플래그를 True로 변경합니다.
    """
    global click_pos, clicked
    # 왼쪽 버튼을 눌렀고, 아직 클릭된 적이 없다면
    if event == cv2.EVENT_LBUTTONDOWN and not clicked:
        click_pos = (x, y)  # 화면 표시 좌표 저장
        clicked   = True    # 클릭 완료 표시
        print(f"[🖱️] Click at display coords: {click_pos}")

def show_and_record(path="screen.png", max_w=800, max_h=600):
    """
    1) 저장된 스크린샷을 로드
    2) max_w * max_h 범위 내에서 비율을 유지하며 리사이즈
    3) 작은 창에 이미지를 띄우고 클릭 대기
    4) 클릭된 좌표를 원본 해상도로 복원하여 반환
    """
    # 1) 이미지 로드
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {path}")
    h, w = img.shape[:2]  # 원본 높이(h) & 너비(w)

    # 2) 화면에 맞출 축소 비율 계산 (최대 1.0 이하)
    scale = min(max_w / w, max_h / h, 1.0)
    disp_w, disp_h = int(w * scale), int(h * scale)

    # 3) OpenCV로 리사이즈 (INTER_AREA: 축소 시 품질 보존)
    resized = cv2.resize(img, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

    # 4) 윈도우 생성 및 크기 설정
    cv2.namedWindow("Mobile Screen", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Mobile Screen", disp_w, disp_h)

    # 5) 클릭 이벤트 콜백 등록
    cv2.setMouseCallback("Mobile Screen", mouse_callback)

    print("👉 화면을 클릭하면 좌표를 기록하고 바로 종료됩니다.")
    # 6) 클릭이 발생할 때까지 루프 실행
    while not clicked:
        cv2.imshow("Mobile Screen", resized)
        cv2.waitKey(1)  # 창이 멈추지 않도록 이벤트 처리만 수행

    # 7) 창 닫기
    cv2.destroyAllWindows()

    # 8) 클릭된 화면 좌표 -> 정규화된 비율 계산
    x_disp, y_disp = click_pos
    x_norm = x_disp / disp_w
    y_norm = y_disp / disp_h

    # 9) 원본 해상도 좌표로 변환
    orig_x = int(x_norm * w)
    orig_y = int(y_norm * h)
    print(f"[✔] Original coords: ({orig_x}, {orig_y})")

    return orig_x, orig_y

if __name__ == "__main__":
    # 스크린샷 캡처
    capture_screenshot("screen.png")
    # 화면 표시 & 클릭 좌표 획득
    final_pos = show_and_record("screen.png")
    print(f"🎯 최종 좌표: {final_pos}")
