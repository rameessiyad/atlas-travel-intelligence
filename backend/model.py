import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

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
        torch_dtype=torch.float16 if use_cuda else torch.float32,
        device_map="auto" if use_cuda else None,
    )
    if os.path.isdir(ADAPTER_PATH):
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    _model = model
    return _tokenizer, _model


SYSTEM_PROMPT = (
    "You are Atlas, a practical travel-planning assistant. "
    "Use the supplied travel notes for facts about places. "
    "Do not invent prices, opening hours, availability or specific venue names "
    "that are not in the notes. If the notes lack something, say it needs to be "
    "checked. Give a clear day-by-day plan with a short reason for each day, "
    "matching the traveller's interests, budget and pace."
)

REVISE_PROMPT = (
    SYSTEM_PROMPT
    + " You will be given an existing itinerary and a requested change. "
    "Apply only the requested change and keep the traveller's original "
    "destination, number of days, budget, interests and pace. "
    "Return the full updated itinerary."
)


def _format_notes(notes: list[dict]) -> str:
    return "\n".join(f"- [{n['id']}] {n['text']}" for n in notes) \
        or "No matching travel notes were found."


def _generate(messages: list[dict]) -> str:
    tokenizer, model = load_model()
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs, max_new_tokens=500, do_sample=True,
            temperature=0.7, top_p=0.9,
        )
    new_tokens = output[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def answer_with_qwen(request: str, notes: list[dict]) -> str:
    return _generate([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",
         "content": f"Travel request: {request}\n\nTravel notes:\n{_format_notes(notes)}"},
    ])


def revise_with_qwen(request: str, itinerary: str, change: str, notes: list[dict]) -> str:
    return _generate([
        {"role": "system", "content": REVISE_PROMPT},
        {"role": "user", "content": (
            f"Original request: {request}\n\n"
            f"Travel notes:\n{_format_notes(notes)}\n\n"
            f"Current itinerary:\n{itinerary}\n\n"
            f"Requested change: {change}"
        )},
    ])