import os
import requests
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
SUPPORTED_TYPES = ["pdf", "docx", "txt", "csv"]

st.set_page_config(
    page_title="Slidecraft | AI Presentation Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# Safe HTML Render Helper
# --------------------------------------------------

def render_html(html_str: str):
    """Render HTML safely without triggering Streamlit's markdown code-block parser."""
    if hasattr(st, "html"):
        st.html(html_str)
    else:
        st.markdown(html_str, unsafe_allow_html=True)


# --------------------------------------------------
# Premium UI Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --background: #F7F8FA;
        --surface: #FFFFFF;
        --text: #172033;
        --muted: #737D90;
        --border: #E7EAF0;
        --accent: #4259E8;
        --accent-hover: #3348CD;
        --soft-blue: #EEF1FF;
        --success: #16845B;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.7px;
        color: var(--text);
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2.8rem;
    }

    .brand {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 23px;
        letter-spacing: -1px;
        color: var(--text);
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: var(--accent);
        color: white;
        margin-right: 9px;
        font-size: 19px;
    }

    .top-label {
        font-size: 12px;
        color: var(--muted);
        border: 1px solid var(--border);
        background: white;
        padding: 7px 12px;
        border-radius: 20px;
    }

    .hero-eyebrow {
        color: var(--accent);
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: clamp(34px, 5vw, 51px);
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -2.2px;
        margin: 0;
        color: var(--text);
    }

    .hero-title span {
        color: var(--accent);
    }

    .hero-subtitle {
        max-width: 610px;
        margin-top: 17px;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.8;
    }

    .section-heading {
        font-family: 'Manrope', sans-serif;
        font-weight: 750;
        font-size: 18px;
        margin-bottom: 5px;
        color: var(--text);
    }

    .section-description {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.7;
        margin-bottom: 20px;
    }

    .panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 25px;
        margin-top: 28px;
    }

    .upload-symbol {
        width: 54px;
        height: 54px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 14px auto;
        background: var(--soft-blue);
        border-radius: 15px;
        font-size: 25px;
        color: var(--accent);
    }

    .upload-title {
        font-family: 'Manrope', sans-serif;
        font-weight: 750;
        font-size: 17px;
        text-align: center;
        color: var(--text);
    }

    .upload-caption {
        text-align: center;
        color: var(--muted);
        font-size: 12px;
        margin-top: 7px;
        margin-bottom: 18px;
    }

    [data-testid="stFileUploader"] {
        border: 1px dashed #CDD3E0;
        border-radius: 13px;
        background: #FBFCFE;
        padding: 12px;
    }

    [data-testid="stFileUploader"] section {
        padding: 10px;
    }

    [data-testid="stFileUploader"] button {
        border-radius: 8px !important;
    }

    .format-label {
        color: var(--muted);
        font-size: 11px;
        text-align: center;
        margin-top: 12px;
    }

    .feature {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 15px 0;
        border-bottom: 1px solid var(--border);
    }

    .feature:last-child {
        border-bottom: none;
    }

    .feature-icon {
        width: 36px;
        height: 36px;
        min-width: 36px;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #F0F2FF;
        font-size: 17px;
    }

    .feature-title {
        color: var(--text);
        font-size: 13px;
        font-weight: 650;
        margin-bottom: 4px;
    }

    .feature-copy {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
    }

    .stButton > button {
        width: 100%;
        min-height: 49px;
        border-radius: 11px;
        background: var(--accent);
        color: white;
        border: 1px solid var(--accent);
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: var(--accent-hover);
        border-color: var(--accent-hover);
        color: white;
    }

    .stButton > button:disabled {
        background: #B8C0EE;
        color: white;
    }

    .stDownloadButton > button {
        width: 100%;
        min-height: 49px;
        border-radius: 11px;
        background: var(--accent);
        color: white;
        border: none;
        font-weight: 650;
    }

    .stDownloadButton > button:hover {
        background: var(--accent-hover);
        color: white;
    }

    .result-header {
        background: #F0FBF6;
        border: 1px solid #D7F1E4;
        border-radius: 13px;
        padding: 16px;
        margin: 12px 0 20px 0;
    }

    .result-title {
        color: #166B4B;
        font-weight: 700;
        font-size: 15px;
    }

    .result-copy {
        color: #467A65;
        font-size: 12px;
        margin-top: 5px;
    }

    .slide-card {
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 17px;
        background: white;
        margin-bottom: 12px;
    }

    .slide-number {
        color: var(--accent);
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .slide-title {
        font-family: 'Manrope', sans-serif;
        font-weight: 750;
        font-size: 16px;
        color: var(--text);
        margin-bottom: 9px;
    }

    .slide-bullet {
        color: #566176;
        font-size: 12px;
        line-height: 1.7;
        margin: 5px 0;
    }

    .footer {
        border-top: 1px solid var(--border);
        padding-top: 20px;
        margin-top: 45px;
        text-align: center;
        color: #9098A7;
        font-size: 11px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            letter-spacing: -1.4px;
        }

        .panel {
            padding: 17px;
        }

        .top-label {
            font-size: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Header
# --------------------------------------------------

render_html(
    """
    <div class="topbar">
        <div class="brand">
            <span class="brand-mark">✦</span>slidecraft
        </div>
        <div class="top-label">AI PRESENTATION STUDIO</div>
    </div>
    """
)

# --------------------------------------------------
# Hero Section
# --------------------------------------------------

render_html(
    """
    <div class="hero-eyebrow">DOCUMENT TO PRESENTATION</div>
    <div class="hero-title">
        Your ideas, turned into<br>
        <span>beautiful slides.</span>
    </div>
    <div class="hero-subtitle">
        Transform documents into clear, structured PowerPoint
        presentations. Upload your content, let AI organize the
        key insights, and download your presentation.
    </div>
    """
)

# --------------------------------------------------
# Main Layout
# --------------------------------------------------

upload_col, info_col = st.columns([1.45, 1], gap="large")

with upload_col:
    render_html(
        """
        <div class="panel">
            <div class="section-heading">Create a presentation</div>
            <div class="section-description">
                Start with a document. Your content will be used
                to build a presentation tailored to its subject.
            </div>
            <div class="upload-symbol">↑</div>
            <div class="upload-title">Upload your document</div>
            <div class="upload-caption">
                Select a file from your computer to get started.
            </div>
        </div>
        """
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=SUPPORTED_TYPES,
        label_visibility="collapsed",
        help="Supported formats: PDF, DOCX, TXT and CSV.",
    )

    if uploaded_file:
        size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.caption(f"Selected: **{uploaded_file.name}** · {size_mb:.2f} MB")

    render_html(
        """
        <div class="format-label">
            SUPPORTED FORMATS &nbsp; PDF · DOCX · TXT · CSV
        </div>
        """
    )

    generate_clicked = st.button(
        "✦  Generate presentation",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

with info_col:
    render_html(
        """
        <div class="panel">
            <div class="section-heading">From document to deck</div>
            <div class="section-description">
                A simple workflow, powered by AI.
            </div>

            <div class="feature">
                <div class="feature-icon">↗</div>
                <div>
                    <div class="feature-title">Smart content extraction</div>
                    <div class="feature-copy">
                        Extract information from your supported
                        documents without manually copying text.
                    </div>
                </div>
            </div>

            <div class="feature">
                <div class="feature-icon">✧</div>
                <div>
                    <div class="feature-title">AI-powered structure</div>
                    <div class="feature-copy">
                        Turn key information into slide titles
                        and concise, topic-specific bullet points.
                    </div>
                </div>
            </div>

            <div class="feature">
                <div class="feature-icon">▤</div>
                <div>
                    <div class="feature-title">PowerPoint export</div>
                    <div class="feature-copy">
                        Generate a downloadable PPTX file
                        ready for further editing.
                    </div>
                </div>
            </div>
        </div>
        """
    )

# --------------------------------------------------
# Upload, Generate and Download
# --------------------------------------------------

if generate_clicked and uploaded_file is not None:
    try:
        with st.spinner("Uploading your document..."):
            upload_response = requests.post(
                f"{API_BASE_URL}/upload",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                },
                timeout=120,
            )

        if not upload_response.ok:
            st.error(f"Upload failed: {upload_response.text[:500]}")
            st.stop()

        upload_data = upload_response.json()
        filename = upload_data.get("filename")

        if not filename:
            st.error("The server did not return an uploaded filename.")
            st.stop()

        with st.spinner("Analyzing content and building your slides..."):
            generate_response = requests.post(
                f"{API_BASE_URL}/generate/{filename}",
                timeout=600,
            )

        if not generate_response.ok:
            st.error(f"Presentation generation failed: {generate_response.text[:1000]}")
            st.stop()

        result = generate_response.json()

        download_url = result.get("download_url")
        output_filename = result.get("filename", "generated_presentation.pptx")

        if not download_url:
            st.error("The server generated a response without a download URL.")
            st.stop()

        with st.spinner("Preparing your PowerPoint download..."):
            download_response = requests.get(
                f"{API_BASE_URL}{download_url}",
                timeout=120,
            )

        if not download_response.ok:
            st.error("Could not retrieve the generated PowerPoint.")
            st.stop()

        ppt_bytes = download_response.content

        if not ppt_bytes:
            st.error("The generated PowerPoint file is empty.")
            st.stop()

        st.session_state["presentation_result"] = result
        st.session_state["presentation_bytes"] = ppt_bytes
        st.session_state["presentation_filename"] = output_filename

    except requests.RequestException as error:
        st.error(
            f"Could not connect to the backend. Make sure FastAPI is running on {API_BASE_URL}."
        )
        st.caption(str(error))

# --------------------------------------------------
# Results and Slide Preview
# --------------------------------------------------

if "presentation_bytes" in st.session_state:
    result = st.session_state["presentation_result"]
    ppt_bytes = st.session_state["presentation_bytes"]
    output_filename = st.session_state["presentation_filename"]

    st.markdown("---")

    render_html(
        """
        <div class="result-header">
            <div class="result-title">
                ✓ &nbsp; Your presentation is ready
            </div>
            <div class="result-copy">
                Your PowerPoint has been generated successfully.
                Download it below.
            </div>
        </div>
        """
    )

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric("Total slides", result.get("slide_count", "—"))

    with metric_col2:
        st.metric("File size", f"{len(ppt_bytes) / (1024 * 1024):.2f} MB")

    st.download_button(
        label="↓  Download PowerPoint (.pptx)",
        data=ppt_bytes,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
        key="download_presentation",
    )

    slides = result.get("slides", [])

    if slides:
        with st.expander("Preview generated slide content", expanded=True):
            for index, slide in enumerate(slides, start=1):
                slide_title = slide.get("title", f"Slide {index}")
                bullets = slide.get("bullets", [])

                bullet_html = "".join(
                    f'<div class="slide-bullet">• {bullet}</div>'
                    for bullet in bullets
                )

                card_html = f"""
                <div class="slide-card">
                    <div class="slide-number">SLIDE {index}</div>
                    <div class="slide-title">{slide_title}</div>
                    {bullet_html}
                </div>
                """

                render_html(card_html)

# --------------------------------------------------
# Footer
# --------------------------------------------------

render_html(
    """
    <div class="footer">
        SLIDECRAFT &nbsp;·&nbsp; AI PRESENTATION STUDIO
        <br><br>
        Turn knowledge into presentations.
    </div>
    """
)