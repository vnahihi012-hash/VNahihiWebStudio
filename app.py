import os
import tempfile
import subprocess
import asyncio
import streamlit as st
import whisper
import edge_tts

# 1. Cấu hình tiêu đề trang mang thương hiệu VNahihi
st.set_page_config(
    page_title="VNahihi - AI Video Studio",
    page_icon="🎬",
    layout="wide"
)

# Chèn thẻ Meta HTML để đổi tên khi chia sẻ link lên mạng xã hội/chat
st.markdown("""
    <head>
        <meta property="title" content="VNahihi - AI Video Studio">
        <meta property="og:title" content="VNahihi - AI Video Studio">
        <meta property="og:description" content="Hệ thống biên tập và xử lý video thông minh VNahihi Studio">
    </head>
""", unsafe_allow_html=True)

# 2. Tùy chỉnh CSS: Ẩn hoàn toàn menu 3 chấm, chân trang và header của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- SIDEBAR ĐIỀU HƯỞNG ---
st.sidebar.markdown("### 🎬 VNahihi Hub")
st.sidebar.caption("Phiên bản Creator Studio v2.5")

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
    
    st.markdown('<div class="studio-header">🎬 VNahihi Studio - Biên Tập & Xử Lý Video AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-sub">Tải lên video hoặc dán đường dẫn trực tiếp. Hệ thống VNahihi tự động xử lý an toàn trên ổ cứng máy bạn.</div>', unsafe_allow_html=True)

    tab_upload, tab_link, tab_sub_editor, tab_tts, tab_marketing = st.tabs([
        "📤 1. Tải Lên Media", 
        "📥 2. Tải Link Mạng Xã Hội", 
        "📝 3. Trình Sửa Phụ Đề", 
        "🗣️ 4. Lồng Giọng AI", 
        "📊 5. Tóm Tắt & SEO"
    ])

    with tab_upload:
        col_left, col_right = st.columns([1.2, 0.8], gap="large")

        with col_left:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### 📂 Khu vực Tải lên Media")
            uploaded_file = st.file_uploader("Kéo thả hoặc chọn file video (MP4, MKV, AVI, MOV):", type=["mp4", "mov", "avi", "mkv"])
            
            if uploaded_file is not None:
                st.success("✅ VNahihi đã nhận diện video thành công trên hệ thống lưu trữ tạm.")
                video_size_mb = uploaded_file.size / (1024 * 1024)
                st.info(f"Dung lượng file: **{video_size_mb:.2f} MB**. Sẵn sàng kích hoạt luồng xử lý AI.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.markdown("### ⚡ Trạng thái & Xuất bản")
            st.write("Kiểm tra lại cấu hình trước khi khởi chạy tiến trình kết xuất (Render).")
            
            start_btn = st.button("🚀 BẮT ĐẦU KẾT XUẤT VIDEO (RENDER)", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None and start_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("VNahihi đang tối ưu hóa file video trên ổ cứng...")
            progress_bar.progress(15)
            
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())
            video_path = tfile.name
            
            status_text.text(f"VNahihi AI đang nhận dạng giọng nói bằng Whisper (Model: {model_size})...")
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
            
            status_text.text("VNahihi đang tạo phụ đề chuẩn và nướng phụ đề cứng...")
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
            status_text.text("✅ VNahihi đã hoàn tất quá trình biên tập video!")
            st.success("🎉 Dự án VNahihi đã xuất bản thành công!")
            
            st.markdown('<div class="studio-card">', unsafe_allow_html=True)
            st.subheader("📥 Trung tâm Tải xuống & Kết quả")
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                if has_burned_video and os.path.exists(output_video_path):
                    with open(output_video_path, "rb") as file_vid:
                        st.download_button(
                            label="📥 Tải xuống Video hoàn chỉnh (VNahihi)",
                            data=file_vid,
                            file_name="vnahihi_video_hoan_chinh.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
            with col_dl2:
                st.download_button(
                    label="📥 Tải xuống file phụ đề (.srt)",
                    data=srt_content,
                    file_name="vnahihi_phu_de.srt",
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
                if os