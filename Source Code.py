import cv2
import numpy as np

img = cv2.imread("Test//Sample 2.png")
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)

thresh = cv2.adaptiveThreshold(blurred, 255, \
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                cv2.THRESH_BINARY_INV, 11, 2)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

sorted_contours = sorted(contours, key = cv2.contourArea, reverse=True)

#cv2.drawContours(img, [sorted_contours[2]], -1, (0, 255, 0), 2)
#print(sorted_contours[2])

peri = cv2.arcLength(sorted_contours[2], True)
approx = cv2.approxPolyDP(sorted_contours[2], 0.04 * peri, True)

if len(approx) == 4:
    screenCnt = approx

def order_points(pts):
    # pts มี shape (4, 1, 2) ต้อง reshape เป็น (4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.reshape(4, 2).sum(axis=1)
    diff = np.diff(pts.reshape(4, 2), axis=1)

    rect[0] = pts.reshape(4, 2)[np.argmin(s)]     # บนซ้าย (ผลรวม x+y น้อยสุด)
    rect[2] = pts.reshape(4, 2)[np.argmax(s)]     # ล่างขวา (ผลรวม x+y มากสุด)
    rect[1] = pts.reshape(4, 2)[np.argmin(diff)]  # บนขวา (ผลต่าง y-x น้อยสุด)
    rect[3] = pts.reshape(4, 2)[np.argmax(diff)]  # ล่างซ้าย (ผลต่าง y-x มากสุด)
    return rect

# 1. จัดเรียงจุดต้นทาง
rect = order_points(screenCnt)
(tl, tr, br, bl) = rect

# 2. กำหนดขนาดภาพผลลัพธ์ (ตัวอย่าง: A4 หรือตามสัดส่วนที่คำนวณ)
width = 622
height = 875

dst = np.array([
    [0, 0],
    [width - 1, 0],
    [width - 1, height - 1],
    [0, height - 1]], dtype="float32")

# 3. คำนวณ Matrix และ Warp
M = cv2.getPerspectiveTransform(rect, dst)
warped = cv2.warpPerspective(img, M, (width, height))

'''cv2.rectangle(warped, (0, 0), (50, 950), (0, 0, 255), 2)
cv2.rectangle(warped, (0, 810), (800, 950), (0, 0, 255), 2)
cv2.imshow("Output", warped)
cv2.waitKey()
cv2.destroyAllWindows()
exit()'''

# กำหนดเงื่อนไขของคุณ
min_area, max_area = 80, 500
min_peri, max_peri = 80, 150

gray_img2 = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray_img2, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

rect_contours = []

for cnt in contours:
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
    area = cv2.contourArea(cnt)
    
    if (min_area <= area <= max_area) and (min_peri <= peri <= max_peri):
        x, y, w, h = cv2.boundingRect(cnt)
        if (x <= 50 and y <= 950) or (x <= 800 and y >= 810):
            rect_contours.append(cnt)

sorted_contours = sorted(rect_contours, key=lambda ctr: (cv2.boundingRect(ctr)[1], cv2.boundingRect(ctr)[0]))[:-1:]

for idx in range(1, len(sorted_contours)):
    x1, y1, w1, h1 = cv2.boundingRect(sorted_contours[idx-1])
    x2, y2, w2, h2 = cv2.boundingRect(sorted_contours[idx])
    if x2 - x1 >= 15:
        X_detector = sorted_contours[idx:]
        Y_detector = sorted_contours[:idx]
        break

X_detector = sorted(X_detector, key = lambda c: cv2.boundingRect(c)[0])
Y_detector = sorted(Y_detector, key = lambda c: cv2.boundingRect(c)[1])

found_shade = []
for idxY in range(len(Y_detector)):
    x1, y1, w1, h1 = cv2.boundingRect(Y_detector[idxY])
    for idxX in range(len(X_detector)):
        x2, y2, w2, h2 = cv2.boundingRect(X_detector[idxX])
        roi = warped[y1:y1+10, x2-5:x2+5]
        black_pixels = np.sum(roi == 255)
        if black_pixels <= 10:
            found_shade.append(tuple([idxX, idxY]))
            cv2.rectangle(warped, (x2-5, y1), (x2+5, y1+10), (0, 0, 255), 3)
cv2.imshow("Output", warped)
cv2.waitKey(0)

Cancel = False
Course_ID = "XX"
Student_ID = "XXX"
Answer = ['' for i in range(10)] + ["XXXX.XX"]

for x, y in found_shade:
    if 2 <= y <= 11 and  9 <= x <= 10:
        Course_ID = Course_ID[:x-9] + str(y-2) + Course_ID[x-8:]

    if 2 <= y <= 11 and  12 <= x <= 14:
        Student_ID = Student_ID[:x-12] + str(y-2) + Student_ID[x-11:]

    if y == 10 and  x == 2:
        Cancel = True

    if 15 <= y <= 24 and  1 <= x <= 5:
        Answer[int(y-15)] += str(x)
    
    if 15 <= y <= 24 and  8 <= x <= 14:
        if Answer[-1][x-8] != "X":
            Answer[-1] += "X"
        Answer[-1] =  Answer[-1][:x-8] + str(y-15) + Answer[-1][x-7:]

print(Course_ID, Student_ID)
print(Answer)
print(Cancel)