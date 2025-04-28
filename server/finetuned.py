from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer ,AutoModelForCausalLM ,pipeline

from huggingface_hub import login

hf_token = "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"
login(hf_token)
# Load dataset
ds = load_dataset("databricks/databricks-dolly-15k")


 


tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")

# Load model and tokenizer
model_name = "mistralai/Mistral-7B-v0.1"
#model = AutoModelForCausalLM.from_pretrained(model_name)
#tokenizer = AutoTokenizer.from_pretrained(model_name)

# Preprocess dataset (tokenization, formatting)

# Create a text generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

prompt = "Explain the theory of relativity in simple terms."
result = generator(prompt, max_length=50, do_sample=True, temperature=0.7)
print(result[0]['generated_text'])