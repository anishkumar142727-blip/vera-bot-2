import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def compose(merchant_ctx, trigger_ctx, customer_ctx=None):
    merchant = merchant_ctx or {}
    trigger = trigger_ctx or {}
    customer = customer_ctx or {}

    identity = merchant.get("identity", {})
    performance = merchant.get("performance", {})
    offers = merchant.get("offers", [])
    category = identity.get("category", "general")
    business_name = identity.get("name", "your business")

    trigger_kind = trigger.get("kind", "general")
    trigger_data = trigger.get("data", {})

    offer_text = ""
    if offers:
        o = offers[0]
        offer_text = f"Current offer: {o.get('title', '')} at {o.get('price', '')}"

    perf_text = ""
    if performance:
        perf_text = f"Recent metrics: {performance}"

    customer_text = ""
    if customer:
        customer_text = f"Customer info: {customer}"

    prompt = f"""You are Vera, magicpin's AI assistant for merchant growth in India.

Merchant: {business_name}
Category: {category}
{perf_text}
{offer_text}
Trigger: {trigger_kind} - {trigger_data}
{customer_text}

Write ONE short WhatsApp-style message from Vera to this merchant.
Rules:
- Be specific: use real numbers, offers, and facts from the context above
- Match the category tone (clinic=clinical, salon=visual, restaurant=appetizing)
- Give ONE clear CTA (yes/no action)
- Max 3 sentences
- Sound like a helpful assistant, not spam
- Use Hindi-English mix naturally

Also provide:
- cta: the single action you want merchant to take
- send_as: "vera" always
- suppression_key: string like "trigger_type:merchant_id"
- rationale: one line why this message now

Respond in EXACTLY this format, nothing else:
MESSAGE: <your message here>
CTA: <one action>
SEND_AS: vera
SUPPRESSION_KEY: <key>
RATIONALE: <one line>"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    result = {}
    for line in text.split("\n"):
        if line.startswith("MESSAGE:"):
            result["message"] = line.replace("MESSAGE:", "").strip()
        elif line.startswith("CTA:"):
            result["cta"] = line.replace("CTA:", "").strip()
        elif line.startswith("SEND_AS:"):
            result["send_as"] = line.replace("SEND_AS:", "").strip()
        elif line.startswith("SUPPRESSION_KEY:"):
            result["suppression_key"] = line.replace("SUPPRESSION_KEY:", "").strip()
        elif line.startswith("RATIONALE:"):
            result["rationale"] = line.replace("RATIONALE:", "").strip()

    return result 