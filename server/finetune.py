from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer ,AutoModelForCausalLM ,pipeline

from huggingface_hub import login

hf_token = "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"
login(hf_token)
# Load dataset
ds = load_dataset("databricks/databricks-dolly-15k")

model_name="mistral-7b-v0.3-bnb-4bit"
#pipe = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1")     
pipe = pipeline("text-generation", model=model_name)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load model and tokenizer
model_name = "mistralai/Mistral-7B-v0.1"
#model = AutoModelForCausalLM.from_pretrained(model_name)
#tokenizer = AutoTokenizer.from_pretrained(model_name)

# Preprocess dataset (tokenization, formatting)
def preprocess(example):
    prompt = example["instruction"] + "\n" + example["context"] + "\n" + example["response"]
    return tokenizer(prompt, truncation=True, padding="max_length", max_length=512)

tokenized_ds = ds.map(preprocess, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./finetuned-mistral",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    save_steps=500,
    logging_steps=100,
    fp16=True,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds["train"],
    eval_dataset=tokenized_ds["test"],
)

# Train
trainer.train()

from datasets import load_dataset

ds = load_dataset("amitjf111/validate_chemistry_question")