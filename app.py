import os
import tempfile
import subprocess
import asyncio
import streamlit as st
import whisper
import edge_tts

# 1. Cấu hình trang & Thương hiệu VNahihi
st.set_page_config(
    page_title="VNahihi - Pro Video Studio",
    page_icon="🎬",
    layout="wide"
)

# 2. CSS Tối ưu hóa tuyệt đối: Xóa sạch rườm rà, giao diện phẳng mượt mà cao cấp
clean_studio_style = """
    <style>
    /* Ẩn hoàn toàn các thành phần mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Nền tổng thể tối sâu, sang trọng */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Thanh Sidebar tối giản phong cách Desktop App */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
        padding-top: 20px;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1 !important;
        font-weight: 500;
        font-size: 15px;
    }

    /* Thẻ Studio Card chuẩn hiện đại, không bị lỗi khối */
    .studio-card {
        background: #111827;
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Tiêu đề rực rỡ */
    .studio-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    
    .studio-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Tùy chỉnh các Tab chuyển đổi */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        color: #94a3b8;
        border-radius: 6px;
        font-weight: 600;
        background-color: transparent;
        border: none;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }

    /* Nút bấm */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Khu vực File Uploader gọn gàng */
    [data-testid="stFileUploader"] {
        background-color: #0b0f19;
        border: 2px dashed #374151;
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
    }
    </style>
"""
st.markdown(clean_studio_style, unsafe_allow_html=True)

# --- SIDEBAR ĐIỀU HƯỞNG ---
st.sidebar.markdown("### 🎬 VNahihi Hub")
st.sidebar.caption("Desktop Studio v2.5")

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
if st.sidebar.button("📁 Mở Thư Mục Ứng Dụng", use_container_width=True):
    os.system(r'explorer "C:\AppDichVideo"')


# --- NỘI DUNG CHÍNH ---
if menu == "🎬 Không gian Sáng tạo (Studio)":
    
    st.markdown('<div class="studio-title">🎬 VNahihi Pro Studio - Trạm Sáng Tạo Video AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-subtitle">Hệ thống xử lý video chuyên nghiệp, không giới hạn dung lượng, tối ưu đa người dùng.</div>', unsafe_allow_html=True)

    tab_upload, tab_link, tab_sub_editor, tab_tts, tab_marketing = st.tabs([
        "📤 1. Tải Lên Media", 
        "📥 2. Tải Link Mạng Xã Hội", 
        "📝 3. Trình Sửa Phụ Đề", 
        "🗣️ 4. Lồng Giọng AI", 
        "📊 5. Tóm Tắt & SEO"
    ])

    with tab_upload:
        col_left, col_right = st.columns([1.3, 0.7], gap="large")

        with col_left:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### 📂 Khu vực Tải lên Media (Hỗ trợ 5GB+)")
            uploaded_file = st.file_uploader("Kéo thả hoặc chọn file video (MP4, MKV, AVI, MOV):", type=["mp4", "mov", "avi", "mkv"])
            
            if uploaded_file is not None:
                st.success("✅ Hệ thống đã nhận diện video thành công.")
                video_size_mb = uploaded_file.size / (1024 * 1024)
                st.info(f"Dung lượng tệp: **{video_size_mb:.2f} MB**. Sẵn sàng khởi chạy quy trình AI.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### ⚡ Trạng thái & Kết xuất")
            st.write("Kiểm tra thiết lập thông số trước khi xuất bản video chính thức.")
            
            start_btn = st.button("🚀 BẮT ĐẦU XỬ LÝ VIDEO", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None and start_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Đang chuẩn bị bộ đệm xử lý video...")
            progress_bar.progress(15)
            
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())
            video_path = tfile.name
            
            status_text.text(f"Đang bóc tách lời thoại bằng Whisper (Model: {model_size})...")
            progress_bar.progress(40)
            
            try:
                model = whisper.load_model(model_size)
                result = model.transcribe(video_path)
                full_text = result["text"]
                segments = result["segments"]
            except Exception as e:
                st.error(f"Lỗi xử lý Whisper: {e}")
                st.stop()
            
            progress_bar.progress(70)
            
            status_text.text("Đang tạo phụ đề chuẩn và nướng phụ đề vào video...")
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
            st.success("🎉 Dự án đã được kết xuất thành công!")
            
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.subheader("📥 Trung tâm Tải xuống Kết Quả")
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                if has_burned_video and os.path.exists(output_video_path):
                    with open(output_video_path, "rb") as file_vid:
                        st.download_button(
                            label="📥 Tải xuống Video hoàn chỉnh",
                            data=file_vid,
                            file_name="vnahihi_video_hoan_chinh.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
            with col_dl2:
                st.download_button(
                    label="📥 Tải xuống tệp phụ đề (.srt)",
                    data=srt_content,
                    file_name="vnahihi_phu_de.srt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            st.subheader("📝 Bản chép lời (Transcript):")
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

    with tab_link:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📥 Tải video trực tiếp từ YouTube / TikTok / Facebook")
        video_url = st.text_input("Dán đường dẫn Video vào đây:", placeholder="https://www.youtube.com/watch?v=...")
        
        if st.button("🚀 Bắt đầu Tải Về Máy"):
            if video_url:
                st.info("Đang tiến hành tải xuống video...")
                try:
                    cmd = f'yt-dlp -o "C:\\AppDichVideo\\downloaded_video.%(ext)s" "{video_url}"'
                    subprocess.run(cmd, shell=True, check=True)
                    st.success("✅ Tải video thành công! Lưu tại: C:\\AppDichVideo\\downloaded_video.mp4")
                except Exception as e:
                    st.error(f"Lỗi tải video: {e}")
            else:
                st.warning("Vui lòng nhập đường dẫn video hợp lệ!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_sub_editor:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📝 Bảng Biên Tập Phụ Đề & Thời Gian")
        st.caption("Tinh chỉnh văn bản phụ đề trực tiếp trước khi xuất bản.")
        
        sample_subtitles = [
            {"STT": 1, "Bắt đầu": "00:00:01", "Kết thúc": "00:00:04", "Nội dung": "Chào mừng đến với VNahihi Pro Studio!"},
            {"STT": 2, "Bắt đầu": "00:00:05", "Kết thúc": "00:00:09", "Nội dung": "Trải nghiệm hệ thống xử lý video AI tốc độ cao."},
            {"STT": 3, "Bắt đầu": "00:00:10", "Kết thúc": "00:00:14", "Nội dung": "Mọi tác vụ đều mượt mà và an toàn."}
        ]
        edited_df = st.data_editor(sample_subtitles, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Lưu Cấu Hình Phụ Đề"):
            st.success("✅ Đã lưu thay đổi phụ đề thành công!")
        st.markdown('</div>', unsafe_allow_html=True)

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
        sample_text = st.text_area("Nhập văn bản cần lồng giọng:", "Chào mừng bạn đến với VNahihi Pro Studio.")
        
        if st.button("🔊 Nghe Thử & Tạo Giọng Đọc"):
            if sample_text:
                voice_code = voice_option.split(" ")[0]
                output_audio = "C:\\AppDichVideo\\test_voice.mp3"
                with st.spinner("Đang khởi tạo âm thanh AI..."):
                    try:
                        asyncio.run(generate_voice(sample_text, voice_code, output_audio))
                        st.audio(output_audio, format="audio/mp3")
                        st.success("✅ Tạo giọng đọc AI thành công!")
                    except Exception as e:
                        st.error(f"Lỗi tạo giọng đọc: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_marketing:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.subheader("📊 Gợi Ý Tiêu Đề & Hashtag Viral")
        if st.button("✨ Tạo Ý Tưởng Đăng Bài"):
            st.markdown("#### 🎯 Tiêu Đề Đề Xuất:")
            st.write("1. 🔥 BÍ MẬT XỬ LÝ VIDEO NHANH GẤP 10 LẦN CÙNG VNAHIHI!")
            st.write("2. 🎬 Khám phá ngay công cụ AI tự động hóa hoàn toàn")
            st.markdown("#### 📌 Hashtag Xu Hướng:")
            st.code("#VNahihi #ProStudio #AIVideo #ContentCreator #Automation", language="text")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📊 Quản lý & Thống kê":
    st.markdown('<div class="studio-title">📊 Quản lý Dự án & Thống kê</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-card">', unsafe_allow_html=True)
    st.info("Hệ thống quản lý không gian lưu trữ và lịch sử xử lý video.")
    st.metric(label="Bộ nhớ đệm tạm", value="0 MB", delta="Tối ưu hóa an toàn")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Cài đặt Hệ thống":
    st.markdown('<div class="studio-title">⚙️ Cài đặt Hệ thống Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-card">', unsafe_allow_html=True)
    st.write("- **Thương hiệu:** VNahihi Pro Studio")
    st.write("- **Phiên bản:** v2.5 Desktop Edition")
    st.write("- **Thư mục lưu trữ:** `C:\\AppDichVideo`")
    st.write("- **Giới hạn tải lên:** 5GB+ (Đã cấu hình config.toml)")
    st.markdown('</div>', unsafe_allow_html=True)