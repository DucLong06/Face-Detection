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
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from loguru import logger
import socket
from contextlib import closing
from opentelemetry.sdk.trace.sampling import ALWAYS_ON


# Get configuration from environment variables
JAEGER_HOST = os.getenv("JAEGER_HOST", "jaeger-jaeger.tracing.svc.cluster.local")
JAEGER_PORT = int(os.getenv("JAEGER_PORT", "6831"))

set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "face-detection"}),
        sampler=ALWAYS_ON
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name=JAEGER_HOST,
    agent_port=JAEGER_PORT,
    transport_format="thrift-compact"
)
span_processor = BatchSpanProcessor(jaeger_exporter)
get_tracer_provider().add_span_processor(span_processor)

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


def check_jaeger_connection(host: str, port: int):
    """Test connection to Jaeger host and port"""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            sock.settimeout(2)  # 2 seconds timeout
            sock.connect((host, port))
            return True
    except (socket.error, socket.timeout):
        return False


@app.get('/check_jaeger')
async def check_jaeger():
    # Try to extract host from full domain
    try:
        host = JAEGER_HOST.split('.')[0]  # Get first part of domain
    except:
        host = JAEGER_HOST

    # Check connection
    is_connected = check_jaeger_connection(JAEGER_HOST, JAEGER_PORT)

    # Create detailed status
    status = {
        'jaeger_host': JAEGER_HOST,
        'jaeger_port': JAEGER_PORT,
        'connection_status': 'connected' if is_connected else 'disconnected',
        'service_name': "face-detection",
        'details': {
            'can_connect': is_connected,
            'protocol': 'UDP',
            'exporter_type': 'thrift'
        }
    }

    # Add trace ID if connected
    if is_connected:
        try:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("check_jaeger_connection") as span:
                status['current_trace_id'] = format(span.get_span_context().trace_id, '016x')
        except Exception as e:
            status['trace_error'] = str(e)

    return status


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
    logger.info(f"Processing time: {execution_time:.2f} seconds")

    return StreamingResponse(
        content=image_bytes,
        media_type="image/jpeg",
        headers={
            "X-Total-Faces": str(len(predictions)),
            "X-Processing-Time": f"{execution_time:.2f}"
        }
    )
