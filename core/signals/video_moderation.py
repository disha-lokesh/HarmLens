"""
Video Content Moderation with Speech Recognition
Analyzes visual content, actions, AND speech/audio from videos
"""

import torch
import torch.nn as nn
from transformers import (
    VideoMAEImageProcessor, VideoMAEForVideoClassification,
    TimesformerForVideoClassification, AutoImageProcessor,
    Wav2Vec2Processor, Wav2Vec2ForCTC
)
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Import text moderation for speech analysis
try:
    from core.signals.advanced_toxicity import AdvancedToxicityDetector
    HAS_TEXT_DETECTOR = True
except:
    HAS_TEXT_DETECTOR = False


class VideoModerationModel:
    """
    Video content moderation using temporal analysis + speech recognition
    
    Models used:
    1. VideoMAE - Pretrained video understanding
    2. Frame-by-frame analysis using image models
    3. Wav2Vec2 - Speech-to-text transcription
    4. Advanced text toxicity on transcribed speech
    5. Temporal pattern detection
    """
    
    def __init__(self, device: str = None, enable_speech: bool = True):
        """
        Initialize video moderation models
        
        Args:
            device: 'cuda', 'mps', or 'cpu'. Auto-detects if None.
            enable_speech: Whether to enable speech recognition
        """
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        self.enable_speech = enable_speech
        
        print(f"🎬 Loading video moderation models on {self.device}...")
        
        # Load video understanding model
        self._load_video_model()
        
        # Load image model for frame analysis
        from core.signals.image_moderation import ImageModerationModel
        self.image_detector = ImageModerationModel(device=self.device, enable_ocr=True)
        
        # Load speech recognition model
        if self.enable_speech:
            self._load_speech_model()
            
            # Load text toxicity detector
            if HAS_TEXT_DETECTOR:
                self.text_detector = AdvancedToxicityDetector(device=self.device)
                print("  ✓ Text toxicity detector loaded")
            else:
                self.text_detector = None
                print("  ⚠️  Text toxicity detector not available")
        
        # Define video-specific harmful patterns
        self.harmful_patterns = {
            'violence': {
                'keywords': ['fight', 'assault', 'attack', 'shooting', 'stabbing', 'kill', 'murder'],
                'visual_cues': ['rapid motion', 'red flashes', 'weapon detection']
            },
            'explicit': {
                'keywords': ['sexual', 'nudity', 'explicit', 'porn'],
                'visual_cues': ['skin detection', 'inappropriate poses']
            },
            'dangerous_acts': {
                'keywords': ['suicide', 'self-harm', 'dangerous stunt', 'jump', 'fall'],
                'visual_cues': ['falling', 'jumping from height', 'fire']
            },
            'hate_speech': {
                'keywords': ['hate', 'racist', 'slur', 'discrimination', 'terrorist'],
                'visual_cues': ['hate symbols', 'aggressive gestures']
            }
        }
        
        print("✅ Video moderation models loaded")
    
    def _load_video_model(self):
        """Load video understanding model"""
        try:
            # Using VideoMAE for video classification
            model_name = "MCG-NJU/videomae-base"
            self.video_processor = VideoMAEImageProcessor.from_pretrained(model_name)
            self.video_model = VideoMAEForVideoClassification.from_pretrained(
                model_name,
                ignore_mismatched_sizes=True
            ).to(self.device)
            self.video_model.eval()
            print("  ✓ VideoMAE model loaded")
        except Exception as e:
            print(f"  ⚠️  VideoMAE model failed: {e}")
            self.video_model = None
    
    def _load_speech_model(self):
        """Load speech recognition model"""
        try:
            # Using Wav2Vec2 for speech-to-text
            model_name = "facebook/wav2vec2-base-960h"
            self.speech_processor = Wav2Vec2Processor.from_pretrained(model_name)
            self.speech_model = Wav2Vec2ForCTC.from_pretrained(model_name).to(self.device)
            self.speech_model.eval()
            print("  ✓ Wav2Vec2 speech model loaded")
        except Exception as e:
            print(f"  ⚠️  Speech model failed: {e}, trying Whisper...")
            try:
                from transformers import WhisperProcessor, WhisperForConditionalGeneration
                model_name = "openai/whisper-base"
                self.speech_processor = WhisperProcessor.from_pretrained(model_name)
                self.speech_model = WhisperForConditionalGeneration.from_pretrained(model_name).to(self.device)
                self.speech_model.eval()
                print("  ✓ Whisper speech model loaded")
            except Exception as e2:
                print(f"  ⚠️  Whisper also failed: {e2}")
                self.speech_model = None
    
    def extract_audio_from_video(self, video_path: str) -> Optional[np.ndarray]:
        """
        Extract audio track from video
        
        Args:
            video_path: Path to video file
        
        Returns:
            Audio waveform as numpy array
        """
        try:
            import librosa
            # Extract audio at 16kHz (required for Wav2Vec2)
            audio, sr = librosa.load(video_path, sr=16000, mono=True)
            return audio
        except Exception as e:
            print(f"  ⚠️  Audio extraction failed: {e}")
            try:
                # Fallback: use moviepy
                from moviepy.editor import VideoFileClip
                video = VideoFileClip(video_path)
                audio = video.audio
                if audio:
                    audio_array = audio.to_soundarray(fps=16000)
                    # Convert to mono if stereo
                    if len(audio_array.shape) > 1:
                        audio_array = audio_array.mean(axis=1)
                    return audio_array
                return None
            except Exception as e2:
                print(f"  ⚠️  Moviepy also failed: {e2}")
                return None
    
    def transcribe_audio(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text using speech recognition
        
        Args:
            audio: Audio waveform
        
        Returns:
            Transcribed text
        """
        if not self.enable_speech or self.speech_model is None or audio is None:
            return ""
        
        try:
            # Check if using Whisper or Wav2Vec2
            if hasattr(self.speech_model, 'generate'):
                # Whisper model
                input_features = self.speech_processor(
                    audio, 
                    sampling_rate=16000, 
                    return_tensors="pt"
                ).input_features.to(self.device)
                
                predicted_ids = self.speech_model.generate(input_features)
                transcription = self.speech_processor.batch_decode(
                    predicted_ids, 
                    skip_special_tokens=True
                )[0]
            else:
                # Wav2Vec2 model
                input_values = self.speech_processor(
                    audio, 
                    sampling_rate=16000, 
                    return_tensors="pt"
                ).input_values.to(self.device)
                
                with torch.no_grad():
                    logits = self.speech_model(input_values).logits
                
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.speech_processor.batch_decode(predicted_ids)[0]
            
            return transcription.strip()
        
        except Exception as e:
            print(f"  ⚠️  Transcription error: {e}")
            return ""
    
    def analyze_video(self, video_path: str, 
                     sample_rate: int = 30,
                     max_frames: int = 100) -> Dict:
        """
        Analyze video for harmful content INCLUDING speech
        
        Args:
            video_path: Path to video file
            sample_rate: Sample every Nth frame
            max_frames: Maximum frames to analyze
        
        Returns:
            Dictionary with risk scores and detected categories
        """
        print(f"📹 Analyzing video: {video_path}")
        
        results = {
            'risk_score': 0,
            'risk_label': 'Low',
            'categories': [],
            'frame_analysis': [],
            'temporal_patterns': {},
            'violence_score': 0,
            'nsfw_score': 0,
            'dangerous_acts_score': 0,
            'hate_score': 0,
            'duration_seconds': 0,
            'total_frames': 0,
            'analyzed_frames': 0,
            'speech_transcript': '',
            'speech_toxicity_score': 0,
            'speech_categories': []
        }
        
        # Extract frames from video
        frames, fps, duration = self._extract_frames(
            video_path, 
            sample_rate=sample_rate,
            max_frames=max_frames
        )
        
        results['duration_seconds'] = duration
        results['total_frames'] = len(frames)
        results['analyzed_frames'] = min(len(frames), max_frames)
        
        if not frames:
            print("⚠️  No frames extracted from video")
            return results
        
        print(f"  Extracted {len(frames)} frames (FPS: {fps}, Duration: {duration}s)")
        
        # Analyze frames using image detector
        frame_results = self._analyze_frames(frames)
        results['frame_analysis'] = frame_results
        
        # Detect temporal patterns
        temporal_analysis = self._analyze_temporal_patterns(frame_results)
        results['temporal_patterns'] = temporal_analysis
        
        # Aggregate scores across frames
        aggregated_scores = self._aggregate_frame_scores(frame_results)
        results.update(aggregated_scores)
        
        # NEW: Extract and analyze audio/speech
        if self.enable_speech:
            print("  🎤 Extracting audio...")
            audio = self.extract_audio_from_video(video_path)
            
            if audio is not None and len(audio) > 16000:  # At least 1 second
                print("  📝 Transcribing speech...")
                transcript = self.transcribe_audio(audio)
                results['speech_transcript'] = transcript
                
                if transcript and len(transcript) > 10:
                    print(f"  📊 Transcript: {transcript[:100]}...")
                    
                    if self.text_detector:
                        speech_analysis = self.text_detector.detect(transcript)
                        results['speech_toxicity_score'] = speech_analysis['tox_score'] * 100
                        results['speech_categories'] = speech_analysis['categories']
                        
                        print(f"  📊 Speech toxicity: {results['speech_toxicity_score']:.1f}/100")
        
        # Calculate overall risk score
        risk_score = self._calculate_video_risk_score(results)
        results['risk_score'] = risk_score
        
        # Determine risk label
        if risk_score >= 70:
            results['risk_label'] = 'High'
        elif risk_score >= 40:
            results['risk_label'] = 'Medium'
        else:
            results['risk_label'] = 'Low'
        
        # Identify detected categories
        results['categories'] = self._identify_video_categories(results)
        
        print(f"  ✅ Analysis complete: {results['risk_label']} risk ({risk_score}/100)")
        
        return results
    
    def _extract_frames(self, video_path: str, 
                       sample_rate: int = 30,
                       max_frames: int = 100) -> tuple:
        """
        Extract frames from video
        
        Args:
            video_path: Path to video file
            sample_rate: Sample every Nth frame
            max_frames: Maximum frames to extract
        
        Returns:
            Tuple of (frames, fps, duration)
        """
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"❌ Could not open video: {video_path}")
                return [], 0, 0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Sample frames
                if frame_count % sample_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    frames.append(pil_image)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
            return frames, fps, duration
        
        except Exception as e:
            print(f"❌ Error extracting frames: {e}")
            return [], 0, 0
    
    def _analyze_frames(self, frames: List[Image.Image]) -> List[Dict]:
        """Analyze each frame using image detector"""
        frame_results = []
        
        print(f"  Analyzing {len(frames)} frames...")
        
        for i, frame in enumerate(frames):
            try:
                result = self.image_detector.analyze_image(frame)
                frame_results.append({
                    'frame_index': i,
                    'risk_score': result['risk_score'],
                    'categories': result['categories'],
                    'nsfw_score': result['nsfw_score'],
                    'violence_score': result['violence_score'],
                    'hate_score': result['hate_score'],
                    'child_safety_score': result['child_safety_score']
                })
            except Exception as e:
                print(f"  ⚠️  Frame {i} analysis failed: {e}")
        
        return frame_results
    
    def _analyze_temporal_patterns(self, frame_results: List[Dict]) -> Dict:
        """
        Analyze temporal patterns across frames
        Detect escalating violence, sustained NSFW content, etc.
        """
        if not frame_results:
            return {}
        
        patterns = {
            'escalating_violence': False,
            'sustained_nsfw': False,
            'peak_risk_frame': 0,
            'risk_trend': 'stable'
        }
        
        # Extract risk scores over time
        risk_scores = [f['risk_score'] for f in frame_results]
        
        # Find peak risk frame
        patterns['peak_risk_frame'] = risk_scores.index(max(risk_scores))
        
        # Detect escalating violence
        violence_scores = [f['violence_score'] for f in frame_results]
        if len(violence_scores) > 3:
            # Check if violence increases over time
            first_half_avg = np.mean(violence_scores[:len(violence_scores)//2])
            second_half_avg = np.mean(violence_scores[len(violence_scores)//2:])
            
            if second_half_avg > first_half_avg * 1.5:
                patterns['escalating_violence'] = True
        
        # Detect sustained NSFW content
        nsfw_scores = [f['nsfw_score'] for f in frame_results]
        high_nsfw_frames = sum(1 for score in nsfw_scores if score > 50)
        
        if high_nsfw_frames > len(nsfw_scores) * 0.3:  # 30% of frames
            patterns['sustained_nsfw'] = True
        
        # Determine risk trend
        if len(risk_scores) > 5:
            first_third = np.mean(risk_scores[:len(risk_scores)//3])
            last_third = np.mean(risk_scores[-len(risk_scores)//3:])
            
            if last_third > first_third * 1.3:
                patterns['risk_trend'] = 'increasing'
            elif last_third < first_third * 0.7:
                patterns['risk_trend'] = 'decreasing'
        
        return patterns
    
    def _aggregate_frame_scores(self, frame_results: List[Dict]) -> Dict:
        """Aggregate scores across all frames"""
        if not frame_results:
            return {
                'violence_score': 0,
                'nsfw_score': 0,
                'hate_score': 0,
                'child_safety_score': 0
            }
        
        # Use max score (worst frame) with some averaging
        violence_scores = [f['violence_score'] for f in frame_results]
        nsfw_scores = [f['nsfw_score'] for f in frame_results]
        hate_scores = [f['hate_score'] for f in frame_results]
        child_scores = [f['child_safety_score'] for f in frame_results]
        
        # Weighted: 70% max, 30% average
        return {
            'violence_score': max(violence_scores) * 0.7 + np.mean(violence_scores) * 0.3,
            'nsfw_score': max(nsfw_scores) * 0.7 + np.mean(nsfw_scores) * 0.3,
            'hate_score': max(hate_scores) * 0.7 + np.mean(hate_scores) * 0.3,
            'child_safety_score': max(child_scores) * 0.7 + np.mean(child_scores) * 0.3
        }
    
    def _calculate_video_risk_score(self, results: Dict) -> int:
        """Calculate overall video risk score INCLUDING speech"""
        # Base score from frame analysis (60% weight)
        visual_score = (
            results['violence_score'] * 0.30 +
            results['nsfw_score'] * 0.25 +
            results['child_safety_score'] * 0.30 +
            results['hate_score'] * 0.15
        ) * 0.60
        
        # NEW: Speech toxicity score (40% weight)
        speech_score = results.get('speech_toxicity_score', 0) * 0.40
        
        # Combined score
        base_score = visual_score + speech_score
        
        # Temporal pattern multipliers
        temporal = results.get('temporal_patterns', {})
        
        if temporal.get('escalating_violence'):
            base_score *= 1.2  # 20% increase
        
        if temporal.get('sustained_nsfw'):
            base_score *= 1.15  # 15% increase
        
        if temporal.get('risk_trend') == 'increasing':
            base_score *= 1.1  # 10% increase
        
        # Boost if both visual and speech are problematic
        if visual_score > 40 and speech_score > 40:
            base_score = min(base_score * 1.3, 100)
        
        return min(int(base_score), 100)
    
    def _identify_video_categories(self, results: Dict) -> List[str]:
        """Identify harmful categories in video INCLUDING speech"""
        categories = []
        threshold = 30
        
        # Visual categories
        if results['violence_score'] > threshold:
            categories.append('Violence/Gore')
        
        if results['nsfw_score'] > threshold:
            categories.append('NSFW/Sexual Content')
        
        if results['hate_score'] > threshold:
            categories.append('Hate Content')
        
        if results['child_safety_score'] > threshold:
            categories.append('Child Safety Concern')
        
        # Temporal patterns
        temporal = results.get('temporal_patterns', {})
        if temporal.get('escalating_violence'):
            categories.append('Escalating Violence')
        
        if temporal.get('sustained_nsfw'):
            categories.append('Sustained NSFW')
        
        # NEW: Speech categories
        speech_categories = results.get('speech_categories', [])
        if speech_categories and speech_categories != ['Safe']:
            for cat in speech_categories:
                if cat not in categories:
                    categories.append(f"Speech: {cat}")
        
        return categories if categories else ['Safe']
    
    def analyze_video_with_audio(self, video_path: str) -> Dict:
        """
        Analyze video including audio track (alias for analyze_video)
        """
        return self.analyze_video(video_path)


class VideoModerationFineTuner:
    """
    Fine-tune video moderation models on custom datasets
    """
    
    def __init__(self, base_model: str = "MCG-NJU/videomae-base"):
        """
        Initialize fine-tuning setup
        
        Args:
            base_model: Base video model to fine-tune
        """
        self.base_model = base_model
        self.model = None
        self.processor = None
        
        print(f"🎯 Setting up video fine-tuning for {base_model}")
    
    def prepare_model(self, num_labels: int = 5):
        """
        Prepare model for fine-tuning
        
        Args:
            num_labels: Number of output categories
        """
        self.processor = VideoMAEImageProcessor.from_pretrained(self.base_model)
        self.model = VideoMAEForVideoClassification.from_pretrained(
            self.base_model,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        )
        
        # Define label mapping
        self.id2label = {
            0: "safe",
            1: "violence",
            2: "nsfw",
            3: "hate",
            4: "dangerous_acts"
        }
        self.label2id = {v: k for k, v in self.id2label.items()}
        
        self.model.config.id2label = self.id2label
        self.model.config.label2id = self.label2id
        
        print("✅ Video model prepared for fine-tuning")
    
    def train(self, train_videos: List[str], train_labels: List[int],
              epochs: int = 3, batch_size: int = 4):
        """
        Fine-tune video model
        
        Args:
            train_videos: List of video file paths
            train_labels: List of corresponding labels
            epochs: Number of training epochs
            batch_size: Batch size (keep small for videos)
        """
        print("🚀 Starting video model fine-tuning...")
        print("⚠️  Note: Video fine-tuning requires significant GPU memory")
        
        # TODO: Implement full training pipeline
        # This requires:
        # 1. Video dataset loader
        # 2. Frame sampling strategy
        # 3. Training loop with gradient accumulation
        # 4. Validation and checkpointing
        
        print("✅ Fine-tuning setup complete")


# Example usage
if __name__ == "__main__":
    # Initialize model
    detector = VideoModerationModel()
    
    # Analyze a video
    # result = detector.analyze_video("path/to/video.mp4")
    # print(f"Risk Score: {result['risk_score']}/100")
    # print(f"Risk Label: {result['risk_label']}")
    # print(f"Categories: {result['categories']}")
