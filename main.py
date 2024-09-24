import pyautogui
import cv2
import numpy as np
import threading
import keyboard  # ไลบรารีสำหรับตรวจจับการกดคีย์

# กำหนดขนาดหน้าต่าง ESP
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
stop_program = False  # ตัวแปรสำหรับหยุดการทำงานของโปรแกรม

def draw_esp_box(position_func, window_name='ESP'):
    global stop_program
    # สร้างหน้าต่างและแสดงกรอบ ESP ในตำแหน่งที่ตรวจจับได้
    img = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)  # หน้าต่างขนาด 800x600
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # ตั้งค่าสถานะให้หน้าต่างซ้อนทับกับหน้าจอและไม่ปิดกั้นการใช้งาน
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    while not stop_program:
        # รีเซ็ตภาพในหน้าต่าง
        img[:] = 0
        # ดึงตำแหน่งที่ตรวจพบจากฟังก์ชัน position_func
        position = position_func()

        # วาดกรอบสีแดงในตำแหน่งที่ตรวจพบ
        if position:
            cv2.rectangle(img, position[0], position[1], (0, 0, 255), 2)  # สีแดง

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # กด 'q' เพื่อออกจากการแสดงผล
            break
    cv2.destroyAllWindows()

def detect_icon_position():
    global stop_program
    # ตรวจสอบขนาดของหน้าจอเพื่อการแปลงสเกล
    screen_width, screen_height = pyautogui.size()
    scale_x = WINDOW_WIDTH / screen_width
    scale_y = WINDOW_HEIGHT / screen_height

    # ตัวแปร position ที่จะใช้ในการวาดกรอบ ESP
    position = [None]

    # ฟังก์ชันที่ส่งตำแหน่งล่าสุดไปยัง draw_esp_box
    def get_position():
        return position[0]

    # เริ่มต้นหน้าต่าง ESP ใน thread แยก
    threading.Thread(target=draw_esp_box, args=(get_position,)).start()

    while not stop_program:
        try:
            # ตรวจจับไอคอนด้วยความแม่นยำ 80%
            icon_location = pyautogui.locateOnScreen('test.png', confidence=0.8)
            if icon_location:
                x, y, w, h = icon_location.left, icon_location.top, icon_location.width, icon_location.height
                # แปลงตำแหน่งที่ตรวจจับได้ตามขนาดของหน้าต่าง
                scaled_x1 = int(x * scale_x)
                scaled_y1 = int(y * scale_y)
                scaled_x2 = int((x + w) * scale_x)
                scaled_y2 = int((y + h) * scale_y)

                # อัปเดตตำแหน่งไอคอนที่ตรวจพบ
                position[0] = ((scaled_x1, scaled_y1), (scaled_x2, scaled_y2))
                print(f"Icon detected at {position[0]} (Scaled)")
            else:
                # ไม่มีการตรวจพบไอคอน
                position[0] = None
        except pyautogui.ImageNotFoundException:
            print("Icon not found on the screen.")

def check_for_stop_key():
    global stop_program
    # ตรวจจับคีย์ 'esc' เพื่อหยุดการทำงานของโปรแกรม
    keyboard.wait('esc')  # รอจนกว่าจะกดปุ่ม 'esc'
    stop_program = True
    print("Program stopped by user.")

# ใช้ threading เพื่อให้การทำงานเกิดขึ้นพร้อมกัน
t1 = threading.Thread(target=detect_icon_position)
t2 = threading.Thread(target=check_for_stop_key)
t1.start()
t2.start()
