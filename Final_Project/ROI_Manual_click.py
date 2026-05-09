import cv2
import math
import numpy as np

Roi_shapes = []
current_points = []
is_selecting_vector = False
is_done = False
img_main = None
bottom_bar = None
ROI_win_Message = "Define the ROI on the map"

def redraw():
    global img_main, bottom_bar, Roi_shapes, current_points
    
    temp_img = np.vstack((img_main, bottom_bar)).copy()
    h_offset = img_main.shape[0]

    for shape in Roi_shapes:
        if len(shape) > 2:
            pts = np.array(shape, np.int32).reshape((-1, 1, 2))
            cv2.polylines(temp_img, [pts], isClosed=True, color=(255, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        for pt in shape:
            cv2.rectangle(temp_img, (pt[0]-3, pt[1]-3), (pt[0]+3, pt[1]+3), (0, 255, 0), -1)

    # 3. วาดสิ่งที่กำลังทำอยู่
    if len(current_points) > 1:
        for i in range(len(current_points) - 1):
            cv2.line(temp_img, current_points[i], current_points[i+1], (0, 255, 255), 2, cv2.LINE_AA)
        if len(current_points) >= 3:
            cv2.line(temp_img, current_points[-1], current_points[0], (0, 255, 255), 2, cv2.LINE_AA)
    for pt in current_points:
        cv2.rectangle(temp_img, (pt[0]-5, pt[1]-5), (pt[0]+5, pt[1]+5), (255, 0, 0), -1)

    # NEXT SHAPE button
    cv2.rectangle(temp_img, (10, h_offset + 20), (150, h_offset + 70), (200, 100, 0), -1)
    cv2.putText(temp_img, " NEXT STEP", (30, h_offset + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # FINISH button
    cv2.rectangle(temp_img, (170, h_offset + 20), (270, h_offset + 70), (0, 150, 0), -1)
    cv2.putText(temp_img, "FINISH", (195, h_offset + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    

    # Status Message
    status = f"Shapes: {len(Roi_shapes)}"
    cv2.putText(temp_img, status, (290, h_offset + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    
    cv2.imshow(ROI_win_Message, temp_img)

def clickPosition(event, x, y, flags, param):
    global current_points, is_done, is_selecting_vector, current_vector, Noon_Mode
    global Roi_shapes, Vector_Road, img_main

    h_offset = img_main.shape[0]
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if h_offset + 15 <= y <= h_offset + 65:
            if 10 <= x <= 150: # NEXT STEP
                if len(current_points) >= 3:
                    Roi_shapes.append(tuple(current_points.copy()))
                    current_points = []
            
            elif 170 <= x <= 270: # FINISH
                if len(Roi_shapes) == 0 and len(current_points) < 3:
                    is_done = False
                else:
                    if len(current_points) >= 3: 
                        Roi_shapes.append(tuple(current_points.copy()))
                    is_done = True

        # ตรวจสอบการคลิกบนภาพ
        elif y < h_offset:
            current_points.append((x, y))
        redraw()
            
    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(current_points) != 0: 
            current_points.pop()
        elif len(Roi_shapes) != 0: 
            current_points = Roi_shapes.pop()
        redraw()


def ROI_Click(img_raw):
    global img_main, bottom_bar, Roi_shapes, current_points, is_done, ROI_win_Message
    
    fix_size = (960, 540)
    img_main = cv2.resize(img_raw, fix_size).copy()

    # Button Bar
    bar_height = 90
    bottom_bar = np.full((bar_height, img_main.shape[1], 3), 50, dtype=np.uint8)

    # Initial lists
    Roi_shapes = []
    current_points = []
    is_done = False

    cv2.namedWindow(ROI_win_Message)
    cv2.setMouseCallback(ROI_win_Message, clickPosition)
    redraw()

    while not is_done:
        key = cv2.waitKey(1) & 0xFF
        if key == 27: break # ESC
    
    cv2.destroyAllWindows()
    return [Roi_shapes]


def preprocessing(frame, RoI):
    w, h = 960, 540
    mask = np.zeros((h, w), dtype=np.uint8)   
    for r in RoI:
        cv2.fillPoly(mask, [np.array(r)], 255)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result