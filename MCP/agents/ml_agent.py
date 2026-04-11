"""Machine Learning agent for sentiment/risk classification."""

from transformers import pipeline
import torch

# Initialize classifier once
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1
)

def classify(text: str):
    """Classify text sentiment and confidence."""
    with torch.no_grad():
        result = classifier(text)[0]
    
    return {
        "label": result["label"],
        "confidence": float(result["score"])
    }
