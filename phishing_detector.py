from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
def detect_phishing(email_text):
    # Tokenize and prepare the input
    tokenizer = AutoTokenizer.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")
    model = AutoModelForSequenceClassification.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")
    inputs = tokenizer(email_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Get model predictions
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)

    # Get predicted label (0: Not Phishing, 1: Phishing)
    predicted_label = torch.argmax(probabilities).item()
    confidence = probabilities[0][predicted_label].item()

    if predicted_label == 0:
        return "Not Phishing", f"Confidence: {confidence:.2f}"
    else:
        return "Phishing", f"Confidence: {confidence:.2f}"
