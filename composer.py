import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# API Key configure
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def compose(merchant_ctx, trigger_ctx, customer_ctx=None):
    merchant = merchant_ctx or {}
    trigger = trigger_ctx or {}
    customer = customer_ctx or {}

    # Context values safely extract karna
    payload = merchant.get("payload", merchant) if isinstance(merchant, dict) else {}
    identity = payload.get("identity", payload) if isinstance(payload, dict) else {}
    performance = payload.get("performance", {}) if isinstance(payload, dict) else {}
    offers = payload.get("offers", []) if isinstance(payload, dict) else {}

    category = identity.get("category", "retail") if isinstance(identity, dict) else "retail"
    business_name = identity.get("name", "your store") if isinstance(identity, dict) else "your store"

    trigger_kind = trigger.get("kind", "merchant_query") if isinstance(trigger, dict) else "merchant_query"
    trigger_data = trigger.get("data", trigger) if isinstance(trigger, dict) else trigger

    offer_text = f"Current offer: {offers[0]}" if (isinstance(offers, list) and len(offers) > 0) else ""
    perf_text = f"Recent metrics: {performance}" if performance else ""
    customer_text = f"Customer info: {customer}" if customer else ""

    prompt = f"""You are Vera, magicpin's AI assistant for merchant growth in India.

Merchant: {business_name}
Category: {category}
{perf_text}
{offer_text}
Trigger: {trigger_kind} - {trigger_data}
{customer_text}

Write ONE short WhatsApp-style message from Vera to this merchant.
Rules:
- Be specific, helpful, and natural
- Use natural Hinglish (Hindi-English mix)
- Give ONE clear CTA
- Max 3 sentences

Respond in EXACTLY this format:
MESSAGE: <message>
CTA: <action>
SEND_AS: vera
SUPPRESSION_KEY: trigger:{business_name}
RATIONALE: Growth recommendation"""

    # Safe fallback agar Gemini API call fail ho ya empty response aaye
    default_result = {
        "message": f"Namaste! Ham aapke store '{business_name}' ke footfall badhane ke liye naye offers plan kar sakte hain.",
        "cta": "Reply YES to activate",
        "send_as": "vera",
        "suppression_key": f"reply:{business_name}",
        "rationale": "Direct growth assistance"
    }

    try:
        response = model.generate_content(prompt)
        text = response.text.strip() if response and hasattr(response, "text") else ""

        result = {}
        for raw_line in text.split("\n"):
            line = raw_line.strip().replace("**", "")  # Bold markdown clean karna
            if line.upper().startswith("MESSAGE:"):
                result["message"] = line[len("MESSAGE:"):].strip()
            elif line.upper().startswith("CTA:"):
                result["cta"] = line[len("CTA:"):].strip()
            elif line.upper().startswith("SEND_AS:"):
                result["send_as"] = line[len("SEND_AS:"):].strip()
            elif line.upper().startswith("SUPPRESSION_KEY:"):
                result["suppression_key"] = line[len("SUPPRESSION_KEY:"):].strip()
            elif line.upper().startswith("RATIONALE:"):
                result["rationale"] = line[len("RATIONALE:"):].strip()

        # Missing fields ko default se fill karo
        for key, val in default_result.items():
            if not result.get(key):
                result[key] = val

        return result

    except Exception as e:
        print(f"Error in compose Gemini call: {e}")
        return default_result