import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status

# Allowed image types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# Max file size — 2MB in bytes
MAX_FILE_SIZE = 2 * 1024 * 1024

# Upload directory
UPLOAD_DIR = "uploads/products"


async def save_product_image(file: UploadFile) -> str:
    """
    Validate and save uploaded product image.
    Returns the saved filename.

    Steps:
    1. Validate file type
    2. Read file and check size
    3. Generate unique filename
    4. Save to disk
    5. Return filename
    """

    # Step 1 — Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. "
                   f"Allowed: jpeg, png, webp, gif"
        )

    # Step 2 — Read file and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is 2MB. "
                   f"Your file: {len(contents) / 1024 / 1024:.2f}MB"
        )

    # Step 3 — Generate unique filename
    # uuid4() generates random unique ID
    # This prevents filename collisions
    # e.g. two users upload "phone.jpg" — no conflict
    extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"

    # Step 4 — Save to disk
    # aiofiles writes asynchronously — doesn't block event loop
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    return unique_filename


def delete_product_image(filename: str) -> None:
    """Delete image file from disk."""
    if filename:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)


def get_image_url(request, filename: str) -> str:
    """Build full URL for image."""
    if not filename:
        return None
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/uploads/products/{filename}"
