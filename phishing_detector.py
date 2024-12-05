from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
def detect_phishing(email_text):
    """
    The detect_phishing function uses a pretrained LLM to detect weather the inputted email is a real email or a phishing email. 
    It outputs its prediction, along with it's confidence level for that prediction. The LLM model that was used is called 
    cybersectony/phishing-email-detection-distilbert_v2.4.1. https://huggingface.co/cybersectony/phishing-email-detection-distilbert_v2.4.1
    """
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
