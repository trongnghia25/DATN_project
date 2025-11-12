import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt

# Đường dẫn mô hình YOLOv8
yolo_model_path = '../modelsYOLO/best.pt'

# Khởi tạo YOLOv8 và PaddleOCR
yolo_model = YOLO(yolo_model_path)
ocr = PaddleOCR(use_angle_cls=True, lang='en')


def detect_license_plate(image_path):
    """
    Phát hiện biển số trong ảnh bằng YOLOv8.
    """
    # Đọc ảnh
    img = cv2.imread(image_path)
    results = yolo_model(img)  # Phát hiện đối tượng

    # Lấy các vùng chứa biển số
    plates = []
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Tọa độ bounding box
        plate_img = img[y1:y2, x1:x2]  # Crop vùng biển số
        plates.append(plate_img)

    return plates


def recognize_text(plate_img):
    """
    Nhận dạng văn bản từ một ảnh biển số bằng PaddleOCR.
    """
    # Chuyển ảnh sang định dạng RGB (nếu cần)
    if len(plate_img.shape) == 2 or plate_img.shape[2] != 3:
        plate_img = cv2.cvtColor(plate_img, cv2.COLOR_GRAY2RGB)

    result = ocr.ocr(plate_img, cls=True)  # Nhận dạng văn bản
    texts = [line[1][0] for line in result[0]]  # Lấy text từ kết quả OCR

    # Vẽ kết quả OCR lên ảnh (tuỳ chọn)
    boxes = [line[0] for line in result[0]]
    img_annotated = draw_ocr(plate_img, boxes, texts, [line[1][1] for line in result[0]])

    return " ".join(texts), img_annotated


def main(image_path):
    # Bước 1: Phát hiện biển số
    plates = detect_license_plate(image_path)

    if not plates:
        print("Không tìm thấy biển số nào.")
        return

    # Hiển thị và nhận dạng từng biển số
    for i, plate in enumerate(plates):
        print(f"Đang xử lý biển số {i + 1}...")

        # Nhận dạng ký tự từ biển số
        recognized_text, annotated_img = recognize_text(plate)

        # Hiển thị kết quả
        print(f"Biển số {i + 1}: {recognized_text}")

        # Hiển thị biển số với chú thích ký tự nhận dạng
        plt.imshow(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))
        plt.title(f"Biển số {i + 1} (OCR)")
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    # Thay đường dẫn tới ảnh của bạn
    image_path = "D:/DataBien_So/train/images/3dd2ac1943c3f89da1d2.jpg"
    main(image_path)