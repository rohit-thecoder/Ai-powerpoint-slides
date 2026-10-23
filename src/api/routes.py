
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.agents.content_extractor import ContentExtractor
from src.agents.summarizer import Summarizer
from src.agents.slide_generator import SlideGenerator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "output"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB


@router.get("/")
def home():
    return {
        "message": "AI PowerPoint Generator API is running."
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Save an uploaded document and return its stored filename."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF, DOCX, TXT, or CSV file.",
        )

    stored_name = f"{uuid.uuid4().hex}{extension}"
    destination = UPLOAD_DIR / stored_name
    total_bytes = 0

    try:
        with destination.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="The maximum upload size is 20 MB.",
                    )

                output_file.write(chunk)

    except HTTPException:
        destination.unlink(missing_ok=True)
        raise

    except OSError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded file.",
        ) from exc

    finally:
        await file.close()

    return {
        "message": "File uploaded successfully.",
        "filename": stored_name,
        "size_bytes": total_bytes,
    }


@router.post("/generate/{filename}")
def generate_presentation(filename: str):
    """Generate a topic-specific PowerPoint from an uploaded file."""

    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    source_path = UPLOAD_DIR / filename

    if not source_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found.",
        )

    if source_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format.",
        )

    try:
        # Step 1: Extract the source document text.
        extractor = ContentExtractor(directory=str(UPLOAD_DIR))
        document_text = extractor.extract_from_file(str(source_path))

        if not isinstance(document_text, str) or not document_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text was extracted.",
            )

        # Step 2: Generate a dynamic presentation plan with Gemini.
        summarizer = Summarizer()
        plan = summarizer.summarize_text(document_text)

        presentation_title = plan["presentation_title"]
        slides = plan["slides"]

        # Step 3: Generate the PowerPoint.
        generator = SlideGenerator(
            output_directory=str(OUTPUT_DIR)
        )

        output_filename = f"{source_path.stem}_presentation.pptx"

        output_path = generator.create_slide_deck(
            title=presentation_title,
            slides=slides,
            filename=output_filename,
        )

        return {
            "message": "Presentation generated successfully.",
            "presentation_title": presentation_title,
            "filename": output_path.name,
            "slide_count": len(slides) + 1,
            "download_url": f"/download/{output_path.name}",
            "slides": slides,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Generation error: {type(exc).__name__}: {exc}")

        raise HTTPException(
            status_code=500,
            detail=(
                "Presentation generation failed. "
                "Check the backend terminal for details."
            ),
        ) from exc


@router.get("/download/{filename}")
def download_presentation(filename: str):
    """Download a previously generated PowerPoint file."""

    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    if not filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=400,
            detail="Only PowerPoint files can be downloaded.",
        )

    output_path = OUTPUT_DIR / filename

    if not output_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Presentation not found.",
        )

    return FileResponse(
        path=str(output_path),
        filename=filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
    )
