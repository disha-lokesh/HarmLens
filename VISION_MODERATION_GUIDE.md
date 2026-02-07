# 🖼️ Image & Video Moderation Guide

## Overview

HarmLens now includes **AI-powered image and video content moderation** using state-of-the-art pretrained models.

### Models Used

#### Image Moderation
1. **CLIP (OpenAI)** - Zero-shot classification for harmful content
2. **NSFW Detector** - Fine-tuned classifier for explicit content
3. **Multi-category detection** - Violence, hate symbols, child safety, self-harm, drugs

#### Video Moderation
1. **VideoMAE** - Temporal video understanding
2. **Frame-by-frame analysis** - Using image models on sampled frames
3. **Temporal pattern detection** - Escalating violence, sustained NSFW content
4. **Audio analysis** (optional) - Speech-to-text for hate speech

---

## Installation

### Step 1: Install Vision Dependencies

```bash
pip install -r requirements_vision.txt
```

### Step 2: Download Models (Automatic)

Models download automatically on first use. Requires ~2GB disk space.

### Step 3: Verify Installation

```python
from core.signals.image_moderation import ImageModerationModel
from core.signals.video_moderation import VideoModerationModel

# Test image model
image_detector = ImageModerationModel()
print("✅ Image moderation ready")

# Test video model
video_detector = VideoModerationModel()
print("✅ Video moderation ready")
```

---

## Image Moderation

### Basic Usage

```python
from core.signals.image_moderation import ImageModerationModel
from PIL import Image

# Initialize detector
detector = ImageModerationModel()

# Analyze an image
result = detector.analyze_image("path/to/image.jpg")

print(f"Risk Score: {result['risk_score']}/100")
print(f"Risk Label: {result['risk_label']}")
print(f"Categories: {result['categories']}")
print(f"NSFW Score: {result['nsfw_score']}")
print(f"Violence Score: {result['violence_score']}")
```

### Output Example

```python
{
    'risk_score': 85,
    'risk_label': 'High',
    'categories': ['Violence/Gore', 'Disturbing Content'],
    'nsfw_score': 12.5,
    'violence_score': 78.3,
    'hate_score': 5.2,
    'child_safety_score': 8.1,
    'self_harm_score': 15.6,
    'drugs_score': 3.4,
    'disturbing_score': 45.8
}
```

### Batch Processing

```python
# Analyze multiple images
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
results = detector.batch_analyze(images)

for i, result in enumerate(results):
    print(f"Image {i+1}: {result['risk_label']} ({result['risk_score']}/100)")
```

### Detected Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **NSFW/Sexual Content** | Nudity, explicit imagery | Pornography, inappropriate exposure |
| **Violence/Gore** | Graphic violence, blood | Assault, weapons, injuries |
| **Hate Symbols** | Extremist imagery | Nazi symbols, hate group insignia |
| **Child Safety** | Child exploitation | Inappropriate child content |
| **Self-Harm** | Self-injury content | Cutting, suicide imagery |
| **Drugs** | Drug-related content | Drug use, paraphernalia |
| **Disturbing** | Shocking content | Dead bodies, severe injuries |

---

## Video Moderation

### Basic Usage

```python
from core.signals.video_moderation import VideoModerationModel

# Initialize detector
detector = VideoModerationModel()

# Analyze a video
result = detector.analyze_video(
    "path/to/video.mp4",
    sample_rate=30,      # Sample every 30th frame
    max_frames=100       # Analyze up to 100 frames
)

print(f"Risk Score: {result['risk_score']}/100")
print(f"Risk Label: {result['risk_label']}")
print(f"Categories: {result['categories']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"Analyzed Frames: {result['analyzed_frames']}")
```

### Output Example

```python
{
    'risk_score': 72,
    'risk_label': 'High',
    'categories': ['Violence/Gore', 'Escalating Violence'],
    'violence_score': 65.4,
    'nsfw_score': 8.2,
    'dangerous_acts_score': 42.1,
    'hate_score': 3.5,
    'duration_seconds': 120.5,
    'total_frames': 3615,
    'analyzed_frames': 100,
    'temporal_patterns': {
        'escalating_violence': True,
        'sustained_nsfw': False,
        'peak_risk_frame': 78,
        'risk_trend': 'increasing'
    }
}
```

### Temporal Pattern Detection

Videos are analyzed for patterns over time:

- **Escalating Violence**: Violence increases throughout video
- **Sustained NSFW**: NSFW content present in >30% of frames
- **Risk Trend**: Whether risk increases, decreases, or stays stable
- **Peak Risk Frame**: Frame with highest risk score

### Performance Optimization

```python
# For long videos, adjust sampling
result = detector.analyze_video(
    "long_video.mp4",
    sample_rate=60,      # Sample less frequently
    max_frames=50        # Analyze fewer frames
)

# For short videos, sample more
result = detector.analyze_video(
    "short_video.mp4",
    sample_rate=10,      # Sample more frequently
    max_frames=200       # Analyze more frames
)
```

---

## Integration with HarmLens API

### Add to API Server

Update `api_server.py`:

```python
from core.signals.image_moderation import ImageModerationModel
from core.signals.video_moderation import VideoModerationModel

# Initialize detectors
image_detector = ImageModerationModel()
video_detector = VideoModerationModel()

@app.post("/api/v1/analyze/image")
async def analyze_image(file: UploadFile):
    """Analyze uploaded image"""
    # Save uploaded file
    image_path = f"temp/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())
    
    # Analyze
    result = image_detector.analyze_image(image_path)
    
    # Clean up
    os.remove(image_path)
    
    return result

@app.post("/api/v1/analyze/video")
async def analyze_video(file: UploadFile):
    """Analyze uploaded video"""
    # Save uploaded file
    video_path = f"temp/{file.filename}"
    with open(video_path, "wb") as f:
        f.write(await file.read())
    
    # Analyze
    result = video_detector.analyze_video(video_path)
    
    # Clean up
    os.remove(video_path)
    
    return result
```

### API Usage

```bash
# Analyze image
curl -X POST "http://localhost:8000/api/v1/analyze/image" \
  -F "file=@image.jpg"

# Analyze video
curl -X POST "http://localhost:8000/api/v1/analyze/video" \
  -F "file=@video.mp4"
```

---

## Fine-Tuning on Custom Data

### Image Model Fine-Tuning

```python
from core.signals.image_moderation import ImageModerationFineTuner

# Initialize fine-tuner
finetuner = ImageModerationFineTuner(
    base_model="google/vit-base-patch16-224"
)

# Prepare model
finetuner.prepare_model(num_labels=7)

# Prepare your dataset
image_paths = [
    "train/safe/img1.jpg",
    "train/nsfw/img2.jpg",
    "train/violence/img3.jpg",
    # ... more images
]

labels = [0, 1, 2, ...]  # Corresponding labels

# Create dataset
train_dataset = finetuner.create_dataset(image_paths, labels)

# Fine-tune
finetuner.train(
    train_dataset=train_dataset,
    epochs=3,
    batch_size=16,
    learning_rate=2e-5
)

# Model saved to ./models/image_moderation_finetuned
```

### Video Model Fine-Tuning

```python
from core.signals.video_moderation import VideoModerationFineTuner

# Initialize fine-tuner
finetuner = VideoModerationFineTuner(
    base_model="MCG-NJU/videomae-base"
)

# Prepare model
finetuner.prepare_model(num_labels=5)

# Prepare your dataset
video_paths = [
    "train/safe/video1.mp4",
    "train/violence/video2.mp4",
    # ... more videos
]

labels = [0, 1, ...]  # Corresponding labels

# Fine-tune
finetuner.train(
    train_videos=video_paths,
    train_labels=labels,
    epochs=3,
    batch_size=4  # Keep small for videos
)
```

### Dataset Requirements

#### Image Dataset Structure
```
dataset/
├── train/
│   ├── safe/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── nsfw/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── violence/
│   └── ...
└── val/
    └── (same structure)
```

#### Video Dataset Structure
```
dataset/
├── train/
│   ├── safe/
│   │   ├── video1.mp4
│   │   └── video2.mp4
│   ├── violence/
│   └── ...
└── val/
    └── (same structure)
```

---

## Performance Benchmarks

### Image Analysis

| Device | Speed | Memory |
|--------|-------|--------|
| **CPU** | ~2s per image | 2GB RAM |
| **GPU (CUDA)** | ~0.1s per image | 4GB VRAM |
| **Apple Silicon (MPS)** | ~0.3s per image | 4GB RAM |

### Video Analysis

| Video Length | Frames Analyzed | Speed (GPU) | Speed (CPU) |
|--------------|-----------------|-------------|-------------|
| **30s** | 100 frames | ~10s | ~3min |
| **2min** | 100 frames | ~10s | ~3min |
| **10min** | 100 frames | ~10s | ~3min |

*Note: Speed depends on sampling rate, not video length*

---

## Use Cases

### 1. Social Media Platform

```python
# User uploads image
@app.post("/upload/image")
async def upload_image(file: UploadFile):
    # Analyze before accepting
    result = image_detector.analyze_image(file)
    
    if result['risk_score'] > 70:
        return {"error": "Content violates community guidelines"}
    
    # Accept upload
    save_image(file)
    return {"success": True}
```

### 2. Video Streaming Platform

```python
# Creator uploads video
@app.post("/upload/video")
async def upload_video(file: UploadFile):
    # Analyze video
    result = video_detector.analyze_video(file)
    
    if result['risk_score'] > 80:
        # Auto-reject
        return {"error": "Content violates guidelines"}
    
    elif result['risk_score'] > 50:
        # Flag for manual review
        queue_for_review(file, result)
        return {"status": "pending_review"}
    
    else:
        # Auto-approve
        publish_video(file)
        return {"success": True}
```

### 3. Content Moderation Queue

```python
# Moderator reviews flagged content
@app.get("/moderation/queue")
async def get_queue():
    flagged_content = get_flagged_items()
    
    for item in flagged_content:
        if item['type'] == 'image':
            analysis = image_detector.analyze_image(item['path'])
        elif item['type'] == 'video':
            analysis = video_detector.analyze_video(item['path'])
        
        item['ai_analysis'] = analysis
    
    return flagged_content
```

### 4. Batch Processing

```python
# Scan entire content library overnight
import glob

images = glob.glob("content/**/*.jpg", recursive=True)
videos = glob.glob("content/**/*.mp4", recursive=True)

# Process images
print(f"Scanning {len(images)} images...")
image_results = image_detector.batch_analyze(images)

# Process videos
print(f"Scanning {len(videos)} videos...")
for video in videos:
    result = video_detector.analyze_video(video)
    if result['risk_score'] > 70:
        flag_for_review(video, result)
```

---

## Model Details

### Image Models

#### CLIP (openai/clip-vit-base-patch32)
- **Purpose**: Zero-shot classification
- **Size**: 151M parameters
- **Input**: 224x224 RGB images
- **Output**: Similarity scores for text descriptions

#### NSFW Detector (Falconsai/nsfw_image_detection)
- **Purpose**: Explicit content detection
- **Size**: 86M parameters
- **Input**: 224x224 RGB images
- **Output**: NSFW probability

### Video Models

#### VideoMAE (MCG-NJU/videomae-base)
- **Purpose**: Video understanding
- **Size**: 86M parameters
- **Input**: 16 frames, 224x224 RGB
- **Output**: Video classification

---

## Troubleshooting

### Out of Memory

```python
# Reduce batch size
detector = ImageModerationModel(device='cpu')  # Use CPU instead

# For videos, reduce frames
result = video_detector.analyze_video(
    video_path,
    sample_rate=60,  # Sample less
    max_frames=50    # Analyze fewer frames
)
```

### Slow Performance

```python
# Use GPU if available
detector = ImageModerationModel(device='cuda')

# For videos, increase sampling rate
result = video_detector.analyze_video(
    video_path,
    sample_rate=60,  # Skip more frames
    max_frames=50    # Analyze fewer frames
)
```

### Model Download Fails

```bash
# Manually download models
huggingface-cli download openai/clip-vit-base-patch32
huggingface-cli download Falconsai/nsfw_image_detection
huggingface-cli download MCG-NJU/videomae-base
```

---

## Accuracy & Limitations

### Strengths
- ✅ High accuracy on common harmful content (NSFW, violence)
- ✅ Fast inference (<1s per image on GPU)
- ✅ Zero-shot capabilities (no training needed)
- ✅ Temporal analysis for videos

### Limitations
- ⚠️ May miss context-dependent content
- ⚠️ Can have false positives on artistic/medical content
- ⚠️ Requires manual review for edge cases
- ⚠️ Video analysis is frame-based (may miss audio cues)

### Recommended Workflow
1. **Auto-approve**: Risk score < 30
2. **Flag for review**: Risk score 30-70
3. **Auto-block**: Risk score > 70
4. **Human review**: All child safety flags

---

## Next Steps

1. ✅ Install vision dependencies
2. ✅ Test image analysis
3. ✅ Test video analysis
4. ✅ Integrate with API
5. ✅ Set up moderation queue
6. ✅ Fine-tune on your data (optional)
7. ✅ Deploy to production

---

**Ready to moderate visual content at scale! 🖼️🎬**
