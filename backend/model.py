import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from prompts import (
    SYSTEM_PROMPT,
    REVISE_PROMPT,
    itinerary_user_message,
    revise_user_message,
)

BASE_MODEL = os.getenv("ATLAS_BASE_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
ADAPTER_PATH = os.getenv("ATLAS_LORA_ADAPTER", "models/atlas-lora")

_tokenizer = None
_model = None


def load_model():
    global _tokenizer, _model
    if _model is not None:
        return _tokenizer, _model
    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    use_cuda = torch.cuda.is_available()
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.float16 if use_cuda else torch.float32,
        device_map="auto" if use_cuda else None,
    )
    if os.path.isdir(ADAPTER_PATH):
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    _model = model
    return _tokenizer, _model


def _generate(messages: list[dict]) -> str:
    tokenizer, model = load_model()
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs, max_new_tokens=500, do_sample=True,
            temperature=0.4, top_p=0.9,
        )
    new_tokens = output[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def answer_with_qwen(request: str, notes: list[dict]) -> str:
    return _generate([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": itinerary_user_message(request, notes)},
    ])


def revise_with_qwen(request: str, itinerary: str, change: str, notes: list[dict]) -> str:
    return _generate([
        {"role": "system", "content": REVISE_PROMPT},
        {"role": "user", "content": revise_user_message(request, itinerary, change, notes)},
    ])