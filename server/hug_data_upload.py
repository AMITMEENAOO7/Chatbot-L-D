from huggingface_hub import HfApi

hf_token="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"
api = HfApi(token=hf_token)
api.upload_folder(
    folder_path= "C:\\Users\\USER\\validate_chemistry_question",
    repo_id="amitjf111/first-finetuning-validate-chemistry-questions",
    repo_type="dataset",
)
