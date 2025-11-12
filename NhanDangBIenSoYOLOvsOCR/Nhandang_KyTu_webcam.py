import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import time

# Đường dẫn mô hình YOLOv8
yolo_model_path = '../modelsYOLO/best.pt'

# Khởi tạo YOLOv8 và PaddleOCR
yolo_model = YOLO(yolo_model_path)
ocr = PaddleOCR(use_angle_cls=True, lang='en')


def detect_license_plate(frame):
    """
    Phát hiện biển số trong khung hình bằng YOLOv8.
    """
    results = yolo_model(frame)  # Phát hiện đối tượng

    # Kiểm tra nếu không có kết quả
    if results[0].boxes is None or len(results[0].boxes) == 0:
        return [], []

    # Lấy các vùng chứa biển số
    plates = []
    boxes = []
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Tọa độ bounding box
        plate_img = frame[y1:y2, x1:x2]  # Crop vùng biển số
        plates.append(plate_img)
        boxes.append((x1, y1, x2, y2))

    return plates, boxes


def recognize_text(plate_img):
    """
    Nhận dạng văn bản từ một ảnh biển số bằng PaddleOCR.
    """
    # Chuyển ảnh sang định dạng RGB (nếu cần)
    if len(plate_img.shape) == 2 or plate_img.shape[2] != 3:
        plate_img = cv2.cvtColor(plate_img, cv2.COLOR_GRAY2RGB)

    # Thực hiện nhận dạng văn bản
    result = ocr.ocr(plate_img, cls=True)
    if not result or not result[0]:
        return "Không nhận dạng được"

    texts = [line[1][0] for line in result[0]]  # Lấy text từ kết quả OCR
    return " ".join(texts)  # Gộp tất cả text thành một chuỗi duy nhất


def main():
    # Mở webcam
    # cap = cv2.VideoCapture("http://10.50.128.71:4747/video")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở webcam.")
        return

    print("Nhấn 'q' để thoát.")

    last_recognized_text = "Không nhận dạng được"  # Lưu kết quả cuối cùng
    while True:
        # Đọc khung hình từ webcam
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ webcam.")
            break

        frame = cv2.resize(frame, (640, 480))

        # Phát hiện biển số
        plates, boxes = detect_license_plate(frame)

        # Hiển thị các khung chứa biển số và nhận dạng ký tự
        for plate, (x1, y1, x2, y2) in zip(plates, boxes):
            # Nhận dạng ký tự từ biển số
            recognized_text = recognize_text(plate)

            # Lưu kết quả cuối cùng
            if recognized_text:
                last_recognized_text = recognized_text

            # Vẽ khung chứa và hiển thị kết quả nhận dạng
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, recognized_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Hiển thị khung hình
        cv2.imshow("Biển số", frame)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()

    # Hiển thị kết quả cuối cùng
    print(f"Kết quả nhận dạng: {last_recognized_text}")


if __name__ == "__main__":
    main()
