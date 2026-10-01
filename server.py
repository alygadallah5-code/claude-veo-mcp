import os
import time
import base64
import requests
from mcp.server.mcpserver import MCPServer

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("VEO_MODEL", "veo-3.1-generate-preview")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

mcp = MCPServer("Claude-Veo-3.1")

def _require_key():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured on the server.")

def _start_generation(prompt, aspect_ratio="9:16", resolution="1080p"):
    _require_key()
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
        },
    }
    r = requests.post(
        f"{BASE_URL}/models/{MODEL}:predictLongRunning",
        headers={
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["name"]

def _poll(operation_name, timeout_seconds=900):
    started = time.time()
    while time.time() - started < timeout_seconds:
        r = requests.get(
            f"{BASE_URL}/{operation_name}",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("done"):
            if "error" in data:
                raise RuntimeError(str(data["error"]))
            sample = data["response"]["generateVideoResponse"]["generatedSamples"][0]
            video = sample["video"]
            return video
        time.sleep(10)
    raise TimeoutError("Veo generation timed out. Use check_generation with the operation name.")

@mcp.tool()
def generate_video(
    prompt: str,
    aspect_ratio: str = "9:16",
    resolution: str = "1080p",
) -> dict:
    """Generate an 8-second Veo 3.1 video with native audio and return the temporary Google video URI.

    Use aspect_ratio 9:16 for Reels/TikTok/Shorts and 16:9 for YouTube/landscape.
    The prompt should describe subject, action, camera, lighting, environment, style, and audio/dialogue.
    """
    if aspect_ratio not in ("9:16", "16:9"):
        raise ValueError("aspect_ratio must be 9:16 or 16:9")
    if resolution not in ("720p", "1080p", "4k"):
        raise ValueError("resolution must be 720p, 1080p, or 4k")
    operation = _start_generation(prompt, aspect_ratio, resolution)
    video = _poll(operation)
    return {
        "status": "completed",
        "operation": operation,
        "video_uri": video.get("uri"),
        "mime_type": video.get("mimeType", "video/mp4"),
        "note": "The Google video URI is temporary. Save the video promptly.",
    }

@mcp.tool()
def start_video_generation(
    prompt: str,
    aspect_ratio: str = "9:16",
    resolution: str = "1080p",
) -> dict:
    """Start a Veo generation without waiting. Returns an operation name for check_generation."""
    if aspect_ratio not in ("9:16", "16:9"):
        raise ValueError("aspect_ratio must be 9:16 or 16:9")
    if resolution not in ("720p", "1080p", "4k"):
        raise ValueError("resolution must be 720p, 1080p, or 4k")
    operation = _start_generation(prompt, aspect_ratio, resolution)
    return {"status": "started", "operation": operation}

@mcp.tool()
def check_generation(operation: str) -> dict:
    """Check a Veo operation. If complete, returns the temporary Google video URI."""
    _require_key()
    r = requests.get(
        f"{BASE_URL}/{operation}",
        headers={"x-goog-api-key": GEMINI_API_KEY},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("done"):
        return {"status": "processing", "operation": operation}
    if "error" in data:
        return {"status": "error", "operation": operation, "error": data["error"]}
    sample = data["response"]["generateVideoResponse"]["generatedSamples"][0]
    video = sample["video"]
    return {
        "status": "completed",
        "operation": operation,
        "video_uri": video.get("uri"),
        "mime_type": video.get("mimeType", "video/mp4"),
    }

@mcp.tool()
def create_ad_video(
    product_or_brand: str,
    concept: str,
    duration_note: str = "8 seconds",
    aspect_ratio: str = "9:16",
) -> dict:
    """Turn a simple ad idea into a polished Veo prompt and generate it.

    This is optimized for short social-media ads: cinematic product shots, controlled camera movement,
    premium lighting, clear visual storytelling, and optional natural sound/dialogue.
    """
    prompt = f"""
Create a premium commercial video for: {product_or_brand}.
Concept: {concept}.
Target duration: {duration_note}.
Format: {aspect_ratio}.

Visual direction:
- Photorealistic commercial cinematography.
- Strong opening hook in the first second.
- Clear hero shot of the product/brand.
- Smooth, intentional camera movement.
- Detailed textures and realistic materials.
- Professional lighting and shallow depth of field where appropriate.
- Clean composition suitable for social media advertising.
- No random text, logos, watermarks, or distorted product packaging unless explicitly described.
- Keep the main subject visually consistent throughout.

Audio:
- Add realistic environmental sound and tasteful cinematic sound design.
- If dialogue is required, speak naturally in Egyptian Arabic.
"""
    operation = _start_generation(prompt, aspect_ratio, "1080p")
    video = _poll(operation)
    return {
        "status": "completed",
        "operation": operation,
        "video_uri": video.get("uri"),
        "mime_type": video.get("mimeType", "video/mp4"),
        "generated_prompt": prompt.strip(),
    }

if __name__ == "__main__":
    # Streamable HTTP is the recommended production transport for remote MCP.
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        stateless_http=True,
        json_response=True,
    )
