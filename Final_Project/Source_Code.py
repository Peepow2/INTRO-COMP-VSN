import cv2
import numpy as np
import ROI_Manual_click

# --------------------------------------------- #

bgd = cv2.imread("background.png")
bgd = cv2.resize(bgd, (960, 540))

RoI = ROI_Manual_click.ROI_Click(bgd)

mask = np.ones(bgd.shape[:2], dtype=np.uint8) * 255
mask = ROI_Manual_click.preprocessing(mask, RoI)
masked_bgd = ROI_Manual_click.preprocessing(bgd, RoI)
gray_bgd = cv2.cvtColor(masked_bgd, cv2.COLOR_BGR2GRAY)
fgbg = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=80, detectShadows=True)
fgbg.apply(gray_bgd)

cap = cv2.VideoCapture("CAM31 Noon 2.mp4")
while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.resize(img, (960, 540))
    masked_img = ROI_Manual_click.preprocessing(img, RoI)
    gray_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(gray_img)

    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(fgmask, kernel, iterations=5)
    dilated = cv2.dilate(eroded, kernel, iterations=40)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_image = img.copy()
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)

    vehicle_area = 0
    vehicle_count = 0

    for c in contours:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = w / h if h != 0 else 0
        
        vehicle_area += area
        vehicle_count += 1

    print(f"Estimated Vehicle Count: {vehicle_count}")
    # print(f"Vehicle Area: {vehicle_area:.2f} pixels")

    total_area = np.count_nonzero(mask)
    congestion_ratio = vehicle_area / total_area

    if congestion_ratio > 0.7:
        status = "Jammed"
    elif congestion_ratio >= 0.4:
        status = "Heavy"
    else:
        status = "Flow"


    # Create Expanded_image
    image_height, image_width = contour_image.shape[:2]
    label_height = 100

    new_height = image_height + label_height
    expanded_image = np.zeros((new_height, image_width, 3), dtype=np.uint8)  # พื้นหลังสีดำ
    expanded_image[label_height:, :] = contour_image  # วางรูปเดิมลงไปด้านล่าง

    text = f"Traffic: {status} ({congestion_ratio:.4f})"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    thickness = 3

    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = (image_width - text_width) // 2
    text_y = (label_height + text_height) // 2
    cv2.putText(expanded_image, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
    cv2.imshow("expanded_image", expanded_image)
    cv2.waitKey(1)