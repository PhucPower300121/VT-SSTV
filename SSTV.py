import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import numpy as np
import sounddevice as sd
from pysstv.color import MartinM1
import time

# Cấu hình màu sắc Dark Mode cực suy
DARK_BG = "#121212"
CARD_BG = "#1E1E1E"
ACCENT = "#BB86FC"
TEXT_COLOR = "#E0E0E0"

class GenzSSTV:
    def __init__(self, root):
        self.root = root
        self.root.title("VT-SSTV 3.9.1 stable")
        self.root.geometry("600x650+30-50")  # Đặt vị trí cao hơn: width x height + x + y
        self.root.configure(bg=DARK_BG)

        # Biến trạng thái RX
        self.rx_running = False
        self.sync_counter = 0
        self.rx_state = "IDLE"
        self.current_line = 0
        self.current_col = 0
        self.color_channel = 0 # 0:G, 1:B, 2:R

        # Style cho Notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD_BG, foreground=TEXT_COLOR, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "black")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_tx = tk.Frame(self.notebook, bg=DARK_BG)
        self.tab_rx = tk.Frame(self.notebook, bg=DARK_BG)
        self.tab_about = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.tab_tx, text="  Transmit (TX)  ")
        self.notebook.add(self.tab_rx, text="  Receive (RX)  ")
        self.notebook.add(self.tab_about, text="  About  ")

        self.setup_tx_ui()
        self.setup_rx_ui()
        self.setup_about_ui()

    def setup_tx_ui(self):
        lbl = tk.Label(self.tab_tx, text="Transmit (TX)", fg=ACCENT, bg=DARK_BG, font=('Arial', 14, 'bold'))
        lbl.pack(pady=20)
        self.canvas_tx = tk.Canvas(self.tab_tx, width=320, height=240, bg=CARD_BG, highlightthickness=0)
        self.canvas_tx.pack(pady=10)
        
        # Call sign input frame
        callsign_frame = tk.LabelFrame(self.tab_tx, text="Call Sign", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=8)
        callsign_frame.pack(pady=10, fill="x", padx=20)
        
        # Call sign input
        input_frame = tk.Frame(callsign_frame, bg=DARK_BG)
        input_frame.pack(fill="x", pady=5)
        tk.Label(input_frame, text="Call sign:", bg=DARK_BG, fg=TEXT_COLOR).pack(side="left", padx=5)
        self.callsign_var = tk.StringVar(value="")
        entry = tk.Entry(input_frame, textvariable=self.callsign_var, bg=CARD_BG, fg=TEXT_COLOR, width=20)
        entry.pack(side="left", padx=5, fill="x", expand=True)
        # Bind event để update preview khi nhập call sign
        self.callsign_var.trace("w", lambda *args: self.update_tx_preview())
        
        # Position dropdown
        pos_frame = tk.Frame(callsign_frame, bg=DARK_BG)
        pos_frame.pack(fill="x", pady=5)
        tk.Label(pos_frame, text="Position:", bg=DARK_BG, fg=TEXT_COLOR).pack(side="left", padx=5)
        self.callsign_pos_var = tk.StringVar(value="top-left")
        pos_combo = ttk.Combobox(pos_frame, textvariable=self.callsign_pos_var, state="readonly", width=17, values=["top-left", "bottom-left"])
        pos_combo.pack(side="left", padx=5)
        # Bind event để update preview khi thay đổi vị trí
        self.callsign_pos_var.trace("w", lambda *args: self.update_tx_preview())
        
        btn_frame = tk.Frame(self.tab_tx, bg=DARK_BG)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Select Image", command=self.load_tx_image, bg=CARD_BG, fg=TEXT_COLOR, width=15).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Play Audio", command=self.start_tx_thread, bg=ACCENT, fg="black", width=15).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Save .WAV File", command=self.save_wav, bg="#03DAC6", fg="black", width=15).grid(row=1, column=0, columnspan=2, pady=10)

    def setup_rx_ui(self):
        lbl = tk.Label(self.tab_rx, text="Receive (RX)", fg=ACCENT, bg=DARK_BG, font=('Arial', 14, 'bold'))
        lbl.pack(pady=20)
        self.canvas_rx = tk.Canvas(self.tab_rx, width=320, height=240, bg=CARD_BG, highlightthickness=0)
        self.canvas_rx.pack(pady=10)
        source_frame = tk.LabelFrame(self.tab_rx, text="Source", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=10)
        source_frame.pack(pady=10, fill="x", padx=20)
        self.rx_source = tk.StringVar(value="mic")
        tk.Radiobutton(source_frame, text="Microphone (Realtime)", variable=self.rx_source, value="mic", bg=DARK_BG, fg=TEXT_COLOR, selectcolor=DARK_BG).pack(anchor="w")
        tk.Radiobutton(source_frame, text="From .WAV file", variable=self.rx_source, value="file", bg=DARK_BG, fg=TEXT_COLOR, selectcolor=DARK_BG).pack(anchor="w")
        # Device selection for microphone
        device_frame = tk.Frame(self.tab_rx, bg=DARK_BG)
        device_frame.pack(pady=6, fill="x", padx=20)
        tk.Label(device_frame, text="Device:", bg=DARK_BG, fg=TEXT_COLOR).pack(side="left")
        self.rx_device_var = tk.StringVar()
        self.rx_device_combo = ttk.Combobox(device_frame, textvariable=self.rx_device_var, state="readonly", width=48)
        self.rx_device_combo.pack(side="left", padx=6)
        tk.Button(device_frame, text="Refresh", command=self.refresh_input_devices, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left", padx=6)
        tk.Button(self.tab_rx, text="START RECEIVING", command=self.start_rx_process, bg=ACCENT, fg="black", font=('Arial', 10, 'bold'), height=2).pack(pady=20)
        # nút xuất ảnh sẽ hiện khi đã decode đủ 256 dòng
        self.btn_export = tk.Button(self.tab_rx, text="Export Image", command=self.export_rx_image,
                                    bg="#03DAC6", fg="black", width=15, state="disabled")
        self.btn_export.pack(pady=5)
        # populate device list
        try:
            self.refresh_input_devices()
        except Exception:
            pass

    def refresh_input_devices(self):
        """Cập nhật danh sách thiết bị input (micro) cho combobox."""
        try:
            devs = sd.query_devices()
            inputs = []
            for i, d in enumerate(devs):
                if d.get('max_input_channels', 0) > 0:
                    name = d.get('name', 'Unknown')
                    inputs.append(f"{i}: {name}")
            # set combobox values
            try:
                self.rx_device_combo['values'] = inputs
            except Exception:
                pass
            # chọn mặc định nếu có
            if inputs:
                try:
                    default_dev = sd.default.device
                    if isinstance(default_dev, (list, tuple)):
                        default_in = default_dev[0]
                    else:
                        default_in = default_dev
                    sel = next((v for v in inputs if v.startswith(f"{default_in}:")), inputs[0])
                except Exception:
                    sel = inputs[0]
                self.rx_device_var.set(sel)
            else:
                self.rx_device_var.set("")
        except Exception:
            try:
                self.rx_device_combo['values'] = []
            except Exception:
                pass
            self.rx_device_var.set("")

    def setup_about_ui(self):
        """Giao diện tab About với thông tin phần mềm."""
        main_frame = tk.Frame(self.tab_about, bg=DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="VT-SSTV 3.9 - Slow Scan Television", 
                        fg=ACCENT, bg=DARK_BG, font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Version info
        version_frame = tk.LabelFrame(main_frame, text="Version", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=8)
        version_frame.pack(fill="x", pady=10)
        tk.Label(version_frame, text="Version: 3.9.1 stable", bg=DARK_BG, fg=TEXT_COLOR).pack(anchor="w", pady=5)
        
        # License info
        license_frame = tk.LabelFrame(main_frame, text="License", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=8)
        license_frame.pack(fill="x", pady=10)
        tk.Label(license_frame, text="Licensed under: GNU General Public License v3 (GPLv3)", 
                bg=DARK_BG, fg=TEXT_COLOR).pack(anchor="w", pady=5)
        
        # Description
        desc_frame = tk.LabelFrame(main_frame, text="About", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=8)
        desc_frame.pack(fill="both", expand=True, pady=10)
        
        desc_text = tk.Text(desc_frame, bg=CARD_BG, fg=TEXT_COLOR, height=8, width=60, 
                           relief=tk.FLAT, wrap=tk.WORD, font=('Arial', 10))
        desc_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        about_text = """VT-SSTV is a modern implementation of Slow Scan Television (SSTV) for transmitting and receiving images over radio frequencies.

Features:
• Transmit images with Martin M1 SSTV mode
• Receive SSTV signals in real-time or from WAV files
• Support for call sign overlay
• Audio sample rate auto-detection
• Dark mode UI for comfortable usage"""
        
        desc_text.insert("1.0", about_text)
        desc_text.config(state="disabled")
        
        # GitHub link
        github_frame = tk.LabelFrame(main_frame, text="GitHub", bg=DARK_BG, fg=TEXT_COLOR, padx=10, pady=8)
        github_frame.pack(fill="x", pady=10)
        tk.Label(github_frame, text="Repository: ", bg=DARK_BG, fg=TEXT_COLOR).pack(anchor="w", pady=5)
        github_link = tk.Label(github_frame, text="https://github.com/PhucPower300121/VT-SSTV/", bg=DARK_BG, fg=ACCENT, 
                              font=('Arial', 10, 'underline'), cursor="hand2")
        github_link.pack(anchor="w", pady=5, padx=10)
        github_link.bind("<Button-1>", lambda e: self.open_github_link())

    # --- TX LOGIC (GIỮ NGUYÊN) ---
    def open_github_link(self):
        """Mở link GitHub trong trình duyệt mặc định."""
        import webbrowser
        webbrowser.open("https://github.com/PhucPower300121/VT-SSTV/")

    def ensure_tx_size(self, img: Image.Image) -> Image.Image:
        """Scale/crop image to SSTV transmit size (320×256).

        Nếu ảnh nhập vào không đúng kích thước, resize mềm và trả về
        bản đã chuẩn. Giữ nguyên nếu đã vừa.
        """
        if img.size != (320, 256):
            return img.resize((320, 256))
        return img

    def draw_callsign_on_image(self, img: Image.Image) -> Image.Image:
        """Vẽ call sign lên ảnh với chữ đen, viền trắng (theo chuẩn SSTV quốc tế)."""
        callsign = self.callsign_var.get().strip()
        if not callsign:  # Nếu call sign trống thì không vẽ
            return img
        
        # Tạo copy để không làm hỏng ảnh gốc
        img_with_callsign = img.copy()
        draw = ImageDraw.Draw(img_with_callsign)
        
        # Cố gắng dùng font lớn; nếu không có thì dùng default
        try:
            # Tìm font system có sẵn
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # Lấy vị trí từ dropdown
        position = self.callsign_pos_var.get()
        
        # Tính toán tọa độ
        if position == "top-left":
            x, y = 5, 5
        else:  # bottom-left
            y = img.height - 30
            x = 5
        
        # Vẽ viền trắng: vẽ text 4 lần quanh vị trí để tạo hiệu ứng border
        offset = 2
        stroke_color = "white"
        text_color = "black"
        
        for adj_x in [-offset, 0, offset]:
            for adj_y in [-offset, 0, offset]:
                if adj_x == 0 and adj_y == 0:
                    continue
                draw.text((x + adj_x, y + adj_y), callsign, font=font, fill=stroke_color)
        
        # Vẽ chữ đen chính
        draw.text((x, y), callsign, font=font, fill=text_color)
        
        return img_with_callsign

    def load_tx_image(self):
        path = filedialog.askopenfilename()
        if path:
            raw_img = Image.open(path)
            # convert + đảm bảo cỡ 320x256
            prepared = self.ensure_tx_size(raw_img.convert('RGB'))
            self.img_to_send = prepared
            self.update_tx_preview()

    def update_tx_preview(self):
        """Cập nhật preview ảnh trên canvas với call sign."""
        if not hasattr(self, 'img_to_send'):
            return
        # Vẽ call sign lên ảnh
        img_with_callsign = self.draw_callsign_on_image(self.img_to_send)
        # Hiển thị trên canvas (resize để vừa khung 320x240)
        img_display = img_with_callsign.resize((320, 240))
        self.photo_tx = ImageTk.PhotoImage(img_display)
        self.canvas_tx.delete("all")
        self.canvas_tx.create_image(160, 120, image=self.photo_tx)

    def start_tx_thread(self):
        threading.Thread(target=self.transmit_logic, daemon=True).start()

    def transmit_logic(self):
        if not hasattr(self, 'img_to_send'): return
        # Apply call sign before transmission
        img_final = self.draw_callsign_on_image(self.img_to_send)
        sample_rate = 44100
        sstv = MartinM1(img_final, sample_rate, 16)
        all_samples = []
        for freq, msec in sstv.gen_freq_bits():
            num_samples = int(sample_rate * msec / 1000.0)
            t = np.linspace(0, msec / 1000.0, num_samples, endpoint=False)
            samples = 0.5 * np.sin(2 * np.pi * freq * t)
            all_samples.append(samples)
        audio_data = np.concatenate(all_samples).astype(np.float32)
        sd.play(audio_data, sample_rate)
        sd.wait()

    def save_wav(self):
        if not hasattr(self, 'img_to_send'): return
        path = filedialog.asksaveasfilename(defaultextension=".wav")
        if path:
            # Apply call sign before saving
            img_final = self.draw_callsign_on_image(self.img_to_send)
            sstv = MartinM1(img_final, 44100, 16)
            sstv.write_wav(path)

    # --- RX LOGIC (FIXED) ---
    def start_rx_process(self):
        self.rx_running = True
        # reset nút xuất mỗi lần chạy lại
        try:
            self.btn_export.config(state="disabled")
        except Exception:
            pass
        self.current_line = 0
        self.current_col = 0
        self.color_channel = 0
        self.rx_state = "IDLE"
        self.rx_img = Image.new('RGB', (320, 256), (18, 18, 18))
        self.draw_rx = self.rx_img.load()
        # reset buffer stream để decoder mới chạy ngon
        self.stream_buffer = np.array([], dtype=np.float32)
        self.decode_ptr = 0.0
        # trạng thái channel/gap
        self.channel = 0
        self.channel_pos = 0
        self.gap_remaining = 0.0
        self.last_sample_rate = None

        # Reset các biến trạng thái dính lại từ lần decode trước
        self.sync_counter = 0
        self.samples_since_last_sync = 0.0
        # sạch history tần số
        self.freq_buf = []
        # xóa các tham số pixel/gap cũ để tính lại khi sample rate mới
        if hasattr(self, 'pixel_samps_float'):
            del self.pixel_samps_float
        if hasattr(self, 'pixel_window'):
            del self.pixel_window
        if hasattr(self, 'gap_samples'):
            del self.gap_samples

        if self.rx_source.get() == "mic":
            # determine selected device index from combobox
            sel = self.rx_device_var.get()
            try:
                # combobox value is stored as 'index: name' or bare index
                if sel and ":" in sel:
                    dev_idx = int(sel.split(":", 1)[0])
                elif sel:
                    dev_idx = int(sel)
                else:
                    dev_idx = None
            except Exception:
                dev_idx = None
            self.selected_input_device = dev_idx
            threading.Thread(target=self.rx_mic_worker, daemon=True).start()
        else:
            path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
            if path:
                threading.Thread(target=self.rx_file_worker, args=(path,), daemon=True).start()

    def decode_freq(self, audio_chunk, sample_rate):
        # ước tần suất tức thời bằng Hilbert transform nè
        # scipy đã có sẵn, để fail thì hốt FFT cho lẹ
        # FFT xoàng dùng khi scipy ko chịu import
        if len(audio_chunk) < 4:
            return 0
        try:
            from scipy.signal import hilbert
            analytic = hilbert(audio_chunk)
            phase = np.unwrap(np.angle(analytic))
            inst_freq = np.diff(phase) * sample_rate / (2 * np.pi)
            if len(inst_freq) == 0:
                return 0
            freq = float(np.median(inst_freq))
        except Exception:
            # plan B: xài FFT cùi như hồi xưa
            window = np.hamming(len(audio_chunk))
            spectrum = np.fft.rfft(audio_chunk * window)
            freqs = np.fft.rfftfreq(len(audio_chunk), 1.0 / sample_rate)
            idx = np.argmax(np.abs(spectrum))
            freq = freqs[idx]
        # bóp tần số lại cho hợp lý
        if freq < 100 or freq > 5000:
            return 0
        return freq

    def process_audio_chunk(self, chunk, sample_rate):
        # append sample vào buffer rồi kiện qua con trỏ float nha.
        # hồi trước dùng int nên drift, vài dòng ảnh bị nghiêng như ván sóng.
        if not hasattr(self, 'stream_buffer'):
            self.stream_buffer = np.array([], dtype=np.float32)
            self.decode_ptr = 0.0
            self.last_sample_rate = sample_rate

        # ensure pixel params are recalculated if sample rate changed or uninitialized
        msec_pixel = 146.432 / 320
        prev_rate = getattr(self, 'last_sample_rate', None)
        if not hasattr(self, 'pixel_samps_float') or sample_rate != prev_rate:
            self.pixel_samps_float = sample_rate * msec_pixel / 1000.0
            self.pixel_window = max(16, int(self.pixel_samps_float * 3))
            # update gap samples whenever rate changes
            self.gap_samples = sample_rate * 0.572 / 1000.0
            self.last_sample_rate = sample_rate

        # use local copies to avoid race/access inconsistency
        pixel_samps = float(self.pixel_samps_float)
        pixel_window = int(self.pixel_window)

        self.stream_buffer = np.concatenate((self.stream_buffer, chunk))

        # băng buffer bằng con trỏ float
        if not hasattr(self, 'channel'):
            self.channel = 0
            self.channel_pos = 0
            self.gap_remaining = 0.0
        # gap_samples already set above when rate changed; ensure exists
        if not hasattr(self, 'gap_samples'):
            self.gap_samples = sample_rate * 0.572 / 1000.0
        if not hasattr(self, 'samples_since_last_sync'):
            self.samples_since_last_sync = 0.0

        # Martin M1: mỗi dòng có 3 channel * 320 pixel + 3 khoảng gap (0.572ms)
        samples_per_line = (pixel_samps * 320 * 3) + (self.gap_samples * 3)
        min_sync_spacing = samples_per_line * 0.8

        while (self.decode_ptr + pixel_window) <= len(self.stream_buffer) and self.current_line < 256:
            # đang trong gap giữa các kênh màu thì quăng mẫu qua
            if self.gap_remaining > 0:
                self.decode_ptr += pixel_samps
                self.gap_remaining -= pixel_samps
                self.samples_since_last_sync += pixel_samps
                continue

            # tính index kiểu floor; round nó nhảy loạn
            start_idx = int(self.decode_ptr)
            end_idx = start_idx + pixel_window
            segment = self.stream_buffer[start_idx:end_idx]
            freq = self.decode_freq(segment, sample_rate)
            # giữ freq thô để check sync; pixel sẽ dùng version khác
            # bản đồ pixel sẽ chặn mọi thứ ngoài dải 1500-2300
            # nhưng đừng đổi `freq` trước khi test sync 1200Hz.

            # phát hiện sync ở đầu dòng khả dĩ; chỉ chấp nhận nếu đủ mẫu
            # đã trôi từ sync trước. dùng cái này để né header lởm.
            # mấy sync header 10ms và tông 1200 vớ vẩn.
            if 1100 <= freq <= 1300 and (self.rx_state != "DATA" or (self.channel == 0 and self.channel_pos == 0)):
                self.sync_counter += 1
                # Ngưỡng sync linh hoạt: lúc IDLE cho phép bắt sync sớm để không mất
                # các dòng đầu; sau khi đã lock thì vẫn giữ spacing để chống false sync.
                required_sync_hits = 4 if self.rx_state == "IDLE" else 6
                enough_spacing = (self.rx_state == "IDLE") or (self.samples_since_last_sync >= min_sync_spacing)
                if self.sync_counter >= required_sync_hits and enough_spacing:
                    # new line begins (either first after IDLE or subsequent)
                    self.current_line = 0 if self.rx_state == "IDLE" else self.current_line
                    self.current_col = 0
                    self.channel = 0
                    self.channel_pos = 0
                    self.rx_state = "SYNC"
                    # clear any old frequency history
                    if hasattr(self, 'freq_buf'):
                        self.freq_buf.clear()
                    # prepare post-sync confirmation buffer (used to avoid mis-detecting header as data)
                    self.post_sync_buf = []
                    # after sync we will expect an initial gap
                    self.gap_remaining = self.gap_samples
                    # reset timing and realign buffer so drift doesn't accumulate
                    # drop consumed samples up to the start of the detected sync
                    consumed = int(self.decode_ptr)
                    self.stream_buffer = self.stream_buffer[consumed:]
                    self.decode_ptr = 0.0
                    self.samples_since_last_sync = 0.0
                    continue  # start over with new buffer
                # if we haven't reached the required sync count yet, advance pointer and keep looking
                self.decode_ptr += pixel_samps
                self.samples_since_last_sync += pixel_samps
                continue
            else:
                self.sync_counter = 0

            # chuyển sang DATA nếu nghe tông cao quá ngưỡng sau sync
            if self.rx_state == "SYNC":
                # Require multiple consecutive high-frequency windows after SYNC
                # to confirm real DATA start. This avoids header tones being
                # interpreted as image data and losing alignment.
                if not hasattr(self, 'post_sync_buf'):
                    self.post_sync_buf = []
                self.post_sync_buf.append(freq)
                if len(self.post_sync_buf) > 6:
                    self.post_sync_buf.pop(0)
                # need several windows with median >1500Hz to commit to DATA
                if len(self.post_sync_buf) >= 4 and float(np.median(self.post_sync_buf)) > 1500.0:
                    self.rx_state = "DATA"
                    self.channel = 0
                    self.channel_pos = 0
                    self.gap_remaining = self.gap_samples
                    # reset frequency history for new data line
                    if hasattr(self, 'freq_buf'):
                        self.freq_buf.clear()
                    # clear the post-sync buffer now that DATA has started
                    try:
                        del self.post_sync_buf
                    except Exception:
                        pass
                else:
                    # not confirmed yet; advance pointer and keep looking
                    self.decode_ptr += pixel_samps
                    self.samples_since_last_sync += pixel_samps
                    continue

            if self.rx_state == "DATA":
                # If we're at the start of a new line, and there's enough buffered
                # samples, decode the entire scanline in one batch from a
                # snapshot. This enforces exact 320-pixel width per channel and
                # prevents gradual drift/skew across lines.
                if self.channel == 0 and self.channel_pos == 0:
                    line_span = (pixel_samps * 320 * 3) + (self.gap_samples * 3)
                    samples_needed = int(line_span) + pixel_window
                    base_idx = int(self.decode_ptr)
                    if (len(self.stream_buffer) - base_idx) >= samples_needed:
                        line_buf = self.stream_buffer[base_idx: base_idx + samples_needed]
                        # process 3 channels sequentially from the snapshot
                        pos = 0.0  # vị trí float tích lũy

                        for ch in range(3):
                            # Martin M1 có gap nhỏ trước mỗi channel màu
                            pos += self.gap_samples
                            self.freq_buf_line = []
                            for px in range(320):
                                idx = int(pos)
                                seg = line_buf[idx: idx + pixel_window]

                                freq = self.decode_freq(seg, sample_rate)

                                if not hasattr(self, 'freq_buf_line'):
                                    self.freq_buf_line = []
                                self.freq_buf_line.append(freq)
                                if len(self.freq_buf_line) > 5:
                                    self.freq_buf_line.pop(0)

                                if px < 5:
                                    smooth_freq = freq
                                else:
                                    smooth_freq = float(np.median(self.freq_buf_line))
                                data_freq = smooth_freq
                                if data_freq < 1500 or data_freq > 2300:
                                    data_freq = 0

                                val = int((data_freq - 1500) * 255 / 800) if data_freq else 0
                                val = max(0, min(255, val))

                                r, g, b = self.draw_rx[px, self.current_line]
                                if ch == 0:
                                    g = val
                                elif ch == 1:
                                    b = val
                                else:
                                    r = val

                                self.draw_rx[px, self.current_line] = (r, g, b)

                                pos += pixel_samps  # tăng đều, KHÔNG tính lại từ đầu
                            # finished a channel
                        # advance buffer past this full line
                        consumed_line = base_idx + int(line_span)
                        self.stream_buffer = self.stream_buffer[consumed_line:]
                        self.decode_ptr = 0.0
                        # cleanup tmp line buffer
                        if hasattr(self, 'freq_buf_line'):
                            del self.freq_buf_line
                        # next line
                        self.current_line += 1
                        self.update_canvas()
                        if self.current_line >= 256:
                            self.on_rx_complete()
                            self.rx_running = False
                        # reset sync/sample counters
                        self.samples_since_last_sync = 0.0
                        self.sync_counter = 0
                        # and continue to next iteration (we consumed samples)
                        continue
                # mượt hoá tín hiệu freq, tránh cục xương noise
                if not hasattr(self, 'freq_buf'):
                    self.freq_buf = []
                self.freq_buf.append(freq)
                if len(self.freq_buf) > 5:
                    self.freq_buf.pop(0)
                # dùng median để vất outlier ra
                smooth_freq = float(np.median(self.freq_buf))

                # map freq to pixel value only if inside data band
                data_freq = smooth_freq
                if data_freq < 1500 or data_freq > 2300:
                    data_freq = 0
                val = int((data_freq - 1500) * 255 / 800) if data_freq else 0
                val = max(0, min(255, val))

                if self.current_line < 256 and self.channel_pos < 320:
                    # văng màu vào đúng channel
                    r, g, b = self.draw_rx[self.channel_pos, self.current_line]
                    if self.channel == 0:
                        g = val
                    elif self.channel == 1:
                        b = val
                    elif self.channel == 2:
                        r = val
                    self.draw_rx[self.channel_pos, self.current_line] = (r, g, b)
                    # giữ current_col cho mấy thứ cũ/vọc bug
                    self.current_col = self.channel_pos
                    self.channel_pos += 1

                    # xong kênh thì quất qua gap/kênh tiếp theo
                    if self.channel_pos >= 320:
                        self.gap_remaining = self.gap_samples
                        self.channel_pos = 0
                        self.current_col = 0
                        if self.channel == 2:
                            # xong kênh đỏ -> lên dòng kế
                            self.current_line += 1
                            self.update_canvas()
                            # nếu đã nhận đủ 256 dòng thì bật nút xuất và tắt rx
                            if self.current_line >= 256:
                                self.on_rx_complete()
                                self.rx_running = False
                            self.channel = 0
                        else:
                            self.channel += 1

            self.decode_ptr += pixel_samps
            self.samples_since_last_sync += pixel_samps

        # trim consumed samples from buffer
        consumed = int(self.decode_ptr)
        if consumed > 0:
            self.stream_buffer = self.stream_buffer[consumed:]
            self.decode_ptr -= consumed

    def on_rx_complete(self):
        # gọi khi đã decode xong dòng 256
        try:
            self.btn_export.config(state="normal")
        except Exception:
            pass

    def export_rx_image(self):
        if not hasattr(self, 'rx_img'):
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG image", "*.png"), ("All files", "*")])
        if path:
            self.rx_img.save(path)

    def rx_file_worker(self, path):
        import wave
        with wave.open(path, 'rb') as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
            # infer dtype from sampwidth
            if sampwidth == 1:
                dtype = np.uint8
                offset = True
            elif sampwidth == 2:
                dtype = np.int16
                offset = False
            elif sampwidth == 4:
                dtype = np.int32
                offset = False
            else:
                dtype = np.int16
                offset = False
            audio = np.frombuffer(frames, dtype=dtype)
            if n_channels > 1:
                audio = audio.reshape(-1, n_channels)[:, 0]
            # normalize to float32 in -1..1
            if offset:
                audio_data = (audio.astype(np.float32) - 128.0) / 128.0
            else:
                maxval = float(2 ** (8 * sampwidth - 1))
                audio_data = audio.astype(np.float32) / maxval

            # quăng cả sóng vào decoder theo block vừa đủ; buffer sẽ lo align
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if not self.rx_running:
                    break
                chunk = audio_data[i:i+chunk_size]
                self.process_audio_chunk(chunk, sample_rate)

    def rx_mic_worker(self):
        # open input stream using selected device (if provided) and use actual samplerate
        chunk_size = 1024
        dev = getattr(self, 'selected_input_device', None)
        try:
            with sd.InputStream(device=dev, channels=1, dtype='float32') as stream:
                sample_rate = int(stream.samplerate)
                while self.rx_running and self.current_line < 256:
                    data, _ = stream.read(chunk_size)
                    # ensure 1-D float32
                    chunk = np.array(data, dtype=np.float32).reshape(-1)
                    self.process_audio_chunk(chunk, sample_rate)
        except Exception:
            # fallback: try default device with explicit samplerate
            try:
                sample_rate = 44100
                with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
                    while self.rx_running and self.current_line < 256:
                        data, _ = stream.read(chunk_size)
                        chunk = np.array(data, dtype=np.float32).reshape(-1)
                        self.process_audio_chunk(chunk, sample_rate)
            except Exception:
                return

    def update_canvas(self):
        # Resize nhẹ để hiển thị khớp canvas UI
        img_display = self.rx_img.resize((320, 240))
        self.photo_rx = ImageTk.PhotoImage(img_display)
        self.canvas_rx.create_image(160, 120, image=self.photo_rx)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = GenzSSTV(root)
    root.mainloop()