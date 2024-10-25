from loguru import logger

from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, File, status

from src.my_yolo import (
    convert_bytes_to_image,
    convert_image_to_bytes,
    detect_faces_in_image,
    draw_detection_boxes
)

# Initialize FastAPI app with metadata
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8008", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root endpoint to API documentation"""
    return RedirectResponse("/docs")


@app.get('/health', status_code=status.HTTP_200_OK, tags=["System"])
async def check_health():
    """
    Check API health status

    Returns:
        dict: Health status and message
    """
    return {
        'status': 'healthy',
        'message': 'Face Detection API is operational'
    }


@app.post(
    "/detect/faces/image",
    summary="Detect faces and return annotated image",
    response_description="JPEG image with detected faces highlighted"
)
async def detect_faces_image(file: bytes = File(..., description="Image file to analyze (JPEG, PNG)",)):
    """
    Analyze an image and return it with detected faces highlighted

    Args:
        file (bytes): Image file in bytes

    Returns:
        StreamingResponse: JPEG image with detected faces highlighted

    Raises:
        HTTPException: If image processing fails
    """
    try:
        # Convert bytes to image
        input_image = convert_bytes_to_image(file)

        # Perform face detection
        predictions = detect_faces_in_image(input_image)

        # Draw detection boxes on image
        annotated_image = draw_detection_boxes(
            image=input_image,
            detections=predictions
        )

        # Convert back to bytes for response
        image_bytes = convert_image_to_bytes(annotated_image)

        logger.info(f"Successfully processed image with {len(predictions)} detections")

        return StreamingResponse(
            content=image_bytes,
            media_type="image/jpeg",
            headers={
                "X-Total-Faces": str(len(predictions))
            }
        )

    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
