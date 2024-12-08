from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File
import uvicorn
from src.my_yolo import (
    convert_bytes_to_image,
    convert_image_to_bytes,
    detect_faces_in_image,
    draw_detection_boxes
)
import time
import os
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Get configuration from environment variables
JAEGER_HOST = os.getenv("OTEL_EXPORTER_JAEGER_AGENT_HOST", "localhost")
JAEGER_PORT = int(os.getenv("OTEL_EXPORTER_JAEGER_AGENT_PORT", "6831"))

# Setup basic Jaeger tracing
provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name=JAEGER_HOST,
    agent_port=JAEGER_PORT,
)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

# Initialize FastAPI app
app = FastAPI()

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health')
async def check_health():
    return {'status': 'healthy'}


@app.post("/detect/faces/image")
async def detect_faces_image(file: bytes = File(...)):
    start_time = time.time()

    input_image = convert_bytes_to_image(file)
    predictions = detect_faces_in_image(input_image)
    annotated_image = draw_detection_boxes(
        image=input_image,
        detections=predictions
    )
    image_bytes = convert_image_to_bytes(annotated_image)

    execution_time = time.time() - start_time
    print(f"Processing time: {execution_time:.2f} seconds")

    return StreamingResponse(
        content=image_bytes,
        media_type="image/jpeg",
        headers={
            "X-Total-Faces": str(len(predictions)),
            "X-Processing-Time": f"{execution_time:.2f}"
        }
    )

if __name__ == "__main__":
    print(f"Connecting to Jaeger at {JAEGER_HOST}:{JAEGER_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
