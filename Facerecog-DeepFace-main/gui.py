import json
import time
import cv2
import numpy as np
from config import (
    COLOR_ACCENT,
    COLOR_ACCENT_SOFT,
    COLOR_BG,
    COLOR_BLUE,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_DANGER_SOFT,
    COLOR_MUTED,
    COLOR_PANEL,
    COLOR_PRIMARY,
    COLOR_PRIMARY_SOFT,
    COLOR_SURFACE,
    COLOR_TEXT,
    COLOR_WARNING,
    COLOR_WARNING_SOFT,
    REGISTER_SAMPLE_COUNT,
)
from recognition import (
    MotionLivenessChallenge,
    create_embedding,
    face_detection,
    find_largest_face,
    open_camera,
    recognize_face,
)
from storage import (
    delete_known_face,
    display_face_label,
    get_member_info,
    image_to_base64,
    known_person_count,
    list_known_face_entries,
    list_known_face_files,
    load_known_faces,
    load_members_metadata,
    rebuild_embeddings,
    save_face_sample,
    save_members_metadata,
    slugify,
    update_member_info,
)
from api_client import (
    get_customer,
    notify_member_detected,
    post_json,
    send_register_customer,
    update_customer,
)


def prompt_int(label, default_value=0):
    raw_value = input(f"{label} [{default_value}]: ").strip()
    if not raw_value:
        return default_value
    try:
        return int(raw_value)
    except ValueError:
        print(f"{label} harus angka. Dipakai default {default_value}.")
        return default_value


def draw_centered_text(canvas, text, center, font_scale, color, thickness=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = int(center[0] - text_size[0] / 2)
    y = int(center[1] + text_size[1] / 2)
    cv2.putText(canvas, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)


def draw_round_rect(canvas, rect, color, radius=12, thickness=-1, border_color=None):
    x1, y1, x2, y2 = rect
    radius = max(0, min(radius, abs(x2 - x1) // 2, abs(y2 - y1) // 2))

    if thickness < 0:
        cv2.rectangle(canvas, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(canvas, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        if radius > 0:
            cv2.circle(canvas, (x1 + radius, y1 + radius), radius, color, -1)
            cv2.circle(canvas, (x2 - radius, y1 + radius), radius, color, -1)
            cv2.circle(canvas, (x1 + radius, y2 - radius), radius, color, -1)
            cv2.circle(canvas, (x2 - radius, y2 - radius), radius, color, -1)
        if border_color:
            draw_round_rect(canvas, rect, border_color, radius, 1)
        return

    if radius == 0:
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
        return

    cv2.line(canvas, (x1 + radius, y1), (x2 - radius, y1), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x1 + radius, y2), (x2 - radius, y2), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x1, y1 + radius), (x1, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x2, y1 + radius), (x2, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.ellipse(canvas, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(canvas, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(canvas, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(canvas, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness, cv2.LINE_AA)


def draw_header(canvas, title, subtitle, width=760):
    draw_round_rect(canvas, (20, 16, width - 20, 96), COLOR_PANEL, 16, -1, COLOR_BORDER)
    # Brand icon badge
    draw_round_rect(canvas, (36, 30, 84, 78), COLOR_PRIMARY_SOFT, 12, -1)
    cv2.circle(canvas, (60, 54), 13, COLOR_PRIMARY, -1, cv2.LINE_AA)
    cv2.circle(canvas, (60, 54), 5, COLOR_PANEL, -1, cv2.LINE_AA)
    # Titles
    cv2.putText(canvas, title, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.76, COLOR_TEXT, 2, cv2.LINE_AA)
    cv2.putText(canvas, subtitle, (100, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.44, COLOR_MUTED, 1, cv2.LINE_AA)


def draw_status_chip(canvas, text, rect, color, soft_color, dot=True):
    draw_round_rect(canvas, rect, soft_color, 10, -1)
    x1, y1, x2, y2 = rect
    if dot:
        cv2.circle(canvas, (x1 + 14, (y1 + y2) // 2), 4, color, -1, cv2.LINE_AA)
        cv2.putText(canvas, text, (x1 + 26, (y1 + y2) // 2 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
    else:
        draw_centered_text(canvas, text, ((x1 + x2) // 2, (y1 + y2) // 2), 0.42, color, 1)


def draw_menu_button(canvas, button, is_hover=False):
    x1, y1, x2, y2 = button["rect"]
    color = button.get("color", COLOR_PANEL)
    border = button.get("border", COLOR_BORDER)
    text_color = button.get("text_color", COLOR_PRIMARY)
    font_scale = button.get("font_scale", 0.54)
    thickness = button.get("thickness", 1)

    draw_round_rect(canvas, (x1, y1, x2, y2), color, 12, -1, border)
    draw_centered_text(
        canvas,
        button["label"],
        ((x1 + x2) // 2, (y1 + y2) // 2),
        font_scale,
        text_color,
        thickness,
    )


def button_at_position(buttons, x, y):
    for button in buttons:
        x1, y1, x2, y2 = button["rect"]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return button["value"]
    return None


def field_at_position(fields, x, y):
    for index, field in enumerate(fields):
        x1, y1, x2, y2 = field["rect"]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return index
    return None


def draw_input_field(canvas, field, value, active=False):
    x1, y1, x2, y2 = field["rect"]
    border = COLOR_PRIMARY if active else COLOR_BORDER
    bg_color = COLOR_PANEL if not active else (255, 255, 255)

    # Field Label
    cv2.putText(
        canvas,
        field["label"],
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.46,
        COLOR_TEXT if active else COLOR_MUTED,
        1,
        cv2.LINE_AA,
    )
    draw_round_rect(canvas, (x1, y1, x2, y2), bg_color, 10, -1, border)

    display_value = value if value else field["placeholder"]
    text_color = COLOR_TEXT if value else COLOR_MUTED
    if active:
        display_value = f"{display_value}|"

    cv2.putText(
        canvas,
        display_value[:42],
        (x1 + 14, y1 + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        text_color,
        1,
        cv2.LINE_AA,
    )


def close_window(camera):
    if camera is not None:
        try:
            camera.release()
        except Exception:
            pass
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass


def show_customer_form(title, subtitle, default_discount=0, initial_values=None, submit_label="Mulai Register"):
    window_name = title
    selected = {"value": None}
    active_field = {"index": 0}
    values = {
        "name": (initial_values or {}).get("name", ""),
        "phone": (initial_values or {}).get("phone", ""),
        "discount": str((initial_values or {}).get("discount", default_discount)),
    }
    status = {"text": "Klik kolom untuk mengetik, lalu klik tombol simpan."}

    fields = [
        {
            "key": "name",
            "label": "Nama Lengkap Member *",
            "placeholder": "Contoh: Budi Santoso",
            "rect": (140, 185, 620, 235),
        },
        {
            "key": "phone",
            "label": "Nomor WhatsApp / HP",
            "placeholder": "Contoh: 08123456789 (opsional)",
            "rect": (140, 270, 620, 320),
        },
        {
            "key": "discount",
            "label": "Diskon Member (%)",
            "placeholder": "0",
            "rect": (140, 355, 620, 405),
        },
    ]

    buttons = [
        {
            "label": submit_label,
            "value": "start",
            "rect": (140, 440, 440, 492),
            "color": COLOR_PRIMARY,
            "border": COLOR_PRIMARY,
            "text_color": (255, 255, 255),
            "font_scale": 0.54,
            "thickness": 1,
        },
        {
            "label": "Batal",
            "value": "back",
            "rect": (460, 440, 620, 492),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.54,
            "thickness": 1,
        },
    ]

    def on_mouse(event, x, y, _flags, _params):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        field_idx = field_at_position(fields, x, y)
        if field_idx is not None:
            active_field["index"] = field_idx
            return

        selected["value"] = button_at_position(buttons, x, y)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)

    while selected["value"] is None:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            selected["value"] = "back"
            break

        canvas = np.full((550, 760, 3), COLOR_BG, dtype=np.uint8)
        draw_header(canvas, title, subtitle, 760)

        # Form Card Panel
        draw_round_rect(canvas, (100, 115, 660, 520), COLOR_PANEL, 16, -1, COLOR_BORDER)
        draw_status_chip(canvas, "Formulir Member", (140, 130, 290, 160), COLOR_PRIMARY, COLOR_PRIMARY_SOFT)
        cv2.putText(
            canvas,
            status["text"],
            (305, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            COLOR_MUTED,
            1,
            cv2.LINE_AA,
        )

        for index, field in enumerate(fields):
            draw_input_field(canvas, field, values[field["key"]], active_field["index"] == index)

        for button in buttons:
            draw_menu_button(canvas, button)

        cv2.imshow(window_name, canvas)
        key = cv2.waitKey(30) & 0xFF

        if key in (27,):  # Esc
            selected["value"] = "back"
            break

        if key == 9:  # Tab
            active_field["index"] = (active_field["index"] + 1) % len(fields)
            continue

        if key in (13, 10):  # Enter
            if active_field["index"] < len(fields) - 1:
                active_field["index"] += 1
                continue
            else:
                selected["value"] = "start"
                break

        field = fields[active_field["index"]]
        field_key = field["key"]

        if key in (8, 127):  # Backspace
            values[field_key] = values[field_key][:-1]
            continue

        if 32 <= key <= 126:
            char = chr(key)
            if field_key == "discount":
                if not char.isdigit():
                    continue
                val = int(values[field_key] + char)
                if val > 100:
                    continue
            values[field_key] = (values[field_key] + char)[:50]

    try:
        cv2.destroyWindow(window_name)
    except cv2.error:
        pass

    if selected["value"] != "start":
        return None

    name = values["name"].strip()
    if not name:
        print("Nama customer wajib diisi.")
        return None

    try:
        discount = int(values["discount"].strip() or "0")
    except ValueError:
        discount = default_discount

    return {
        "name": name,
        "phone": values["phone"].strip(),
        "discount": discount,
    }


def show_register_form(default_discount=0):
    return show_customer_form(
        "Registrasi Wajah Baru",
        "Masukkan nama dan diskon untuk pendaftaran member baru.",
        default_discount,
        submit_label="Lanjut Ambil Foto Wajah",
    )


def register_customer(name, phone, discount_percent, api_url, camera_index=0):
    camera = open_camera(camera_index)
    face_label = slugify(name)
    window_name = "Register Customer Face"
    response_payload = None
    frame_count = 0
    gray_frame = None
    faces = []
    face_samples = []
    saved_paths = []
    status_message = "Hadapkan wajah ke kamera, lalu klik Ambil Foto."
    action = {"value": None}

    buttons = [
        {
            "label": "Ambil Foto (C)",
            "value": "capture",
            "rect": (310, 505, 450, 555),
            "color": COLOR_PRIMARY,
            "border": COLOR_PRIMARY,
            "text_color": (255, 255, 255),
            "font_scale": 0.50,
        },
        {
            "label": "Simpan & Daftar",
            "value": "save",
            "rect": (465, 505, 615, 555),
            "color": COLOR_ACCENT,
            "border": COLOR_ACCENT,
            "text_color": (255, 255, 255),
            "font_scale": 0.50,
        },
        {
            "label": "Batal (Q)",
            "value": "back",
            "rect": (630, 505, 715, 555),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.50,
        },
    ]

    def on_mouse(event, x, y, _flags, _params):
        if event == cv2.EVENT_LBUTTONDOWN:
            action["value"] = button_at_position(buttons, x, y)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)

    while True:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1

        if frame_count % 3 == 1:
            gray_frame, faces = face_detection(frame)

        # Pad frame to add bottom control dock
        h, w = frame.shape[:2]
        canvas = cv2.copyMakeBorder(frame, 0, 95, 0, 0, cv2.BORDER_CONSTANT, value=COLOR_BG)

        # Draw bottom dock
        draw_round_rect(canvas, (14, h + 10, w - 14, h + 85), COLOR_PANEL, 16, -1, COLOR_BORDER)

        # Status chips
        chip_color = COLOR_ACCENT if len(faces) else COLOR_MUTED
        chip_soft = COLOR_ACCENT_SOFT if len(faces) else COLOR_SURFACE
        draw_status_chip(canvas, f"{len(faces)} Wajah Terdeteksi", (24, h + 22, 210, h + 52), chip_color, chip_soft)
        draw_status_chip(canvas, f"{len(saved_paths)}/{REGISTER_SAMPLE_COUNT} Sampel", (220, h + 22, 340, h + 52), COLOR_PRIMARY, COLOR_PRIMARY_SOFT)

        cv2.putText(
            canvas,
            f"Member: {name[:24]} ({discount_percent}% OFF)",
            (24, h + 74),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            COLOR_TEXT,
            1,
            cv2.LINE_AA,
        )

        for x, y, fw, fh in faces:
            cv2.rectangle(canvas, (x, y), (x + fw, y + fh), COLOR_PRIMARY, 2)

        # Draw dock buttons
        for btn in buttons:
            # Offset buttons to match frame width if needed
            draw_menu_button(canvas, btn)

        cv2.imshow(window_name, canvas)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27) or action["value"] == "back":
            break

        if key == ord("c") or action["value"] == "capture":
            action["value"] = None
            selected_face = find_largest_face(faces)
            if selected_face is None or gray_frame is None:
                print("Wajah belum terdeteksi. Coba hadapkan wajah ke kamera.")
                continue

            x, y, fw, fh = selected_face
            face_roi = frame[y : y + fh, x : x + fw].copy()
            saved_path = save_face_sample(face_roi, face_label)
            face_samples.append(face_roi)
            saved_paths.append(saved_path)
            print(f"Sampel {len(saved_paths)} tersimpan: {saved_path}")
            continue

        if key == ord("s") or action["value"] == "save":
            action["value"] = None
            if not face_samples:
                print("Belum ada sampel wajah. Capture minimal 1 sampel dulu.")
                continue

            # Save to local metadata
            meta = load_members_metadata()
            meta[face_label] = {
                "name": name,
                "phone": phone,
                "discount": discount_percent,
            }
            save_members_metadata(meta)

            try:
                rebuild_embeddings()
            except RuntimeError as exc:
                print(f"Gagal memperbarui embedding: {exc}")
                continue

            face_roi = face_samples[0]
            try:
                embedding = create_embedding(face_roi).tolist()
                response_payload = send_register_customer(
                    name=name,
                    phone=phone,
                    discount_percent=discount_percent,
                    face_image=face_roi,
                    face_label=face_label,
                    face_embedding=embedding,
                    consent_confirmed=True,
                    api_url=api_url,
                )
                print("Customer berhasil didaftarkan ke Laravel & tersimpan lokal.")
            except Exception as exc:
                print(f"{len(saved_paths)} sampel wajah tersimpan lokal (sinkron Laravel pending: {exc}).")
            break

    close_window(camera)
    return response_payload


def run_recognition(camera_index=0):
    try:
        known_faces = load_known_faces(rebuild_if_needed=True)
    except RuntimeError as exc:
        print(f"Recognition tidak dapat dimulai: {exc}")
        return

    camera = open_camera(camera_index)
    window_name = "Pingkal Face Recognition"
    frame_count = 0
    detections = []
    liveness = MotionLivenessChallenge()
    action = {"value": None}

    buttons = [
        {
            "label": "Kembali (Q)",
            "value": "back",
            "rect": (500, 505, 620, 555),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.50,
        },
    ]

    def on_mouse(event, x, y, _flags, _params):
        if event == cv2.EVENT_LBUTTONDOWN:
            action["value"] = button_at_position(buttons, x, y)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)

    members_meta = load_members_metadata()

    while True:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1

        if frame_count % 4 == 1:
            _gray_frame, faces = face_detection(frame)
            detections = []

            for x, y, fw, fh in faces:
                face_roi = frame[y : y + fh, x : x + fw]
                try:
                    label, score = recognize_face(face_roi, known_faces)
                except RuntimeError as exc:
                    label, score = "Unknown", 1.0
                liveness_passed = liveness.update((x, y, fw, fh))
                detections.append((x, y, fw, fh, label, score, liveness_passed))

        for x, y, fw, fh, label, score, liveness_passed in detections:
            is_known = label != "Unknown"
            box_color = COLOR_PRIMARY if is_known else (120, 120, 128)

            cv2.rectangle(frame, (x, y), (x + fw, y + fh), box_color, 2)

            info = members_meta.get(label, {})
            display_name = info.get("name") or display_face_label(label)
            discount = info.get("discount")

            if is_known:
                similarity = max(0.0, min(1.0, 1.0 - float(score))) * 100
                disc_text = f" | {discount}% OFF" if discount else ""
                badge_text = f"{display_name} ({similarity:.0f}%{disc_text})"
                cv2.rectangle(frame, (x, y - 28), (x + len(badge_text) * 11 + 10, y), box_color, -1)
                cv2.putText(frame, badge_text, (x + 6, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
                notify_member_detected(label, score, liveness_passed)
            else:
                cv2.rectangle(frame, (x, y - 24), (x + 100, y), box_color, -1)
                cv2.putText(frame, "Unknown", (x + 6, y - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        h, w = frame.shape[:2]
        canvas = cv2.copyMakeBorder(frame, 0, 90, 0, 0, cv2.BORDER_CONSTANT, value=COLOR_BG)

        # Bottom Panel
        draw_round_rect(canvas, (14, h + 10, w - 14, h + 80), COLOR_PANEL, 14, -1, COLOR_BORDER)
        rec_count = sum(1 for d in detections if d[4] != "Unknown")
        chip_col = COLOR_ACCENT if rec_count else COLOR_PRIMARY
        chip_soft = COLOR_ACCENT_SOFT if rec_count else COLOR_PRIMARY_SOFT
        chip_msg = f"{rec_count} Member Terdeteksi" if rec_count else "Scanning Wajah..."
        draw_status_chip(canvas, chip_msg, (24, h + 22, 230, h + 52), chip_col, chip_soft)
        cv2.putText(
            canvas,
            f"Terdaftar: {known_person_count()} Member | {len(known_faces)} Sampel",
            (24, h + 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            COLOR_MUTED,
            1,
            cv2.LINE_AA,
        )

        for btn in buttons:
            draw_menu_button(canvas, btn)

        cv2.imshow(window_name, canvas)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27) or action["value"] == "back":
            break

    close_window(camera)


def row_at_position(rows, x, y):
    for index, rect in enumerate(rows):
        x1, y1, x2, y2 = rect
        if x1 <= x <= x2 and y1 <= y <= y2:
            return index
    return None


def show_member_data_list():
    window_name = "Data Wajah Member"
    action = {"value": None}
    selected = {"index": 0}
    scroll = {"offset": 0}
    confirm_delete = {"value": False}
    status = {"text": "Pilih member lalu klik Edit untuk mengubah atau Hapus untuk menghapus."}
    visible_rows = 7

    # Load local metadata
    members_meta = load_members_metadata()

    # Try background fetch from Laravel for fresh info
    for face_entry in list_known_face_entries():
        lbl = face_entry["label"]
        if lbl not in members_meta:
            try:
                cust = get_customer(lbl).get("customer", {})
                if cust:
                    members_meta[lbl] = {
                        "name": cust.get("name", display_face_label(lbl)),
                        "phone": cust.get("phone", ""),
                        "discount": cust.get("discount_percent", 0),
                    }
                    save_members_metadata(members_meta)
            except Exception:
                pass

    buttons_normal = [
        {
            "label": "Hapus (D)",
            "value": "delete",
            "rect": (40, 570, 180, 620),
            "color": COLOR_DANGER_SOFT,
            "border": COLOR_DANGER,
            "text_color": COLOR_DANGER,
            "font_scale": 0.50,
            "thickness": 1,
        },
        {
            "label": "Edit Member (E)",
            "value": "edit",
            "rect": (195, 570, 365, 620),
            "color": COLOR_PRIMARY,
            "border": COLOR_PRIMARY,
            "text_color": (255, 255, 255),
            "font_scale": 0.50,
            "thickness": 1,
        },
        {
            "label": "Kembali (Q)",
            "value": "back",
            "rect": (590, 570, 720, 620),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.50,
            "thickness": 1,
        },
        {
            "label": "^ Naek",
            "value": "scroll_up",
            "rect": (590, 125, 650, 160),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_PRIMARY,
            "font_scale": 0.42,
        },
        {
            "label": "v Turun",
            "value": "scroll_down",
            "rect": (660, 125, 720, 160),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_PRIMARY,
            "font_scale": 0.42,
        },
    ]

    buttons_confirm = [
        {
            "label": "YAKIN HAPUS (Enter)",
            "value": "confirm_delete",
            "rect": (40, 570, 240, 620),
            "color": COLOR_DANGER,
            "border": COLOR_DANGER,
            "text_color": (255, 255, 255),
            "font_scale": 0.50,
            "thickness": 1,
        },
        {
            "label": "Batal (Esc)",
            "value": "cancel_delete",
            "rect": (255, 570, 380, 620),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.50,
            "thickness": 1,
        },
    ]

    row_rects = []

    def on_mouse(event, x, y, flags, _params):
        face_entries = list_known_face_entries()
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                selected["index"] = max(0, selected["index"] - 1)
            elif flags < 0:
                selected["index"] = min(max(0, len(face_entries) - 1), selected["index"] + 1)
            confirm_delete["value"] = False
            return

        if event != cv2.EVENT_LBUTTONDOWN:
            return

        # Check row click
        row_idx = row_at_position(row_rects, x, y)
        if row_idx is not None:
            selected["index"] = scroll["offset"] + row_idx
            confirm_delete["value"] = False
            return

        active_btns = buttons_confirm if confirm_delete["value"] else buttons_normal
        action["value"] = button_at_position(active_btns, x, y)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)

    while action["value"] != "back":
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            action["value"] = "back"
            break

        face_entries = list_known_face_entries()
        total_items = len(face_entries)

        if selected["index"] >= total_items:
            selected["index"] = max(0, total_items - 1)
        if selected["index"] < scroll["offset"]:
            scroll["offset"] = selected["index"]
        if selected["index"] >= scroll["offset"] + visible_rows:
            scroll["offset"] = selected["index"] - visible_rows + 1
        scroll["offset"] = max(0, min(scroll["offset"], max(0, total_items - visible_rows)))

        canvas = np.full((650, 760, 3), COLOR_BG, dtype=np.uint8)
        draw_header(canvas, "Data Member & Wajah", "Daftar member kasir yang tersimpan secara lokal dan sinkron ke Laravel.", 760)

        # Main Card Panel
        draw_round_rect(canvas, (20, 110, 740, 635), COLOR_PANEL, 16, -1, COLOR_BORDER)

        count_label = f"Total: {total_items} Member" if not total_items else f"Item {selected['index'] + 1} dari {total_items}"
        draw_status_chip(canvas, count_label, (40, 125, 220, 160), COLOR_PRIMARY, COLOR_PRIMARY_SOFT)

        cv2.putText(
            canvas,
            status["text"][:75],
            (235, 147),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            COLOR_MUTED,
            1,
            cv2.LINE_AA,
        )

        # Table Header Bar
        table_top = 175
        draw_round_rect(canvas, (40, table_top, 720, table_top + 34), COLOR_SURFACE, 8, -1, COLOR_BORDER)
        cv2.putText(canvas, "NO", (55, table_top + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(canvas, "NAMA MEMBER", (110, table_top + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(canvas, "DISKON", (450, table_top + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(canvas, "SAMPEL WAJAH", (580, table_top + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLOR_MUTED, 1, cv2.LINE_AA)

        row_rects = []
        if not face_entries:
            cv2.putText(
                canvas,
                "Belum ada data member yang tersimpan.",
                (40, table_top + 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                COLOR_MUTED,
                1,
                cv2.LINE_AA,
            )
        else:
            visible_entries = face_entries[scroll["offset"] : scroll["offset"] + visible_rows]
            for idx, face_entry in enumerate(visible_entries):
                row_y = table_top + 42 + idx * 46
                row_rect = (40, row_y, 695, row_y + 40)
                row_rects.append(row_rect)

                abs_idx = scroll["offset"] + idx
                is_selected = abs_idx == selected["index"]

                row_bg = COLOR_PRIMARY_SOFT if is_selected else COLOR_PANEL
                row_border = COLOR_PRIMARY if is_selected else COLOR_BORDER
                text_color = COLOR_PRIMARY if is_selected else COLOR_TEXT

                draw_round_rect(canvas, row_rect, row_bg, 8, -1, row_border)

                # Active left indicator bar
                if is_selected:
                    draw_round_rect(canvas, (40, row_y, 45, row_y + 40), COLOR_PRIMARY, 4, -1)

                info = members_meta.get(face_entry["label"], {})
                display_name = info.get("name") or display_face_label(face_entry["label"])
                discount = info.get("discount", 0)
                sample_count = len(face_entry["files"])

                # No
                cv2.putText(canvas, str(abs_idx + 1), (55, row_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.46, text_color, 1, cv2.LINE_AA)
                # Nama
                cv2.putText(canvas, display_name[:32], (110, row_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.50, text_color, 1 if not is_selected else 2, cv2.LINE_AA)

                # Diskon chip
                disc_color = COLOR_ACCENT if discount > 0 else COLOR_MUTED
                disc_soft = COLOR_ACCENT_SOFT if discount > 0 else COLOR_SURFACE
                disc_text = f"{discount}% Diskon" if discount > 0 else "0% Regular"
                draw_status_chip(canvas, disc_text, (445, row_y + 8, 550, row_y + 32), disc_color, disc_soft, dot=False)

                # Sampel chip
                draw_status_chip(canvas, f"{sample_count} Foto", (580, row_y + 8, 675, row_y + 32), COLOR_PRIMARY, COLOR_PRIMARY_SOFT, dot=False)

            # Modern Scrollbar
            if total_items > visible_rows:
                track_x1, track_y1, track_x2, track_y2 = 708, table_top + 42, 716, table_top + 42 + visible_rows * 46 - 6
                draw_round_rect(canvas, (track_x1, track_y1, track_x2, track_y2), COLOR_SURFACE, 4, -1, COLOR_BORDER)
                track_h = track_y2 - track_y1
                thumb_h = max(24, int(track_h * (visible_rows / total_items)))
                max_scroll = total_items - visible_rows
                ratio = scroll["offset"] / max_scroll if max_scroll > 0 else 0
                thumb_y1 = track_y1 + int(ratio * (track_h - thumb_h))
                thumb_y2 = thumb_y1 + thumb_h
                draw_round_rect(canvas, (track_x1, thumb_y1, track_x2, thumb_y2), COLOR_PRIMARY, 4, -1)

        # Bottom Actions / Confirm prompt
        if confirm_delete["value"] and face_entries:
            curr_entry = face_entries[selected["index"]]
            curr_name = members_meta.get(curr_entry["label"], {}).get("name", display_face_label(curr_entry["label"]))
            # Confirm prompt warning
            draw_round_rect(canvas, (40, 520, 720, 558), COLOR_DANGER_SOFT, 8, -1, COLOR_DANGER)
            cv2.putText(
                canvas,
                f"PERINGATAN: Yakin ingin menghapus seluruh data wajah member '{curr_name}'?",
                (55, 544),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.46,
                COLOR_DANGER,
                1,
                cv2.LINE_AA,
            )
            for btn in buttons_confirm:
                draw_menu_button(canvas, btn)
        else:
            for btn in buttons_normal:
                draw_menu_button(canvas, btn)

        cv2.imshow(window_name, canvas)
        key = cv2.waitKey(30)
        raw_key = key
        char_key = key & 0xFF if key != -1 else -1

        if char_key in (ord("q"), 27):
            if confirm_delete["value"]:
                confirm_delete["value"] = False
                continue
            action["value"] = "back"
            break

        # Up Key
        if (raw_key in (2490368, 38, 82) or char_key in (ord("w"), ord("W"))) and face_entries:
            selected["index"] = max(0, selected["index"] - 1)
            confirm_delete["value"] = False
            continue

        # Down Key
        if (raw_key in (2621440, 40, 84) or char_key in (ord("s"), ord("S"))) and face_entries:
            selected["index"] = min(len(face_entries) - 1, selected["index"] + 1)
            confirm_delete["value"] = False
            continue

        if char_key in (ord("d"), ord("D")):
            action["value"] = "delete"
        if char_key in (ord("e"), ord("E")):
            action["value"] = "edit"
        if char_key in (13, 10):
            if confirm_delete["value"]:
                action["value"] = "confirm_delete"

        if action["value"] == "scroll_up":
            action["value"] = None
            if face_entries:
                selected["index"] = max(0, selected["index"] - 1)
                confirm_delete["value"] = False
            continue

        if action["value"] == "scroll_down":
            action["value"] = None
            if face_entries:
                selected["index"] = min(len(face_entries) - 1, selected["index"] + 1)
                confirm_delete["value"] = False
            continue

        if action["value"] == "delete":
            action["value"] = None
            if not face_entries:
                status["text"] = "Tidak ada data yang bisa dihapus."
                continue
            confirm_delete["value"] = True
            status["text"] = "Konfirmasi penghapusan member terpilih."
            continue

        if action["value"] == "cancel_delete":
            action["value"] = None
            confirm_delete["value"] = False
            status["text"] = "Penghapusan dibatalkan."
            continue

        if action["value"] == "confirm_delete":
            action["value"] = None
            if confirm_delete["value"] and face_entries:
                entry_to_delete = face_entries[selected["index"]]
                del_label = entry_to_delete["label"]
                del_name = members_meta.get(del_label, {}).get("name", display_face_label(del_label))
                delete_known_face(entry_to_delete)
                confirm_delete["value"] = False
                members_meta = load_members_metadata()
                status["text"] = f"Member '{del_name}' berhasil dihapus."
            continue

        if action["value"] == "edit":
            action["value"] = None
            if not face_entries:
                status["text"] = "Tidak ada data yang bisa diedit."
                continue

            entry = face_entries[selected["index"]]
            old_label = entry["label"]

            # Load initial values from metadata or Laravel
            current_info = members_meta.get(old_label, {})
            current_name = current_info.get("name") or display_face_label(old_label)
            current_phone = current_info.get("phone", "")
            current_discount = current_info.get("discount", 0)

            # Try to get fresh data from Laravel
            try:
                remote = get_customer(old_label).get("customer", {})
                if remote:
                    current_name = remote.get("name", current_name)
                    current_phone = remote.get("phone", current_phone)
                    current_discount = remote.get("discount_percent", current_discount)
            except Exception:
                pass

            edited = show_customer_form(
                title="Edit Data Member",
                subtitle=f"ID Wajah: {old_label} | Ubah informasi nama, HP, atau diskon.",
                default_discount=current_discount,
                initial_values={
                    "name": current_name,
                    "phone": current_phone,
                    "discount": current_discount,
                },
                submit_label="Simpan Perubahan",
            )

            if edited is None:
                status["text"] = "Edit member dibatalkan."
                continue

            # Update local metadata & rename face samples if name changed
            new_label, updated_data = update_member_info(
                old_label=old_label,
                new_name=edited["name"],
                new_phone=edited["phone"],
                new_discount=edited["discount"],
            )
            members_meta = load_members_metadata()

            # Sync to Laravel
            laravel_status = ""
            try:
                update_customer(
                    old_label,
                    edited["name"],
                    edited["phone"],
                    edited["discount"],
                )
                laravel_status = " & sinkron ke Laravel"
            except Exception:
                # If not found on Laravel, attempt auto-registration with first face sample
                try:
                    matching_files = [p for p in list_known_face_files() if slugify(edited["name"]) in p.stem]
                    if matching_files:
                        face_img = cv2.imread(str(matching_files[0]))
                        if face_img is not None:
                            emb = create_embedding(face_img).tolist()
                            send_register_customer(
                                name=edited["name"],
                                phone=edited["phone"],
                                discount_percent=edited["discount"],
                                face_image=face_img,
                                face_label=new_label,
                                face_embedding=emb,
                                consent_confirmed=True,
                            )
                            laravel_status = " & didaftarkan ke Laravel"
                except Exception:
                    laravel_status = " (disimpan lokal)"

            status["text"] = f"Member '{edited['name']}' berhasil diperbarui{laravel_status}."
            continue

    try:
        cv2.destroyWindow(window_name)
    except cv2.error:
        pass


def show_visual_menu():
    window_name = "Pingkal Face Menu"
    selected = {"value": None}

    buttons = [
        {
            "label": "1. Mulai Pengenalan Wajah (Recognition)",
            "value": "1",
            "rect": (140, 150, 620, 210),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_PRIMARY,
            "font_scale": 0.54,
            "thickness": 1,
        },
        {
            "label": "2. Registrasi Member Baru (Register Face)",
            "value": "2",
            "rect": (140, 230, 620, 290),
            "color": COLOR_PRIMARY,
            "border": COLOR_PRIMARY,
            "text_color": (255, 255, 255),
            "font_scale": 0.54,
            "thickness": 1,
        },
        {
            "label": "3. Kelola Data Member (List, Edit, Hapus)",
            "value": "3",
            "rect": (140, 310, 620, 370),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_TEXT,
            "font_scale": 0.54,
            "thickness": 1,
        },
        {
            "label": "0. Keluar Aplikasi (Exit)",
            "value": "0",
            "rect": (140, 390, 620, 450),
            "color": COLOR_PANEL,
            "border": COLOR_BORDER,
            "text_color": COLOR_MUTED,
            "font_scale": 0.54,
            "thickness": 1,
        },
    ]

    def on_mouse(event, x, y, _flags, _params):
        if event == cv2.EVENT_LBUTTONDOWN:
            selected["value"] = button_at_position(buttons, x, y)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)

    while selected["value"] is None:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            selected["value"] = "0"
            break

        canvas = np.full((540, 760, 3), COLOR_BG, dtype=np.uint8)
        draw_header(canvas, "PINGKAL KASIR & FACE AI", "Sistem Pengenalan Wajah & Loyalty Member Kasir", 760)

        # Center Card Panel
        draw_round_rect(canvas, (100, 118, 660, 480), COLOR_PANEL, 16, -1, COLOR_BORDER)

        for btn in buttons:
            draw_menu_button(canvas, btn)

        # Footer status
        draw_status_chip(canvas, f"{known_person_count()} Member Terdaftar", (140, 492, 330, 525), COLOR_ACCENT, COLOR_ACCENT_SOFT)
        cv2.putText(
            canvas,
            "Tekan angka 1, 2, 3, atau 0 di keyboard",
            (420, 513),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            COLOR_MUTED,
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(window_name, canvas)
        key = cv2.waitKey(30) & 0xFF

        if key in (ord("1"), ord("2"), ord("3"), ord("0")):
            selected["value"] = chr(key)
        elif key in (ord("q"), 27):
            selected["value"] = "0"

    try:
        cv2.destroyWindow(window_name)
    except cv2.error:
        pass
    return selected["value"]


def run_terminal_menu(args):
    while True:
        choice = show_visual_menu()

        if choice == "1":
            run_recognition(args.camera_index)
            continue

        if choice == "2":
            form_data = show_register_form(args.discount)
            if form_data is None:
                continue

            register_customer(
                form_data["name"],
                form_data["phone"],
                form_data["discount"],
                args.api_url,
                args.camera_index,
            )
            continue

        if choice == "3":
            show_member_data_list()
            continue

        if choice == "0":
            print("Keluar dari Pingkal Face AI.")
            return

        print("Menu tidak valid.")
