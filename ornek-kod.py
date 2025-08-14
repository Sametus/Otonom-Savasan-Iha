from pymavlink import mavutil
import time, math, threading

latest_pos = None
pos_lock = threading.Lock()

def gps_listener(con):
    global latest_pos
    while True:
        time.sleep(0.1)
        msg = con.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=1.0)
        if msg:
            with pos_lock:
                latest_pos = (msg.lat/1e7, msg.lon/1e7, msg.relative_alt/1000.0)

def get_latest_position():
    with pos_lock:
        return latest_pos

def connect(port):
    con = mavutil.mavlink_connection(port)
    con.wait_heartbeat()
    time.sleep(0.5)
    print(f"{port} ile bağlantı kuruldu.")
    return con

def do_arm(con):
    con.mav.command_long_send(
        con.target_system,
        con.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,1,0,0,0,0,0,0
    )
    con.motors_armed_wait()
    print("Motorlar arm edildi.")

def set_mode(con, mod):
    con.mav.command_long_send(
        con.target_system,
        con.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mod,0,0,0,0,0
    )
    time.sleep(1)
    print(f"Uçuş Modu: {mod}")

def auto_takeoff(con,alt=50):
    set_mode(con,13)
    time.sleep(8)
    print("Kalkış Yapıldı.")

########################################
########################################
########################################
########################################

def guided_go_to(con, p1, alt=50):
    lat, lon, alt = p1
    assert abs(lat) < 180 and abs(lon) < 180
    ########################################
    ########################################
    ########################################
    ########################################
    print(f"Şuan hedef: {lat:.6f}, {lon:.6f}, {alt:.2f} m")

def h_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = φ2 - φ1
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def distance(p1, p2):
    lat1, lon1, alt1 = p1
    lat2, lon2, alt2 = p2
    horiz = h_distance(lat1, lon1, lat2, lon2)
    vert = abs(alt2 - alt1)
    d = math.hypot(horiz, vert)
    print(f"Mesafe: {d:.2f} m")
    time.sleep(0.1)
    return d

def lineer_go_to(p1, p2, h_d):
    lat1, lon1, alt1 = p1
    lat2, lon2, alt2 = p2

    # Enlemde 1 derece ≈ 111320 metre
    m_lat = 111320
    # Boylamda 1 derece ≈ 111320 * cos(lat) metre
    m_lon = 111320 * math.cos(math.radians((lat1 + lat2) / 2))

    dx = (lat2 - lat1) * m_lat
    dy = (lon2 - lon1) * m_lon

    d = math.hypot(dx, dy)
    if d == 0:
        raise ValueError("İki nokta aynı olamaz")
    ux = dx / d
    uy = dy / d

    # Metre cinsinden ilerleme → dereceye çevrilip eklenmeli
    lat3 = lat2 + (ux * h_d) / m_lat
    lon3 = lon2 + (uy * h_d) / m_lon
    return (lat3, lon3)

def quaternion_from_euler(roll, pitch, yaw):
    cr = math.cos(roll/2); sr = math.sin(roll/2)
    cp = math.cos(pitch/2); sp = math.sin(pitch/2)
    cy = math.cos(yaw/2); sy = math.sin(yaw/2)
    ########################################
    ########################################
    ########################################
    ########################################
    return w, x, y, z

def change_pitch(con, target_deg):
    pitch = math.radians(target_deg)
    q = quaternion_from_euler(0.0, pitch, 0.0)
    ########################################
    ########################################
    ########################################
    ########################################

def get_blocking_position(con, timeout=1.0):
    ########################################
    ########################################
    ########################################
    ########################################
    msg = con.recv_match(type="GLOBAL_POSITION_INT",blocking = True, timeout=timeout)
    if msg:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt/1000.0
        return lat, lon, alt

def QR_(con, qr, t):

    did_kamikaze = False
    if not did_kamikaze:
        ########################################
        ########################################
        ########################################
        ########################################
            p = get_latest_position()
            if not p: continue
            d = distance(p, qr)
            if 135 <= d < 155:
                guided_go_to(con, lineer_go_to(p, qr, t)+(50,))
                print("QR Gidiliyor [fake_t]")
                break
    while True:
        c = get_latest_position()
        if not c: continue
        m = distance(c, qr)
        if m <= 75:
            print("KAMİKAZE BAŞLADI")
            while True:
                change_pitch(con, -45)
                time.sleep(0.1)
                h = get_blocking_position(con, timeout=1.0)
                if h is not None and h[2] <= 25:
                    change_pitch(con, 0)
                    break
            print("KAMİKAZE BİTTİ")
            ########################################
            ########################################
            ########################################
            ########################################
    time.sleep(2)

###############################################
con = connect("tcp:127.0.0.1:5763")
time.sleep(0.25)
do_arm(con)
time.sleep(0.25)
auto_takeoff(con, 50)
set_mode(con, 15)
time.sleep(0.25)

# GPS dinleyici thread başlat
gps_thread = threading.Thread(target=gps_listener, args=(con,), daemon=True)
gps_thread.start()
time.sleep(2)

########################################
########################################
########################################
########################################
# QR 1
QR_(con, (-35.363218, 149.164264, 50), t=80)
# -35.365082, 149.165904
guided_go_to(con, (-35.365082, 149.165904, 50))
time.sleep(7)

# QR 2
QR_(con, (-35.361466, 149.167454, 50), t=80)
# -35.360897, 149.165329
guided_go_to(con, (-35.360897, 149.165329, 80))
time.sleep(5)

#QR 1 (TEKRAR)
QR_(con, (-35.363262, 149.164137, 50), t=70)

set_mode(con, 11)


"""
Latitude  = -35.363262
Longitude = 149.164137

"""