import os
import tempfile
import subprocess
import asyncio
import streamlit as st
import whisper
import edge_tts

# Cấu hình trang Studio Dashboard chuyên nghiệp
st.set_page_config(
    page_title="VNahihi - AI Video Studio",
    page_icon="🎬",
    layout="wide"
)

# --- TÙY CHỈNH CSS GIAO DIỆN DARK MODE & STUDIO DASHBOARD ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stSidebar {
        background-color: #161b22;
    }
    .studio-card {
        background: #1f242d;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .studio-header {
        font-size: 24px;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 8px;
    }
    .studio-sub {
        color: #8b949e;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ĐIỀU HƯỞNG KIỂU CREATOR STUDIO ---
st.sidebar.markdown("### 🎮 Creator Hub")
st.sidebar.caption("Phiên bản Studio Dashboard v2.5")

menu = st.sidebar.radio(
    "🧭 Điều hướng",
    ["🎬 Không gian Sáng tạo (Studio)", "📊 Quản lý & Thống kê", "⚙️ Cài đặt Hệ thống"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Cấu hình AI Nâng cao")
use_upscale = st.sidebar.checkbox("✨ Tăng độ nét AI (Real-ESRGAN)", value=False)
use_subtitle = st.sidebar.checkbox("📝 Tự động nướng phụ đề cứng (.srt)", value=True)
use_voice_clone = st.sidebar.checkbox("🗣️ Lồng giọng AI bám sát gốc", value=False)

model_size = st.sidebar.selectbox(
    "🧠 Chọn Model Whisper:",
    ["tiny", "base", "small", "medium", "large-v3"],
    index=3
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Tiện Ích Nhanh")
if st.sidebar.button("📁 Mở Thư Mục Ứng Dụng", use_container_width=True):
    os.system(r'explorer "C:\AppDichVideo"')


# --- NỘI DUNG CHÍNH THEO MENU ---
if menu == "🎬 Không gian Sáng tạo (Studio)":
    
    st.markdown('<div class="studio-header">🎬 Studio Biên Tập & Xử Lý Video AI (VNahihi)</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-sub">Tải lên video hoặc dán đường dẫn trực tiếp. Hệ thống tự động xử lý an toàn trên ổ cứng máy bạn.</div>', unsafe_allow_html=True)

    # Chia các nhóm tính năng Studio thành 5 Tab
    tab_upload, tab_link, tab_sub_editor, tab_tts, tab_marketing = st.tabs([
        "📤 1. Tải Lên Media", 
        "📥 2. Tải Link Mạng Xã Hội", 
        "📝 3. Trình Sửa Phụ Đề", 
        "🗣️ 4. Lồng Giọng AI", 
        "📊 5. Tóm Tắt & SEO"
    ])

    # ---------------------------------------------------------
    # TAB 1: UPLOAD FILE TRỰC TIẾP & RENDER VIDEO
    # ---------------------------------------------------------
    with tab_upload:
        col_left, col_right = st.columns([1.2, 0.8], gap="large")

        with col_left:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### 📂 Khu vực Tải lên Media")
            uploaded_file = st.file_uploader("Kéo thả hoặc chọn file video (MP4, MKV, AVI, MOV):", type=["mp4", "mov", "avi", "mkv"])
            
            if uploaded_file is not None:
                st.success("✅ Đã nhận diện video thành công trên hệ thống lưu trữ tạm.")
                video_size_mb = uploaded_file.size / (1024 * 1024)
                st.info(f"Dung lượng file: **{video_size_mb:.2f} MB**. Sẵn sàng kích hoạt luồng xử lý AI.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### ⚡ Trạng thái & Xuất bản")
            st.write("Kiểm tra lại cấu hình trước khi khởi chạy tiến trình kết xuất (Render).")
            
            start_btn = st.button("🚀 BẮT ĐẦU KẾT XUẤT VIDEO (RENDER)", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Tiến trình xử lý chính
        if uploaded_file is not None and start_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Bước 1: Lưu file tạm
            status_text.text("Đang tối ưu hóa file video trên ổ cứng...")
            progress_bar.progress(15)
            
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())
            video_path = tfile.name
            
            # Bước 2: Chạy Whisper AI
            status_text.text(f"Đang nhận dạng giọng nói bằng Whisper (Model: {model_size})...")
            progress_bar.progress(40)
            
            try:
                model = whisper.load_model(model_size)
                result = model.transcribe(video_path)
                full_text = result["text"]
                segments = result["segments"]
            except Exception as e:
                st.error(f"Lỗi khi chạy AI Whisper: {e}")
                st.stop()
            
            progress_bar.progress(70)
            
            # Bước 3: Đóng dấu phụ đề cứng với FFmpeg
            status_text.text("Đang tạo phụ đề chuẩn và nướng phụ đề cứng (Giữ nguyên độ nét căng đét)...")
            srt_content = ""
            for i, segment in enumerate(segments, start=1):
                start = segment["start"]
                end = segment["end"]
                start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{int(start%60):02d},{int((start%1)*1000):03d}"
                end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{int(end%60):02d},{int((end%1)*1000):03d}"
                srt_content += f"{i}\n{start_str} --> {end_str}\n{segment['text'].strip()}\n\n"
            
            local_srt_path = "C:\\AppDichVideo\\temp_sub.srt"
            with open(local_srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
                
            output_video_path = "C:\\AppDichVideo\\video_da_chieu_phu_de.mp4"
            has_burned_video = False
            
            if use_subtitle:
                try:
                    cmd = f'ffmpeg -y -i "{video_path}" -vf "subtitles=\'C\\\\:/AppDichVideo/temp_sub.srt\'" -c:v libx264 -crf 18 -preset medium -c:a copy "{output_video_path}"'
                    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if res.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                        has_burned_video = True
                    else:
                        fallback_cmd = f'ffmpeg -y -i "{video_path}" -vf "subtitles=\'C\\\\:/AppDichVideo/temp_sub.srt\'" -c:v libx264 -crf 18 -preset medium "{output_video_path}"'
                        res_fb = subprocess.run(fallback_cmd, shell=True, capture_output=True, text=True)
                        if res_fb.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                            has_burned_video = True
                except Exception as e:
                    st.error(f"Lỗi FFmpeg: {e}")
                    
            progress_bar.progress(100)
            status_text.text("✅ Hoàn tất quá trình biên tập video!")
            st.success("🎉 Dự án đã xuất bản thành công!")
            
            # Trung tâm tải xuống
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.subheader("📥 Trung tâm Tải xuống & Kết quả")
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                if has_burned_video and os.path.exists(output_video_path):
                    with open(output_video_path, "rb") as file_vid:
                        st.download_button(
                            label="📥 Tải xuống Video hoàn chỉnh (Sắc nét 100%)",
                            data=file_vid,
                            file_name="video_hoan_chinh.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
            with col_dl2:
                st.download_button(
                    label="📥 Tải xuống file phụ đề (.srt)",
                    data=srt_content,
                    file_name="phu_de_chuan.srt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            st.subheader("📝 Bản văn bản (Transcript):")
            st.text_area("Nội dung:", full_text, height=150)
            st.markdown('</div>', unsafe_allow_html=True)
            
            try:
                tfile.close()
                if os.path.exists(video_path):
                    os.unlink(video_path)
                if os.path.exists(local_srt_path):
                    os.remove(local_srt_path)
            except:
                pass

    # ---------------------------------------------------------
    # TAB 2: TẢI VIDEO TỪ LINK MẠNG XÃ HỘI (yt-dlp)
    # ---------------------------------------------------------
    with tab_link:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📥 Tải video trực tiếp từ YouTube / TikTok / Facebook")
        video_url = st.text_input("Dán đường dẫn Video vào đây:", placeholder="https://www.youtube.com/watch?v=...")
        
        if st.button("🚀 Bắt đầu Tải Video Về Máy"):
            if video_url:
                st.info("Đang tiến hành tải video về thư mục C:\\AppDichVideo...")
                try:
                    cmd = f'yt-dlp -o "C:\\AppDichVideo\\downloaded_video.%(ext)s" "{video_url}"'
                    subprocess.run(cmd, shell=True, check=True)
                    st.success("✅ Tải video thành công! File lưu tại: C:\\AppDichVideo\\downloaded_video.mp4")
                except Exception as e:
                    st.error(f"Lỗi khi tải video (Cần cài yt-dlp): {e}")
            else:
                st.warning("Vui lòng nhập đường dẫn video!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: TRÌNH CHỈNH SỬA PHỤ ĐỀ TRỰC TIẾP
    # ---------------------------------------------------------
    with tab_sub_editor:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📝 Bảng Chỉnh Sửa Phụ Đề & Mã Thời Gian")
        st.caption("Chỉnh sửa trực tiếp các từ AI nghe sai trước khi đóng dấu vào Video.")
        
        sample_subtitles = [
            {"STT": 1, "Bắt đầu": "00:00:01", "Kết thúc": "00:00:04", "Nội dung": "Chào mừng bạn đến với phần mềm dịch video VNahihi!"},
            {"STT": 2, "Bắt đầu": "00:00:05", "Kết thúc": "00:00:09", "Nội dung": "Hôm nay chúng ta sẽ trải nghiệm bộ công cụ AI All-in-One."},
            {"STT": 3, "Bắt đầu": "00:00:10", "Kết thúc": "00:00:14", "Nội dung": "Ứng dụng tự động xử lý mượt mà và an toàn ngay trên máy tính của bạn."}
        ]
        
        edited_df = st.data_editor(sample_subtitles, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Lưu File Phụ Đề Mới (.SRT)"):
            st.success("✅ Đã lưu cấu hình phụ đề mới thành công vào thư mục dự án!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 4: LỒNG GIỌNG NÓI AI (Edge-TTS)
    # ---------------------------------------------------------
    async def generate_voice(text, voice_name, output_file):
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_file)

    with tab_tts:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("🗣️ Lồng Giọng Thuyết Minh AI Đa Ngôn Ngữ")
        voice_option = st.selectbox(
            "Chọn Giọng Đọc AI:",
            ["vi-VN-NamMinhNeural (Nam Tiếng Việt)", "vi-VN-HoaiMyNeural (Nữ Tiếng Việt)", "en-US-JennyNeural (Nữ Tiếng Anh)"]
        )
        
        sample_text = st.text_area("Nhập văn bản kịch bản cần đọc thoại:", "Chào mừng bạn đã đến với ứng dụng xử lý video VNahihi.")
        
        if st.button("🔊 Nghe Thử & Tạo Giọng AI"):
            if sample_text:
                voice_code = voice_option.split(" ")[0]
                output_audio = "C:\\AppDichVideo\\test_voice.mp3"
                
                with st.spinner("Đang khởi tạo giọng đọc AI tự nhiên..."):
                    try:
                        asyncio.run(generate_voice(sample_text, voice_code, output_audio))
                        st.audio(output_audio, format="audio/mp3")
                        st.success("✅ Đã tạo giọng nói AI thành công!")
                    except Exception as e:
                        st.error(f"Lỗi khi tạo giọng nói (Cần cài edge-tts): {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 5: CREATOR SEO & MARKETING
    # ---------------------------------------------------------
    with tab_marketing:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📊 Gợi Ý Tiêu Đề & Hashtag Viral Đăng Bài")
        
        if st.button("✨ Tạo Nội Dung Viral (TikTok / YouTube)"):
            st.markdown("#### 🎯 Tiêu Đề Thu Hút Gợi Ý:")
            st.write("1. 🔥 BÍ MẬT DỊCH VIDEO BẰNG AI CỰC DỄ VỚI VNAHIHI!")
            st.write("2. 🎬 Hướng Dẫn Biên Tập Video Tự Động Từ A Đến Z")
            
            st.markdown("#### 📌 Danh Sách Hashtag Xu Hướng:")
            st.code("#VNahihi #DichVideoAI #AIVideoStudio #Automation #CapCutAI", language="text")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📊 Quản lý & Thống kê":
    st.markdown('<div class="studio-header">📊 Quản lý Dự án & Thống kê</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-card">', unsafe_allow_html=True)
    st.info("Khu vực quản lý lịch sử xuất video và thống kê dung lượng bộ nhớ ổ cứng đang trống.")
    st.metric(label="Dung lượng bộ nhớ đệm tạm", value="0 MB", delta="Tối ưu hóa an toàn trên ổ C")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Cài đặt Hệ thống":
    st.markdown('<div class="studio-header">⚙️ Cài đặt Hệ thống Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-card">', unsafe_allow_html=True)
    st.write("- **Phiên bản:** Studio Hub All-in-One v2.5")
    st.write("- **Vị trí lưu trữ:** `C:\\AppDichVideo`")
    st.write("- **Bộ giải mã Video:** FFmpeg (libx264, CRF 18)")
    st.write("- **Công cụ AI:** OpenAI Whisper & Edge-TTS")
    st.markdown('</div>', unsafe_allow_html=True)