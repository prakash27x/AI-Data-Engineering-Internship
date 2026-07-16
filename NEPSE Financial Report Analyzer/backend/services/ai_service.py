
from google import genai
from backend.core.config import settings
import json
from decimal import Decimal

MODEL_FALLBACKS = [
    "gemini-flash-latest",
    "gemini-2.5-pro",
    "models/gemini-2.5-pro",
    "gemini-2.5-flash",
    "models/gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash",
    "models/gemini-2.0-flash",
]


def _generate_text(prompt):
    """
    Send a prompt to Gemini, trying each model in fallback order.
    Returns the response text, or raises if none succeed.
    """
    last_error = None
    for model_name in MODEL_FALLBACKS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as model_err:
            last_error = model_err
            continue
    raise Exception(
        f"No available models could process the request. Last error: {last_error}"
    )


def _strip_code_fence(text):
    """Remove ```json / ``` fences that models sometimes wrap JSON in."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_decimal(i) for i in obj]
    return obj

client = None
if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_dashboard_insights(company_data, metrics_data):
    """
    Generate AI insights for a single company dashboard
    """
    if not client:
        return {
            "summary": ["AI insights disabled - API key not configured"],
            "risks": ["Check API key configuration"],
            "score": 0,
            "growth_score": 0,
            "profitability_score": 0,
            "liquidity_score": 0,
            "stability_score": 0,
            "risk_score": 0
        }

    company_data_clean = convert_decimal(company_data)
    metrics_data_clean = convert_decimal(metrics_data)

    prompt = f"""
You are a financial analyst specializing in Nepalese hydropower companies listed on NEPSE.
Given the following data for {company_data_clean.get('name', 'the company')}, generate a concise analysis.

Company Data:
- Symbol: {company_data_clean.get('symbol', '')}
- Sector: {company_data_clean.get('sector', '')}
- Period: {company_data_clean.get('fiscal_year', '')} {company_data_clean.get('quarter', '')}

Metrics:
{metrics_data_clean}

Please provide:
1. A short executive summary (max 4 bullet points)
2. Key risks (max 3 bullet points)
3. A score from 0-100 for each category:
   - Growth
   - Profitability
   - Liquidity
   - Stability
   - Risk (0 = high risk, 100 = low risk)

Return the response ONLY as valid JSON, no extra text. Use exact keys:
{{
    "summary": ["bullet1", "bullet2"],
    "risks": ["risk1", "risk2"],
    "score": overall_score_0_100,
    "growth_score": score,
    "profitability_score": score,
    "liquidity_score": score,
    "stability_score": score,
    "risk_score": score
}}
"""

    try:
        text = _generate_text(prompt)
        text = _strip_code_fence(text)
        return convert_decimal(json.loads(text))
    except Exception as e:
        print(f"Error generating dashboard insights: {e}")
        return {
            "summary": [f"Could not generate AI insights at this time. Error: {str(e)}"],
            "risks": ["Check API key configuration and internet connection"],
            "score": 50,
            "growth_score": 50,
            "profitability_score": 50,
            "liquidity_score": 50,
            "stability_score": 50,
            "risk_score": 50
        }

def generate_comparison_insights(company_a, company_b, comparison_rows):
    """
    Generate AI insights for comparing two companies
    """
    if not client:
        return {
            "risk_perspective": "AI insights disabled - API key not configured",
            "growth_trajectory": "AI insights disabled - API key not configured"
        }

    company_a_clean = convert_decimal(company_a)
    company_b_clean = convert_decimal(company_b)
    comparison_rows_clean = convert_decimal(comparison_rows)

    prompt = f"""
You are a financial analyst specializing in Nepalese hydropower companies listed on NEPSE.
Compare the following two companies based on the provided metrics.

Company A: {company_a_clean.get('symbol', '')}
Company B: {company_b_clean.get('symbol', '')}

Metrics Comparison:
{comparison_rows_clean}

Please provide:
1. Risk Perspective - analyze leverage, liquidity, and earning-quality notes (1 paragraph)
2. Growth Trajectory - revenue and profit momentum summary (1 paragraph)

Return ONLY as valid JSON, no extra text, with exact keys:
{{
    "risk_perspective": "text here",
    "growth_trajectory": "text here"
}}
"""

    try:
        text = _generate_text(prompt)
        text = _strip_code_fence(text)
        return convert_decimal(json.loads(text))
    except Exception as e:
        print(f"Error generating comparison insights: {e}")
        return {
            "risk_perspective": f"Could not generate AI insights at this time. Error: {str(e)}",
            "growth_trajectory": "Check API key configuration and internet connection"
        }

def generate_chat_response(question, dashboard_data):
    """
    Generate chat response, guard against out-of-context questions
    """
    if not client:
        return "AI insights are currently disabled. Please configure your API key in the .env file."
    
    dashboard_data_clean = convert_decimal(dashboard_data)

    q = (question or "").strip()
    if not q:
        return "Please ask a question about the selected company's financial metrics for the selected quarter."

    q_lower = q.lower()
    allowed_keywords = [
        "risk",
        "revenue",
        "sale",
        "profit",
        "loss",
        "income",
        "expense",
        "margin",
        "growth",
        "trend",
        "assets",
        "asset",
        "equity",
        "liability",
        "debt",
        "cash",
        "liquidity",
        "solvency",
        "ratio",
        "quarter",
        "fiscal",
        "nepse",
        "hydro",
        dashboard_data_clean.get("company", {}).get("symbol", "").lower(),
        dashboard_data_clean.get("company", {}).get("name", "").lower(),
    ]

    if not any(k and k in q_lower for k in allowed_keywords):
        return (
            "I can only answer questions about the selected company's NEPSE financial metrics for the selected quarter "
            "(e.g., revenue, profit, assets, equity, growth, liquidity, risk)."
        )

    metrics_json = json.dumps(dashboard_data_clean.get("metrics", {}), ensure_ascii=False, indent=2)
    
    system_prompt = f"""
You are a financial assistant specializing only in Nepalese hydropower companies listed on NEPSE.
You can only answer questions related to the financial metrics and performance of {dashboard_data_clean['company']['name']} ({dashboard_data_clean['company']['symbol']}).

Here is the company's financial data for context:
Company: {dashboard_data_clean['company']['name']}
Symbol: {dashboard_data_clean['company']['symbol']}
Period: {dashboard_data_clean['company']['fiscal_year']} {dashboard_data_clean['company']['quarter']}

Financial Metrics:
{metrics_json}

IMPORTANT RULES:
1. If the question is NOT related to this company's financial performance, metrics, hydropower sector, or NEPSE, politely decline and say you can only help with questions about this company's financial data.
2. Always base your answers on the provided financial data.
3. Keep answers concise and professional.
4. Do not make up information not present in the data.
"""

    try:
        return _generate_text(f"{system_prompt}\n\nUser Question: {q}")
    except Exception as e:
        print(f"Error generating chat response: {e}")
        return f"Sorry, I'm having trouble answering that right now. Error: {str(e)}"
