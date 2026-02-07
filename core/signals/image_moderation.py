"""
Image Content Moderation with OCR
Analyzes both visual content AND text extracted from images
"""

import torch
import torch.nn as nn
from transformers import (
    CLIPProcessor, CLIPModel,
    ViTImageProcessor, ViTForImageClassification,
    AutoImageProcessor, AutoModelForImageClassification,
    TrOCRProcessor, VisionEncoderDecoderModel
)
from PIL import Image
import numpy as np
from typing import Dict, List, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Import text moderation for OCR text
try:
    from core.signals.advanced_toxicity import AdvancedToxicityDetector
    HAS_TEXT_DETECTOR = True
except:
    HAS_TEXT_DETECTOR = False


class ImageModerationModel:
    """
    Multi-model ensemble for image content moderation
    NOW WITH OCR: Extracts and analyzes text from images
    
    Models used:
    1. CLIP (OpenAI) - Zero-shot classification for harmful content
    2. Google's SafeSearch-style classifier
    3. NSFW detection model
    4. Violence/Gore detection
    5. TrOCR - Text extraction from images
    6. Advanced text toxicity detection on extracted text
    """
    
    def __init__(self, device: str = None, enable_ocr: bool = True):
        """
        Initialize image moderation models
        
        Args:
            device: 'cuda', 'mps', or 'cpu'. Auto-detects if None.
            enable_ocr: Whether to enable OCR text extraction
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
        
        self.enable_ocr = enable_ocr
        
        print(f"🖼️  Loading image moderation models on {self.device}...")
        
        # Load CLIP for zero-shot classification
        self._load_clip_model()
        
        # Load NSFW detection model
        self._load_nsfw_model()
        
        # Load OCR model
        if self.enable_ocr:
            self._load_ocr_model()
            
            # Load text toxicity detector
            if HAS_TEXT_DETECTOR:
                self.text_detector = AdvancedToxicityDetector(device=self.device)
                print("  ✓ Text toxicity detector loaded")
            else:
                self.text_detector = None
                print("  ⚠️  Text toxicity detector not available")
        
        # Define harmful content categories
        self.harmful_categories = {
            'violence': [
                "graphic violence", "blood and gore", "weapons being used",
                "physical assault", "war violence", "torture"
            ],
            'nsfw': [
                "nudity", "sexual content", "explicit imagery",
                "pornographic content", "inappropriate exposure"
            ],
            'hate_symbols': [
                "hate symbols", "nazi imagery", "racist symbols",
                "extremist flags", "hate group insignia"
            ],
            'child_safety': [
                "child in danger", "child exploitation imagery",
                "inappropriate child content", "child abuse imagery"
            ],
            'self_harm': [
                "self-harm imagery", "suicide content", "cutting imagery",
                "eating disorder content", "self-injury"
            ],
            'drugs': [
                "drug paraphernalia", "drug use imagery", "illegal substances",
                "drug manufacturing", "substance abuse"
            ],
            'disturbing': [
                "dead bodies", "severe injuries", "animal cruelty",
                "graphic medical content", "disturbing imagery"
            ]
        }
        
        print("✅ Image moderation models loaded")
    
    def _load_clip_model(self):
        """Load CLIP model for zero-shot classification"""
        try:
            model_name = "openai/clip-vit-base-patch32"
            self.clip_processor = CLIPProcessor.from_pretrained(model_name)
            self.clip_model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.clip_model.eval()
            print("  ✓ CLIP model loaded")
        except Exception as e:
            print(f"  ⚠️  CLIP model failed: {e}")
            self.clip_model = None
    
    def _load_nsfw_model(self):
        """Load NSFW detection model"""
        try:
            # Using a fine-tuned NSFW classifier
            model_name = "Falconsai/nsfw_image_detection"
            self.nsfw_processor = AutoImageProcessor.from_pretrained(model_name)
            self.nsfw_model = AutoModelForImageClassification.from_pretrained(model_name).to(self.device)
            self.nsfw_model.eval()
            print("  ✓ NSFW detection model loaded")
        except Exception as e:
            print(f"  ⚠️  NSFW model failed: {e}")
            self.nsfw_model = None
    
    def _load_ocr_model(self):
        """Load OCR model for text extraction"""
        try:
            # Using TrOCR for text extraction
            model_name = "microsoft/trocr-base-printed"
            self.ocr_processor = TrOCRProcessor.from_pretrained(model_name)
            self.ocr_model = VisionEncoderDecoderModel.from_pretrained(model_name).to(self.device)
            self.ocr_model.eval()
            print("  ✓ OCR model loaded (TrOCR)")
        except Exception as e:
            print(f"  ⚠️  OCR model failed: {e}, trying EasyOCR...")
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(['en'], gpu=(self.device == 'cuda'), verbose=False)
                self.ocr_model = 'easyocr'
                print("  ✓ OCR model loaded (EasyOCR)")
            except Exception as e2:
                print(f"  ⚠️  EasyOCR also failed: {e2}")
                self.ocr_model = None
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image
        
        Returns:
            Extracted text string
        """
        if not self.enable_ocr or self.ocr_model is None:
            return ""
        
        try:
            if self.ocr_model == 'easyocr':
                # EasyOCR
                import numpy as np
                img_array = np.array(image.convert('RGB'))
                results = self.ocr_reader.readtext(img_array, detail=0, paragraph=True)
                return '\n'.join(results).strip()
            else:
                # TrOCR
                pixel_values = self.ocr_processor(images=image, return_tensors="pt").pixel_values.to(self.device)
                generated_ids = self.ocr_model.generate(pixel_values)
                generated_text = self.ocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                return generated_text.strip()
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    def analyze_image(self, image: Union[str, Image.Image]) -> Dict:
        """
        Analyze image for harmful content INCLUDING text extraction
        
        Args:
            image: PIL Image or path to image file
        
        Returns:
            Dictionary with risk scores and detected categories
        """
        # Load image if path provided
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be PIL Image or file path")
        
        results = {
            'risk_score': 0,
            'risk_label': 'Low',
            'categories': [],
            'detections': {},
            'nsfw_score': 0,
            'violence_score': 0,
            'hate_score': 0,
            'child_safety_score': 0,
            'self_harm_score': 0,
            'drugs_score': 0,
            'disturbing_score': 0,
            'text_content': '',
            'text_toxicity_score': 0,
            'text_categories': []
        }
        
        # Run CLIP zero-shot classification
        if self.clip_model:
            clip_results = self._analyze_with_clip(image)
            results['detections']['clip'] = clip_results
            
            # Extract category scores
            results['violence_score'] = clip_results.get('violence', 0)
            results['hate_score'] = clip_results.get('hate_symbols', 0)
            results['child_safety_score'] = clip_results.get('child_safety', 0)
            results['self_harm_score'] = clip_results.get('self_harm', 0)
            results['drugs_score'] = clip_results.get('drugs', 0)
            results['disturbing_score'] = clip_results.get('disturbing', 0)
        
        # Run NSFW detection
        if self.nsfw_model:
            nsfw_result = self._analyze_nsfw(image)
            results['detections']['nsfw'] = nsfw_result
            results['nsfw_score'] = nsfw_result.get('nsfw_probability', 0)
        
        # NEW: Extract and analyze text from image
        if self.enable_ocr:
            extracted_text = self.extract_text_from_image(image)
            results['text_content'] = extracted_text
            
            if extracted_text and len(extracted_text) > 5:  # Only analyze if meaningful text
                print(f"  📝 Extracted text: {extracted_text[:100]}...")
                
                if self.text_detector:
                    text_analysis = self.text_detector.detect(extracted_text)
                    results['text_toxicity_score'] = text_analysis['tox_score'] * 100
                    results['text_categories'] = text_analysis['categories']
                    results['detections']['text'] = text_analysis
                    
                    print(f"  📊 Text toxicity: {results['text_toxicity_score']:.1f}/100")
        
        # Calculate overall risk score (0-100)
        risk_score = self._calculate_risk_score(results)
        results['risk_score'] = risk_score
        
        # Determine risk label
        if risk_score >= 70:
            results['risk_label'] = 'High'
        elif risk_score >= 40:
            results['risk_label'] = 'Medium'
        else:
            results['risk_label'] = 'Low'
        
        # Identify detected categories
        results['categories'] = self._identify_categories(results)
        
        return results
    
    def _analyze_with_clip(self, image: Image.Image) -> Dict:
        """Use CLIP for zero-shot classification"""
        category_scores = {}
        
        try:
            with torch.no_grad():
                for category, descriptions in self.harmful_categories.items():
                    # Prepare inputs
                    inputs = self.clip_processor(
                        text=descriptions,
                        images=image,
                        return_tensors="pt",
                        padding=True
                    ).to(self.device)
                    
                    # Get predictions
                    outputs = self.clip_model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = logits_per_image.softmax(dim=1)
                    
                    # Get max probability for this category
                    max_prob = probs.max().item()
                    category_scores[category] = max_prob * 100
        
        except Exception as e:
            print(f"CLIP analysis error: {e}")
        
        return category_scores
    
    def _analyze_nsfw(self, image: Image.Image) -> Dict:
        """Analyze image for NSFW content"""
        try:
            with torch.no_grad():
                inputs = self.nsfw_processor(images=image, return_tensors="pt").to(self.device)
                outputs = self.nsfw_model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                
                # Get NSFW probability
                # Model outputs: [normal, nsfw]
                nsfw_prob = probs[0][1].item() if probs.shape[1] > 1 else probs[0][0].item()
                
                return {
                    'nsfw_probability': nsfw_prob * 100,
                    'is_nsfw': nsfw_prob > 0.5
                }
        
        except Exception as e:
            print(f"NSFW analysis error: {e}")
            return {'nsfw_probability': 0, 'is_nsfw': False}
    
    def _calculate_risk_score(self, results: Dict) -> int:
        """Calculate overall risk score from all detections INCLUDING text"""
        # Weighted scoring for visual content
        visual_weights = {
            'nsfw_score': 0.20,
            'violence_score': 0.15,
            'child_safety_score': 0.25,  # Highest weight
            'hate_score': 0.08,
            'self_harm_score': 0.08,
            'drugs_score': 0.02,
            'disturbing_score': 0.02
        }
        
        visual_score = 0
        for key, weight in visual_weights.items():
            visual_score += results.get(key, 0) * weight
        
        # NEW: Add text toxicity score (20% weight)
        text_score = results.get('text_toxicity_score', 0) * 0.20
        
        # Combined score
        risk_score = visual_score + text_score
        
        # Boost if both visual and text are problematic
        if visual_score > 50 and text_score > 50:
            risk_score = min(risk_score * 1.3, 100)
        
        # Cap at 100
        return min(int(risk_score), 100)
    
    def _identify_categories(self, results: Dict) -> List[str]:
        """Identify which categories were detected"""
        categories = []
        threshold = 30  # 30% confidence threshold
        
        # Visual categories
        if results['nsfw_score'] > threshold:
            categories.append('NSFW/Sexual Content')
        
        if results['violence_score'] > threshold:
            categories.append('Violence/Gore')
        
        if results['hate_score'] > threshold:
            categories.append('Hate Symbols')
        
        if results['child_safety_score'] > threshold:
            categories.append('Child Safety Concern')
        
        if results['self_harm_score'] > threshold:
            categories.append('Self-Harm')
        
        if results['drugs_score'] > threshold:
            categories.append('Drugs/Substances')
        
        if results['disturbing_score'] > threshold:
            categories.append('Disturbing Content')
        
        # NEW: Text categories
        text_categories = results.get('text_categories', [])
        if text_categories and text_categories != ['Safe']:
            for cat in text_categories:
                if cat not in categories:
                    categories.append(f"Text: {cat}")
        
        return categories if categories else ['Safe']
    
    def batch_analyze(self, images: List[Union[str, Image.Image]]) -> List[Dict]:
        """
        Analyze multiple images in batch
        
        Args:
            images: List of PIL Images or file paths
        
        Returns:
            List of analysis results
        """
        results = []
        for image in images:
            result = self.analyze_image(image)
            results.append(result)
        return results


class ImageModerationFineTuner:
    """
    Fine-tune image moderation models on custom datasets
    """
    
    def __init__(self, base_model: str = "google/vit-base-patch16-224"):
        """
        Initialize fine-tuning setup
        
        Args:
            base_model: Base model to fine-tune
        """
        self.base_model = base_model
        self.model = None
        self.processor = None
        
        print(f"🎯 Setting up fine-tuning for {base_model}")
    
    def prepare_model(self, num_labels: int = 7):
        """
        Prepare model for fine-tuning
        
        Args:
            num_labels: Number of output categories
        """
        from transformers import ViTForImageClassification, ViTImageProcessor
        
        self.processor = ViTImageProcessor.from_pretrained(self.base_model)
        self.model = ViTForImageClassification.from_pretrained(
            self.base_model,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        )
        
        # Define label mapping
        self.id2label = {
            0: "safe",
            1: "nsfw",
            2: "violence",
            3: "hate",
            4: "child_safety",
            5: "self_harm",
            6: "drugs"
        }
        self.label2id = {v: k for k, v in self.id2label.items()}
        
        self.model.config.id2label = self.id2label
        self.model.config.label2id = self.label2id
        
        print("✅ Model prepared for fine-tuning")
    
    def create_dataset(self, image_paths: List[str], labels: List[int]):
        """
        Create dataset for training
        
        Args:
            image_paths: List of paths to training images
            labels: List of corresponding labels
        """
        from torch.utils.data import Dataset
        
        class ImageDataset(Dataset):
            def __init__(self, image_paths, labels, processor):
                self.image_paths = image_paths
                self.labels = labels
                self.processor = processor
            
            def __len__(self):
                return len(self.image_paths)
            
            def __getitem__(self, idx):
                image = Image.open(self.image_paths[idx]).convert('RGB')
                encoding = self.processor(images=image, return_tensors="pt")
                encoding = {k: v.squeeze() for k, v in encoding.items()}
                encoding['labels'] = torch.tensor(self.labels[idx])
                return encoding
        
        return ImageDataset(image_paths, labels, self.processor)
    
    def train(self, train_dataset, val_dataset=None, epochs: int = 3, 
              batch_size: int = 16, learning_rate: float = 2e-5):
        """
        Fine-tune the model
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset (optional)
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        from transformers import TrainingArguments, Trainer
        
        training_args = TrainingArguments(
            output_dir="./models/image_moderation_finetuned",
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            evaluation_strategy="epoch" if val_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if val_dataset else False,
            logging_dir='./logs',
            logging_steps=10,
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        print("🚀 Starting fine-tuning...")
        trainer.train()
        print("✅ Fine-tuning complete!")
        
        # Save model
        self.model.save_pretrained("./models/image_moderation_finetuned")
        self.processor.save_pretrained("./models/image_moderation_finetuned")
        print("💾 Model saved to ./models/image_moderation_finetuned")


# Example usage
if __name__ == "__main__":
    # Initialize model
    detector = ImageModerationModel()
    
    # Analyze an image
    # result = detector.analyze_image("path/to/image.jpg")
    # print(f"Risk Score: {result['risk_score']}/100")
    # print(f"Risk Label: {result['risk_label']}")
    # print(f"Categories: {result['categories']}")
