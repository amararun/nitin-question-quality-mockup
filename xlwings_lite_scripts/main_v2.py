"""
Question Quality Assessment System - xlwings Lite
Version 3.0 - Thinking/Reasoning Token Support

Assesses educational questions against quality guidelines using 3 LLMs via OpenRouter

Key Changes in v3.0:
🧠 THINKING/REASONING SUPPORT:
- Intelligent model detection: Auto-detects Gemini 2.5 and GPT-5 models
- Gemini 2.5 models: thinking_budget parameter (0-24576 tokens, default: -1 dynamic)
- OpenAI GPT-5 models: reasoning_effort parameter (minimal/low/medium/high)
- Parameters passed natively to OpenRouter (no wrapper complexity)
- Master switch: "Thinking On (1) / Off (0)" in MASTER sheet

📊 DASHBOARD ENHANCEMENTS:
- New "Thinking" row shows active parameters per model (Budget: 8192 / Effort: medium)
- Total Reasoning Tokens metric
- Reasoning Cost metric (billed at output pricing)
- Updated formula: Total Tokens = Input + Output + Reasoning

🔧 API METRICS:
- API_METRICS sheet now includes Reasoning_Tokens column
- Console logging shows reasoning tokens when detected
- Checks both 'reasoning_tokens' and 'thinking_tokens' keys (provider flexibility)

💡 INTELLIGENT PARAMETER HANDLING:
- Only adds thinking parameters if model supports it (no errors on non-thinking models)
- Supports all variants: gemini-2.5-flash/flash-lite/pro, gpt-5/gpt-5-mini/gpt-5-nano

🧪 MANUAL TESTING SUPPORT:
- NEW: get_manual_test_payload() function
- Generates exact JSON payload for AI Studio/Gemini Playground testing
- Ensures consistency between manual testing and automation
- Outputs first batch only to MANUAL_TEST_JSON sheet

📄 SYSTEM PROMPT MANAGEMENT:
- Complete system prompt loaded from PROMPT sheet cell A1
- User uploads TXT file via VBA button
- No more hardcoded instructions in Python code
- Validation: stops execution if prompt is missing or too short

Previous Changes (v2.9):
- Fixed "Total Time" metric showing blank in Total column
- Non-numeric columns (time strings) now copy values from first model in Total column

Previous Changes (v2.8):
- API key now checks ENVIRONMENT VARIABLES FIRST, then MASTER sheet
- Follows xlwings Lite security best practices (store secrets in add-in environment)

Previous Changes (v2.6):
- RE-ADDED time metrics to dashboard (HH:MM:SS format)
- Both cost metrics: Cost per 1K Questions and Cost per 100K Questions

Previous Changes (v2.3):
- Added cost projection metric to dashboard for budget planning
- Verified token extraction from API response (prompt_tokens, completion_tokens, total_tokens)
- Confirmed cost calculation uses per-million token rates from T_COST table

Previous Changes (v2.2):
- Fixed dashboard row alignment issues
- Improved HTML tag preservation in LLM prompts
- Fixed percentage calculations (removed double multiplication)
- Added separate Input/Output token rows
- Removed currency symbols from cost columns
- Used .resize() instead of .expand() for reliable table creation

Author: AI Coding Assistant guided by Amar Harolikar
Version: 3.2
Date: 2025-11-17

Key Changes in v3.2:
- Dashboard now includes Max Tokens, Temperature, and Top P parameters.

Key Changes in v3.1:
- ASSESSMENT_RESULTS sheet now includes a 'questionid' column.
"""

import xlwings as xw
from xlwings import script
import pandas as pd
import json
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any
import time
import re
import os

import numpy as np

# ==================== MODEL NAME MAPPING ====================

MODEL_DISPLAY_NAMES = {
    'model_1': 'Claude',
    'model_2': 'OpenAI',
    'model_3': 'Gemini'
}

MODEL_CONFIG = {
    'model_1': {
        'name': 'Claude',
        'key': 'ANTHROPIC_MODEL',
        'default': 'anthropic/claude-3-5-haiku-20241022'
    },
    'model_2': {
        'name': 'OpenAI',
        'key': 'OPENAI_MODEL',
        'default': 'openai/gpt-4o-mini'
    },
    'model_3': {
        'name': 'Gemini',
        'key': 'GEMINI_MODEL',
        'default': 'google/gemini-2.0-flash-lite'
    }
}

# ==================== SYSTEM PROMPT ====================

# The complete system prompt (user guidelines + technical instructions) is loaded from:
# - Excel PROMPT sheet, Cell A1
# - User uploads their TXT file via VBA button which pastes content into A1
# - File should contain user guidelines + separator + technical instructions
# - See: docs/QUESTION_GUIDELINES_20251112.txt for template

def get_short_model_name(full_model_string: str) -> str:
    if '/' in full_model_string:
        return full_model_string.split('/')[-1]
    return full_model_string # Return as is if no slash

def format_time_hms(seconds: float) -> str:
    """
    Format seconds into human-readable HH:MM:SS format
    Examples: "02h 15m 30s", "00h 00m 45s", "10h 05m 12s"
    """
    if seconds == 0:
        return "00h 00m 00s"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"



# ==================== CONFIGURATION LOADER ====================

def find_config_value(sheet: xw.Sheet, param_name: str, column: str = 'C', default_value=None):
    """
    Search for a parameter name in column A and return corresponding value from a specified column.

    Args:
        sheet: Excel sheet to search
        param_name: Parameter name to find (case-insensitive, flexible matching)
        column: Column to get the value from (e.g., 'C', 'D'). Defaults to 'C'.
        default_value: Value to return if not found

    Returns:
        Value from the specified column, or default_value if not found
    """
    try:
        # Read column A (parameter names) - read first 50 rows
        param_names = sheet.range('A1:A50').value

        # Normalize search term
        search_term = param_name.lower().replace('_', '').replace(' ', '')

        for idx, cell_value in enumerate(param_names, start=1):
            if cell_value is None:
                continue

            # Normalize cell value
            cell_normalized = str(cell_value).lower().replace('_', '').replace(' ', '')

            if search_term in cell_normalized:
                # Found it! Get corresponding value from the specified column
                value = sheet[f'{column}{idx}'].value
                # Only print for the main value column 'C' to avoid clutter
                if column == 'C':
                    print(f"   Found {param_name} = {value} (row {idx})")
                return value

        # Only print for the main value column 'C'
        if column == 'C':
            print(f"   {param_name} not found, using default: {default_value}")
        return default_value

    except Exception as e:
        print(f"   Error finding {param_name}: {e}, using default: {default_value}")
        return default_value


def load_config(book: xw.Book) -> Dict:
    """Load configuration from environment variables and MASTER sheet with flexible parameter search"""
    print("📋 Loading configuration from environment variables and MASTER sheet...")

    try:
        master_sheet = book.sheets["MASTER"]

        # Check for API key in environment variable FIRST, then fall back to MASTER sheet
        api_key_from_env = os.getenv("OPENROUTER_API_KEY")
        api_key_from_sheet = find_config_value(master_sheet, "OPENROUTER_API_KEY", default_value="")

        if api_key_from_env:
            api_key = str(api_key_from_env)
            print(f"   ✅ Using OPENROUTER_API_KEY from environment variable")
        else:
            api_key = str(api_key_from_sheet or "")
            print(f"   ℹ️  No environment variable found, using OPENROUTER_API_KEY from MASTER sheet")

        # Read all configuration with flexible search
        config = {
            "api_key": api_key,
            "model_1": str(find_config_value(master_sheet, "LLM 1", default_value="anthropic/claude-3-5-haiku-20241022") or "anthropic/claude-3-5-haiku-20241022"),
            "model_2": str(find_config_value(master_sheet, "LLM 2", default_value="openai/gpt-4o-mini") or "openai/gpt-4o-mini"),
            "model_3": str(find_config_value(master_sheet, "LLM 3", default_value="google/gemini-2.0-flash-lite") or "google/gemini-2.0-flash-lite"),
            "temperature": float(master_sheet['C14'].value or 0.3),
            "top_p": float(find_config_value(master_sheet, "TOPP", default_value=0.9) or 0.9),
            "max_tokens": int(find_config_value(master_sheet, "MAX_TOKENS", default_value=2000) or 2000),
            "batch_size": int(find_config_value(master_sheet, "BATCH_SIZE", default_value=5) or 5),
            "start_row": int(find_config_value(master_sheet, "START_ROW", default_value=2) or 2),
            "end_row": int(end_row_val) if (end_row_val := find_config_value(master_sheet, "END_ROW", default_value=None)) is not None else None,
            "request_delay_seconds": float(find_config_value(master_sheet, "REQUEST_DELAY", default_value=0) or 0),
            "http_referer": str(find_config_value(master_sheet, "HTTP_REFERER", default_value="https://github.com") or "https://github.com"),
            "x_title": str(find_config_value(master_sheet, "X_TITLE", default_value="Question Quality Assessor") or "Question Quality Assessor"),
            # Thinking/Reasoning parameters (read directly from cell references)
            "thinking_budget_gemini": master_sheet['C26'].value,
            "reasoning_effort_openai": str(master_sheet['C27'].value).strip().lower() if master_sheet['C27'].value is not None else ""
        }

        # Read model enable/disable tags from column B by finding the label
        model_1_tag = find_config_value(master_sheet, "LLM 1", column='B', default_value=0)
        config['model_1_tag'] = 1 if str(model_1_tag).strip() == '1' else 0
        model_2_tag = find_config_value(master_sheet, "LLM 2", column='B', default_value=0)
        config['model_2_tag'] = 1 if str(model_2_tag).strip() == '1' else 0
        model_3_tag = find_config_value(master_sheet, "LLM 3", column='B', default_value=0)
        config['model_3_tag'] = 1 if str(model_3_tag).strip() == '1' else 0

        # Safety check: Ensure start_row is at least 2 (skip header)
        if config["start_row"] < 2:
            print(f"⚠️  START_ROW was {config['start_row']}, adjusting to 2 (header row)")
            config["start_row"] = 2

        # Validate API key
        if not config["api_key"] or config["api_key"] == "" or len(config["api_key"]) < 20:
            print("⚠️  WARNING: OPENROUTER_API_KEY appears invalid! API calls will likely fail.")
            print("   Key length:", len(config["api_key"]))
        else:
            # Show masked API key for verification (first 8 chars + last 4 chars)
            masked_key = config["api_key"][:8] + "..." + config["api_key"][-4:] if len(config["api_key"]) > 12 else "***"
            print(f"   API Key detected: {masked_key} (length: {len(config['api_key'])} chars)")

        print(f"\n✅ Configuration loaded successfully:")
        print(f"   Model 1: {config['model_1']} (Enabled: {config['model_1_tag'] == 1})")
        print(f"   Model 2: {config['model_2']} (Enabled: {config['model_2_tag'] == 1})")
        print(f"   Model 3: {config['model_3']} (Enabled: {config['model_3_tag'] == 1})")
        print(f"   Processing rows:     {config['start_row']} to {config['end_row']}")
        print(f"   Temperature:         {config['temperature']}")
        print(f"   Top-P:               {config['top_p']}")
        print(f"   Max Tokens:          {config['max_tokens']}")
        print(f"   Batch Size:          {config['batch_size']}")
        print(f"   Request Delay (s):   {config['request_delay_seconds']}")
        print(f"   HTTP Referer:        {config['http_referer']}")
        print(f"   X-Title:             {config['x_title']}")

        # Load complete system prompt from PROMPT sheet (uploaded via VBA)
        print("   Loading system prompt from PROMPT sheet...")
        try:
            prompt_sheet = book.sheets["PROMPT"]
            system_prompt = prompt_sheet.range("A1").value

            # Validate prompt is present and has minimum content
            if not system_prompt or str(system_prompt).strip() == "":
                raise ValueError("❌ PROMPT sheet cell A1 is EMPTY! Please upload your instruction file using the VBA button.")

            if len(str(system_prompt).strip()) < 100:
                raise ValueError(f"❌ PROMPT sheet cell A1 content is TOO SHORT ({len(str(system_prompt))} chars). Expected complete instructions. Please upload your instruction file.")

            config["system_prompt"] = str(system_prompt).strip()
            print(f"   ✅ System prompt loaded successfully ({len(config['system_prompt'])} characters)")

            # Print preview
            print("-" * 20 + " PROMPT PREVIEW " + "-" * 20)
            print(str(system_prompt)[:300] + "...")
            print("-" * 56)

        except Exception as e:
            # Critical error - stop execution
            print(f"\n{'='*80}")
            print(f"❌ CRITICAL ERROR: Cannot load system prompt from 'PROMPT' sheet")
            print(f"{'='*80}")
            print(f"Reason: {e}")
            print(f"\nACTION REQUIRED:")
            print(f"1. Open your instruction TXT file (e.g., QUESTION_GUIDELINES_20251112.txt)")
            print(f"2. Click the VBA 'Upload Instructions' button to paste it into PROMPT sheet cell A1")
            print(f"3. Re-run the assessment")
            print(f"{'='*80}\n")
            raise

        return config

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        raise


# NOTE: Future enhancement - load guidelines from Google Drive
def load_guidelines_from_url(url: str) -> str:
    """
    Load quality guidelines from a Google Drive or GitHub URL

    CURRENTLY NOT USED - Guidelines are hardcoded above

    Future usage:
    1. Add GUIDELINES_URL to MASTER sheet
    2. For Google Drive: Convert share link to direct download URL
       Example: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
       Becomes: https://drive.google.com/uc?export=download&id=FILE_ID
    3. For GitHub: Use raw.githubusercontent.com URL
    4. Uncomment code below and call this function in assess_questions
    """
    # import requests
    # try:
    #     response = requests.get(url, timeout=10)
    #     if response.status_code == 200:
    #         return response.text
    #     else:
    #         print(f"Failed to load guidelines from URL: {response.status_code}")
    #         return QUALITY_GUIDELINES  # Fallback to hardcoded
    # except Exception as e:
    #     print(f"Error loading guidelines from URL: {e}")
    #     return QUALITY_GUIDELINES  # Fallback
    pass


# ==================== TABLE HELPER ====================

def find_table_in_workbook(book: xw.Book, table_name: str) -> Tuple[Optional[Any], Optional[Any]]:
    """
    MANDATORY HELPER: xlwings Lite Table objects have no .sheet attribute
    Returns: (sheet, table) or (None, None) if not found

    This is the mandatory pattern from AI_CODER_INSTRUCTIONS.md section 3.1
    """
    for sheet in book.sheets:
        if table_name in sheet.tables:
            return sheet, sheet.tables[table_name]
    return None, None


# ==================== OPENROUTER API CLIENT ====================

def call_openrouter_api(
    model_name: str,
    messages: List[Dict],
    config: Dict,
    thinking_models_lookup: Dict,
    thinking_values_lookup: Dict,
    timeout: int = 30,
    batch_num: int = 1
) -> Tuple[Optional[Dict], Optional[str], float]:
    """
    Call OpenRouter API with specified model

    Args:
        model_name: Full model name (e.g., "google/gemini-2.5-flash-lite")
        messages: List of message dicts with role and content
        config: Configuration dictionary
        thinking_models_lookup: Dictionary mapping model names to thinking capability (1 or 0)
        thinking_values_lookup: Dictionary mapping model names to valid reasoning effort strings.
        timeout: Request timeout in seconds
        batch_num: Batch number (1-indexed) - enables detailed logging for batch #1

    Returns:
        (response_dict, error_message, latency_seconds)
    """
    import requests

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "HTTP-Referer": config['http_referer'],
        "X-Title": config['x_title'],
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": config['temperature'],
        "top_p": config['top_p'],
        "max_tokens": config['max_tokens']
    }

    # Add thinking/reasoning parameters based on model type and config
    is_thinking_model = thinking_models_lookup.get(model_name) == 1

    if is_thinking_model:
        # Handle Gemini Models
        if model_name.startswith('google/'):
            budget_val = config.get('thinking_budget_gemini')

            # If cell is blank or None, budget is 0 (off)
            if budget_val is None or str(budget_val).strip() == '':
                budget = 0
            else:
                budget = int(budget_val)

            # Apply clamping/capping logic only for positive budgets
            if budget > 0:
                is_pro = 'pro' in model_name.lower()
                min_val = 128 if is_pro else 512
                max_val = 32768 if is_pro else 24576

                if budget < min_val:
                    print(f"   🧠 Gemini budget was {budget}, bumping up to minimum of {min_val}")
                    budget = min_val
                elif budget > max_val:
                    print(f"   🧠 Gemini budget was {budget}, capping at maximum of {max_val}")
                    budget = max_val
            
            # Only add the parameter if the budget is not 0
            if budget != 0:
                payload['thinking_budget'] = budget
                print(f"   🧠 Applying Gemini thinking_budget: {budget}")

        # Handle OpenAI Models
        elif model_name.startswith('openai/'):
            user_effort = config.get('reasoning_effort_openai')

            # Only proceed if the user has entered a value.
            # If the cell is blank, we send no parameter, letting the API use its default.
            if user_effort and user_effort.strip():
                # User provided a value, so we must validate it.
                valid_efforts_str = thinking_values_lookup.get(model_name)

                # Check if the model is supposed to have reasoning effort values defined in T_COST.
                if not valid_efforts_str or not str(valid_efforts_str).strip():
                     raise ValueError(f"Model '{model_name}' does not support the 'reasoning_effort' parameter, but a value was provided. Please clear cell C27 in the MASTER sheet.")

                valid_efforts = [v.strip() for v in str(valid_efforts_str).split(',')]

                if user_effort not in valid_efforts:
                    raise ValueError(f"Invalid reasoning_effort '{user_effort}' for model '{model_name}'. Supported values are: {valid_efforts}")

                # If validation passes, add it to the payload.
                payload['reasoning_effort'] = user_effort
                print(f"   🧠 Applying OpenAI reasoning_effort: {user_effort}")

    # DETAILED LOGGING FOR BATCH #1 ONLY
    if batch_num == 1:
        print("\n" + "="*80)
        print("🔍 DETAILED API REQUEST LOG - BATCH #1 ONLY")
        print("="*80)
        print("\n📋 MODEL CONFIGURATION:")
        print(f"   Model: {model_name}")
        print(f"   Temperature: {config['temperature']}")
        print(f"   Top-P: {config['top_p']}")
        print(f"   Max Tokens: {config['max_tokens']}")
        
        # Updated logging for thinking parameters
        if 'thinking_budget' in payload:
            print(f"   Thinking Budget (Gemini): {payload['thinking_budget']}")
        elif 'reasoning_effort' in payload:
            print(f"   Reasoning Effort (OpenAI): {payload['reasoning_effort']}")
        else:
            print("   Thinking/Reasoning: Off")

        print("\n📝 SYSTEM PROMPT (First 500 chars):")
        print("-" * 80)
        system_content = messages[0]['content'] if messages and messages[0]['role'] == 'system' else 'N/A'
        print(system_content[:500])
        print("..." if len(system_content) > 500 else "")
        print(f"\n[Total System Prompt Length: {len(system_content)} characters]")

        print("\n📦 USER PAYLOAD (Questions JSON - First 1000 chars):")
        print("-" * 80)
        user_content = messages[1]['content'] if len(messages) > 1 and messages[1]['role'] == 'user' else 'N/A'
        print(user_content[:1000])
        print("..." if len(user_content) > 1000 else "")
        print(f"\n[Total User Payload Length: {len(user_content)} characters]")

        print("\n🌐 FULL API PAYLOAD (Complete JSON):")
        print("-" * 80)
        print(json.dumps(payload, indent=2))
        print("\n" + "="*80)
        print("🚀 SENDING REQUEST TO OPENROUTER...")
        print("="*80 + "\n")

    # Minimal logging for production (200K+ records)
    start_time = time.time()

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        latency = time.time() - start_time

        if response.status_code == 200:
            # Check if response is empty
            if not response.text or response.text.strip() == "":
                error_msg = f"Empty response from OpenRouter"
                return None, error_msg, latency

            try:
                response_json = response.json()
                return response_json, None, latency
            except json.JSONDecodeError as je:
                error_msg = f"Invalid JSON response: {str(je)}"
                return None, error_msg, latency
        else:
            # Enhanced error reporting for non-200 status codes
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                if 'error' in error_detail:
                    error_msg += f" - {error_detail['error']}"
            except:
                # If response is not JSON, try to get text
                if response.text:
                    error_msg += f" - {response.text[:200]}"

            # Special handling for 401 errors
            if response.status_code == 401:
                error_msg += " (AUTHENTICATION FAILED - Check your OPENROUTER_API_KEY in MASTER sheet)"

            return None, error_msg, latency

    except requests.exceptions.Timeout:
        latency = time.time() - start_time
        error_msg = f"Timeout after {timeout}s"
        return None, error_msg, latency

    except Exception as e:
        latency = time.time() - start_time
        error_msg = str(e)
        return None, error_msg, latency


def parse_llm_response(response: Dict, model_name: str = "Unknown") -> Optional[Dict]:
    """
    Parse OpenRouter response and extract the LLM's JSON output.
    Expected format:
    {
      "change_required": 0 or 1,
      "feedback": {
        "question": {"issue": "", "rewrite": ""},
        "answer1": {"issue": "", "rewrite": ""},
        ...
      }
    }
    """
    try:
        content = response["choices"][0]["message"]["content"]

        print(f"   [DEBUG] {model_name} raw content length: {len(content)} chars")
        print(f"   [DEBUG] {model_name} first 100 chars: {content[:100]}")

        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            print(f"   [DEBUG] {model_name}: Found ```json block")
            content = content[7:]
        if content.startswith("```"):
            print(f"   [DEBUG] {model_name}: Found ``` block")
            content = content[3:]
        if content.endswith("```"):
            print(f"   [DEBUG] {model_name}: Removing trailing ```")
            content = content[:-3]
        content = content.strip()

        print(f"   [DEBUG] {model_name} cleaned content length: {len(content)} chars")

        # Parse JSON
        try:
            parsed = json.loads(content)
            print(f"   [DEBUG] {model_name}: JSON parsed successfully")
        except json.JSONDecodeError as je:
            print(f"   [DEBUG] {model_name}: JSON parse failed - {str(je)}")
            print(f"   [DEBUG] {model_name}: Content that failed: {content[:200]}")
            return None

        # Validate top-level structure
        required_keys = ["change_required", "feedback"]
        missing_keys = [k for k in required_keys if k not in parsed]
        if missing_keys:
            print(f"   [DEBUG] {model_name}: Missing top-level keys: {missing_keys}")
            return None

        # Ensure change_required is 0 or 1
        if parsed["change_required"] not in [0, 1]:
            print(f"   [DEBUG] {model_name}: Invalid change_required value: {parsed['change_required']}")
            return None
        
        # Validate feedback structure (at least 'question' should be present) and ensure it's a dict
        if not isinstance(parsed['feedback'], dict) or 'question' not in parsed['feedback']:
            print(f"   [DEBUG] {model_name}: Invalid or missing 'feedback' object.")
            return None

        # User experience improvement: if no change is required, make it explicit per item.
        # Iterate through all feedback items (question, answer1, etc.)
        for item_key, item_feedback in parsed['feedback'].items():
            if isinstance(item_feedback, dict):
                if item_feedback.get('issue', '').strip() == '' and item_feedback.get('rewrite', '').strip() == '':
                    item_feedback['issue'] = 'No changes needed.'
            else:
                # Ensure item_feedback is a dict, if not, initialize it
                parsed['feedback'][item_key] = {"issue": "Invalid feedback format.", "rewrite": ""}


        print(f"   [DEBUG] {model_name}: ✅ Valid JSON response")
        return parsed

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"   [DEBUG] {model_name}: Exception during parsing - {str(e)}")
        return None


# ==================== QUESTION PROCESSING ====================

def _clean_text(text):
    if pd.isna(text):
        return ""
    text_str = str(text)
    # A simplified cleaning, as the user wants to control `strip_html` from the prompt itself now.
    text_str = text_str.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text_str = text_str.replace('&quot;', '"').replace('&amp;', '&')
    return text_str.strip()


def prepare_question_batch_payload(batch_df: pd.DataFrame) -> str:
    """
    Prepare a batch of questions as a JSON array string for the LLM.
    Includes the questionid for reliable mapping of results.
    """
    payload_list = []
    for _, row in batch_df.iterrows():
        question_obj = {
            "questionid": row.get('questionid')
        }
        
        # Add question text and handle potential images
        question_text = _clean_text(row.get('question', ''))
        if pd.notna(row.get('questionImage')):
            question_text += " [Image present - visual content not assessed]"
        question_obj['question'] = question_text

        # Add answer options dynamically
        total_answers = int(row.get('totalanswers', 0))
        for i in range(1, total_answers + 1):
            answer_key = f'answer{i}'
            answer_text = _clean_text(row.get(answer_key, ''))
            if pd.notna(row.get(f'answer{i}Image')):
                answer_text += " [Image present - visual content not assessed]"
            question_obj[answer_key] = answer_text
        
        payload_list.append(question_obj)

    return json.dumps(payload_list, indent=2)


def parse_llm_batch_response(response: Dict, batch_df: pd.DataFrame) -> Tuple[Dict, str]:
    """
    Parses the JSON array from the LLM's batched response.
    Returns a dictionary of results mapped by questionid and an error string.
    """
    results_map = {}
    content = "" # Initialize content to avoid reference before assignment in except block
    try:
        content = response["choices"][0]["message"]["content"]

        # Clean the response content
        content = content.strip()

        # Handle markdown code blocks
        if content.startswith("```json"):
            content = content[7:].strip()
        elif content.startswith("```"):
            content = content[3:].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        # For reasoning models, extract JSON array from anywhere in the content
        # Look for the first '[' and last ']' to extract just the JSON array
        if not content.startswith('['):
            print("   [INFO] Response doesn't start with '[', attempting to extract JSON array...")
            start_idx = content.find('[')
            if start_idx != -1:
                end_idx = content.rfind(']')
                if end_idx != -1:
                    content = content[start_idx:end_idx+1]
                    print(f"   [INFO] Extracted JSON array from position {start_idx} to {end_idx}")

        # Parse the string into a Python list of feedback objects
        parsed_array = json.loads(content)
        
        if not isinstance(parsed_array, list):
            return {}, "LLM response was not a JSON array."

        # Map results by questionid for reliable processing
        for item in parsed_array:
            if 'questionid' in item:
                results_map[item['questionid']] = item
            else:
                print("   [WARN] Found a result item without a questionid, it will be ignored.")

        # Check if all original questionids were found in the response
        original_ids = set(batch_df['questionid'])
        returned_ids = set(results_map.keys())
        if original_ids != returned_ids:
            print(f"   [WARN] Mismatch in returned questionids. Missing: {original_ids - returned_ids}")

        return results_map, None

    except (KeyError, IndexError, json.JSONDecodeError, TypeError) as e:
        error_msg = f"Failed to parse LLM batch response: {e}"
        print(f"   [DEBUG] Content that failed parsing: {content[:500]}")
        return {}, error_msg


def assess_question_batch(batch_df: pd.DataFrame, config: Dict, thinking_models_lookup: Dict, thinking_values_lookup: Dict, batch_num: int = 1) -> Dict:
    """
    Assess a batch of questions with all enabled models.
    Returns a dictionary of dictionaries, keyed by questionid and then model_key.
    e.g., {3401: {'model_1': {...}, 'model_2': {...}}}

    Args:
        batch_df: DataFrame containing questions to assess
        config: Configuration dictionary
        thinking_models_lookup: Dictionary mapping model names to thinking capability (1 or 0)
        thinking_values_lookup: Dictionary mapping model names to valid reasoning effort strings.
        batch_num: Batch number (1-indexed) - used for detailed logging on first batch
    """
    # Use the complete system prompt loaded from PROMPT sheet
    system_prompt = config['system_prompt']

    question_payload = prepare_question_batch_payload(batch_df)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_payload}
    ]

    batch_results = {}

    for model_key in ['model_1', 'model_2', 'model_3']:
        if config.get(f'{model_key}_tag') != 1:
            continue

        full_model_name = config[model_key]  # e.g., "google/gemini-2.0-flash-lite"
        model_display = MODEL_DISPLAY_NAMES.get(model_key, model_key)  # e.g., "Gemini" (for console logs only)

        print(f"   -> Assessing batch of {len(batch_df)} questions with {model_display} ({full_model_name})...")

        response, error, latency = call_openrouter_api(full_model_name, messages, config, thinking_models_lookup, thinking_values_lookup, batch_num=batch_num)

        usage = response.get('usage', {}) if response else {}

        # DETAILED DIAGNOSTICS FOR BATCH #1 ONLY
        if batch_num == 1:
            print("\n" + "="*80)
            print("🔍 RAW API RESPONSE - USAGE OBJECT DIAGNOSTICS (BATCH #1 ONLY)")
            print("="*80)
            print(f"📊 Model: {full_model_name}")
            print(f"\n📦 Full Usage Object:")
            print(json.dumps(usage, indent=2))
            print("\n🔎 Token Extraction Attempts:")

        # Extract reasoning/thinking tokens (check multiple possible locations)
        reasoning_tokens = 0

        # Check nested location: completion_tokens_details.reasoning_tokens (OpenAI format)
        completion_details = usage.get('completion_tokens_details', {})
        reasoning_tokens_nested = completion_details.get('reasoning_tokens', 0)
        if batch_num == 1:
            print(f"   1. completion_tokens_details.reasoning_tokens: {reasoning_tokens_nested}")
        reasoning_tokens = reasoning_tokens_nested

        # Fallback: Check top-level reasoning_tokens
        reasoning_tokens_top = usage.get('reasoning_tokens', 0)
        if batch_num == 1:
            print(f"   2. usage.reasoning_tokens (top-level): {reasoning_tokens_top}")
        if reasoning_tokens == 0:
            reasoning_tokens = reasoning_tokens_top

        # Fallback: Check top-level thinking_tokens (Gemini format)
        thinking_tokens_top = usage.get('thinking_tokens', 0)
        if batch_num == 1:
            print(f"   3. usage.thinking_tokens (top-level): {thinking_tokens_top}")
        if reasoning_tokens == 0:
            reasoning_tokens = thinking_tokens_top

        if batch_num == 1:
            print(f"\n✅ Final Reasoning Tokens Value: {reasoning_tokens}")
            print("="*80 + "\n")

        tokens = {
            'input': usage.get('prompt_tokens', 0),
            'output': usage.get('completion_tokens', 0),
            'reasoning': reasoning_tokens,
            'total': usage.get('total_tokens', 0)
        }

        # Console log for reasoning token detection
        if reasoning_tokens > 0:
            print(f"      🧠 Reasoning tokens used: {reasoning_tokens}")

        # Common data for all questions in this batch for this model
        model_batch_info = {
            'model_key': model_key, 'model_name': full_model_name,  # Store FULL model name
            'latency': latency, 'tokens': tokens, 'raw_response': json.dumps(response) if response else None
        }

        if error:
            print(f"      ❌ Batch failed. Error: {error}")
            for qid in batch_df['questionid']:
                batch_results.setdefault(qid, {})[model_key] = {'error': error, **model_batch_info}
            continue

        parsed_results_map, parse_error = parse_llm_batch_response(response, batch_df)

        if parse_error:
            print(f"      ⚠️  Batch failed on parsing. Error: {parse_error}")
            for qid in batch_df['questionid']:
                batch_results.setdefault(qid, {})[model_key] = {'error': parse_error, **model_batch_info}
            continue

        print(f"      ✅ Batch successful. Parsed {len(parsed_results_map)} results.")
        # Map the parsed results back to the original questions
        for qid in batch_df['questionid']:
            result_for_qid = parsed_results_map.get(qid)
            if result_for_qid:
                batch_results.setdefault(qid, {})[model_key] = {'error': None, **result_for_qid, **model_batch_info}
            else:
                 batch_results.setdefault(qid, {})[model_key] = {'error': "Response missing for this questionid", **model_batch_info}

    return batch_results


# ==================== DASHBOARD HELPER (Not @script - callable from main) ====================

def build_and_write_dashboard(book: xw.Book, config: Dict, metrics_data: List[Dict], results_data: List[Dict], system_prompt_text: str):
    """
    Builds and writes an enhanced dashboard with prompt cost analysis and metric descriptions.
    """
    print("\n🎨 DASHBOARD: Starting build_and_write_dashboard()...")

    METRIC_DESCRIPTIONS = {
        "Thinking": "Shows thinking/reasoning parameters if enabled for the model. Budget for Gemini, Effort for OpenAI.",
        "Max Tokens": "Maximum number of tokens the model is allowed to generate in its response.",
        "Temperature": "Controls the randomness of the model's output. Higher values mean more random.",
        "Top P": "Controls the diversity of the model's output by sampling from the most probable tokens whose cumulative probability exceeds top_p.",
        "Total API Calls": "Total number of API requests made to the model.",
        "Successful API Calls": "Number of API requests that returned a successful (200) response.",
        "Total Items": "Total number of questions processed by the model (i.e., number of rows from T_QUESTIONS).",
        "Successful Items": "Number of questions for which a valid, parsable response was received from the model.",
        "Failed Items": "Number of questions for which the API call or response parsing failed.",
        "Changes Recommended": "Count of questions where the model indicated 'change_required' was 1.",
        "Change Rate (%)": "Percentage of successful items where changes were recommended. (Changes Recommended / Successful Items)",
        "Total Time": "Total time spent on all API calls for the model (HH:MM:SS). Sum of 'Latency_Seconds' from API_METRICS.",
        "Time per Question": "Average time taken to process a single question. (Total Time / Total Items)",
        "Time per API Call": "Average latency for a single API call. (Total Time / Total API Calls)",
        "Total Input Tokens": "Sum of all input tokens used for this model. Actual value from API response.",
        "Total Output Tokens": "Sum of all output tokens generated by this model. Actual value from API response.",
        "Total Reasoning Tokens": "Sum of all reasoning/thinking tokens used. Billed at output rate. Actual value from API response.",
        "Total Tokens": "Sum of Input, Output, and Reasoning tokens.",
        "System Prompt Tokens (Est.)": "Estimated tokens for the complete system prompt loaded from PROMPT sheet. Calculated as (number of characters / 4).",
        "Total System Prompt Tokens (Est.)": "Estimated total tokens used by the system prompt across all calls. (System Prompt Tokens) * Total API Calls",
        "Prompt Share of Input (%)": "The percentage of total input tokens that were used by the system prompt.",
        "Input Cost": "Total cost for input tokens. Calculated as (Total Input Tokens / 1,000,000) * Input Price from T_COST.",
        "Output Cost": "Total cost for output tokens. Calculated as (Total Output Tokens / 1,000,000) * Output Price from T_COST.",
        "Reasoning Cost": "Total cost for reasoning tokens. Billed at output price. (Total Reasoning Tokens / 1,000,000) * Output Price from T_COST.",
        "Total Cost": "Sum of Input, Output, and Reasoning costs.",
        "Cost per 1K Questions (USD)": "Projected cost to process 1,000 questions based on the current run's average cost per question.",
        "Cost per 100K Questions (USD)": "Projected cost to process 100,000 questions based on the current run's average cost per question.",
        "Total Time per 100K Questions": "Projected time to process 100,000 questions based on the current run's average time per question."
    }
    
    try:
        # --- Initial Setup and Calculations ---
        cost_sheet, cost_table = find_table_in_workbook(book, "T_COST")
        cost_lookup = {}
        if cost_table:
            cost_df = cost_table.range.options(pd.DataFrame, index=False).value
            cost_df.columns = [str(c).upper() for c in cost_df.columns]

            if cost_df['MODEL'].duplicated().any():
                print("   ⚠️  DASHBOARD: T_COST has duplicate model names. Keeping first occurrence only.")
                cost_df = cost_df.drop_duplicates(subset='MODEL', keep='first')

            cost_df.set_index('MODEL', inplace=True)
            cost_lookup = cost_df.to_dict('index')
            print("   ✅ DASHBOARD: T_COST table loaded.")
        else:
            print("   ⚠️  DASHBOARD: T_COST table not found. Cost calculations will be skipped.")

        if not metrics_data:
            print("   🔴 DASHBOARD: No metrics data provided, skipping.")
            return

        # Estimate system prompt tokens (1 token ≈ 4 characters)
        system_prompt_tokens = round(len(system_prompt_text) / 4)
        prompt_tokens_per_call = system_prompt_tokens

        metrics_df = pd.DataFrame(metrics_data)
        results_df = pd.DataFrame(results_data)
        dashboard_data = []
        active_models = metrics_df['Model_Key'].unique()

        # --- Per-Model Calculation Loop ---
        for model_key in active_models:
            full_model_name = config[model_key]
            display_model_name = get_short_model_name(full_model_name)
            print(f"\n   📊 DASHBOARD: Processing {display_model_name}...")

            model_metrics = metrics_df[metrics_df['Model_Key'] == model_key]
            model_results = results_df[results_df['Model'] == display_model_name]

            total_api_calls = len(model_metrics)
            total_input_tokens = int(model_metrics['Input_Tokens'].sum())
            total_output_tokens = int(model_metrics['Output_Tokens'].sum())
            total_reasoning_tokens = int(model_metrics['Reasoning_Tokens'].sum())
            total_prompt_tokens = prompt_tokens_per_call * total_api_calls
            prompt_share_of_input = (total_prompt_tokens / total_input_tokens) if total_input_tokens > 0 else 0

            model_costs = cost_lookup.get(config[model_key], {'INPUT': 0, 'OUTPUT': 0})
            input_cost = (total_input_tokens / 1_000_000) * float(model_costs.get('INPUT', 0))
            output_cost = (total_output_tokens / 1_000_000) * float(model_costs.get('OUTPUT', 0))
            reasoning_cost = (total_reasoning_tokens / 1_000_000) * float(model_costs.get('OUTPUT', 0))
            total_cost = input_cost + output_cost + reasoning_cost

            successful_items = model_results['Change Required?'].notna().sum() / 3
            changes_recommended = (model_results['Change Required?'] == 1).sum() / 3

            total_time_seconds = model_metrics['Latency_Seconds'].sum()
            batch_size = config['batch_size']
            total_questions_processed = total_api_calls * batch_size
            time_per_question_seconds = (total_time_seconds / total_questions_processed) if total_questions_processed > 0 else 0
            time_per_api_call_seconds = (total_time_seconds / total_api_calls) if total_api_calls > 0 else 0

            cost_per_1k = (total_cost / total_questions_processed * 1_000) if total_questions_processed > 0 else 0
            cost_per_100k = (total_cost / total_questions_processed * 100_000) if total_questions_processed > 0 else 0
            
            time_per_100k_seconds = (total_time_seconds / total_questions_processed * 100_000) if total_questions_processed > 0 else 0
            formatted_time_per_100k = format_time_hms(time_per_100k_seconds)

            dashboard_data.append({
                'Model': display_model_name,
                'Total API Calls': total_api_calls,
                'Successful API Calls': len(model_metrics[model_metrics['Status'] == 'SUCCESS']),
                'Total Items': len(model_results) / 3,
                'Successful Items': successful_items,
                'Failed Items': (len(model_results) / 3) - successful_items,
                'Changes Recommended': int(changes_recommended),
                'Change Rate (%)': (changes_recommended / successful_items) if successful_items > 0 else 0,
                'Total Time': format_time_hms(total_time_seconds),
                'Time per Question': format_time_hms(time_per_question_seconds),
                'Time per API Call': format_time_hms(time_per_api_call_seconds),
                'Total Input Tokens': total_input_tokens,
                'Total Output Tokens': total_output_tokens,
                'Total Reasoning Tokens': total_reasoning_tokens,
                'Total Tokens': total_input_tokens + total_output_tokens + total_reasoning_tokens,
                'System Prompt Tokens (Est.)': system_prompt_tokens,
                'Total System Prompt Tokens (Est.)': total_prompt_tokens,
                'Prompt Share of Input (%)': prompt_share_of_input,
                'Input Cost': input_cost,
                'Output Cost': output_cost,
                'Reasoning Cost': reasoning_cost,
                'Total Cost': total_cost,
                'Cost per 1K Questions (USD)': cost_per_1k,
                'Cost per 100K Questions (USD)': cost_per_100k,
                'Total Time per 100K Questions': formatted_time_per_100k
            })

        # --- Final DataFrame Assembly & Formatting ---
        print("\n   ✅ DASHBOARD: Built all model rows.")
        dashboard_df = pd.DataFrame(dashboard_data)

        if not dashboard_df.empty:
            total_row = {}
            for col in dashboard_df.columns:
                if col == 'Model':
                    total_row[col] = 'Total'
                elif dashboard_df[col].dtype in ['int64', 'float64']:
                    total_row[col] = dashboard_df[col].sum()
                else:
                    if len(dashboard_df) > 0:
                        total_row[col] = dashboard_df[col].iloc[0]
                    else:
                        total_row[col] = ''

            dashboard_df = pd.concat([dashboard_df, pd.DataFrame([total_row])], ignore_index=True)
            dashboard_df = dashboard_df.set_index('Model').T.reset_index().rename(columns={'index': 'Metric'})
            
            # Add the Description column
            dashboard_df['Description'] = dashboard_df['Metric'].map(METRIC_DESCRIPTIONS).fillna('')
            print("   ✅ DASHBOARD: Added 'Description' column.")

            thinking_row = {'Metric': 'Thinking', 'Description': METRIC_DESCRIPTIONS.get('Thinking', '')}

            for col in dashboard_df.columns:
                if col in ['Metric', 'Description']:
                    continue
                if col == 'Total':
                    thinking_row[col] = ''
                else:
                    # Find the full model name corresponding to the short display name (column header)
                    full_model_name = next((config[mk] for mk in ['model_1', 'model_2', 'model_3'] if get_short_model_name(config[mk]) == col), None)
                    if full_model_name:
                        model_cost_info = cost_lookup.get(full_model_name, {})
                        is_thinking_model = model_cost_info.get('THINKING') == 1

                        if is_thinking_model:
                            if full_model_name.startswith('google/'):
                                budget_val = config.get('thinking_budget_gemini')
                                if budget_val is None or str(budget_val).strip() == '':
                                    thinking_row[col] = 'Off (Blank)'
                                else:
                                    thinking_row[col] = f"Budget: {budget_val}"
                            elif full_model_name.startswith('openai/'):
                                effort_val = config.get('reasoning_effort_openai')
                                if effort_val is None or str(effort_val).strip() == '':
                                    thinking_row[col] = 'Effort: minimal (Default)'
                                else:
                                    thinking_row[col] = f"Effort: {effort_val}"
                            else:
                                thinking_row[col] = 'Yes' # Fallback
                        else:
                            thinking_row[col] = 'N/A'
                    else:
                        thinking_row[col] = 'N/A'

            thinking_df = pd.DataFrame([thinking_row])
            
            # Add Max Tokens row
            max_tokens_row = {'Metric': 'Max Tokens', 'Description': METRIC_DESCRIPTIONS.get('Max Tokens', '')}
            for col in dashboard_df.columns:
                if col in ['Metric', 'Description', 'Total']: continue
                max_tokens_row[col] = config['max_tokens']
            max_tokens_df = pd.DataFrame([max_tokens_row])

            # Add Temperature row
            temperature_row = {'Metric': 'Temperature', 'Description': METRIC_DESCRIPTIONS.get('Temperature', '')}
            for col in dashboard_df.columns:
                if col in ['Metric', 'Description', 'Total']: continue
                temperature_row[col] = config['temperature']
            temperature_df = pd.DataFrame([temperature_row])

            # Add Top P row
            top_p_row = {'Metric': 'Top P', 'Description': METRIC_DESCRIPTIONS.get('Top P', '')}
            for col in dashboard_df.columns:
                if col in ['Metric', 'Description', 'Total']: continue
                top_p_row[col] = config['top_p']
            top_p_df = pd.DataFrame([top_p_row])

            dashboard_df = pd.concat([thinking_df, max_tokens_df, temperature_df, top_p_df, dashboard_df], ignore_index=True)
            print("   ✅ DASHBOARD: Added 'Thinking', 'Max Tokens', 'Temperature', and 'Top P' parameter rows.")

            # Reorder columns to place Description last
            cols = dashboard_df.columns.tolist()
            if 'Description' in cols:
                cols.append(cols.pop(cols.index('Description')))
                dashboard_df = dashboard_df[cols]
                print("   ✅ DASHBOARD: Reordered columns to place 'Description' last.")

        if 'DASHBOARD' in [s.name for s in book.sheets]:
            book.sheets['DASHBOARD'].delete()
        dashboard_sheet = book.sheets.add('DASHBOARD')

        dashboard_sheet['A1'].options(pd.DataFrame, index=False).value = dashboard_df
        print(f"   ✅ DASHBOARD: Written {len(dashboard_df)} rows to sheet.")

        num_cols = len(dashboard_df.columns)
        header_range = dashboard_sheet.range('A1').resize(1, num_cols)
        header_range.color = '#4472C4'
        header_range.font.color = '#FFFFFF'
        header_range.font.bold = True

        for row_idx in range(len(dashboard_df)):
            metric_name = str(dashboard_df.iloc[row_idx]['Metric'])
            excel_row = row_idx + 2
            # Format numeric columns, skipping Metric (col A) and Description (last col)
            format_range = dashboard_sheet.range(f"B{excel_row}").resize(1, num_cols - 2)

            if '%' in metric_name:
                format_range.number_format = '0.00%'
            elif 'Tokens' in metric_name or 'Items' in metric_name or 'Calls' in metric_name:
                format_range.number_format = '#,##0'
            elif 'Cost' in metric_name:
                format_range.number_format = '#,##0.0000'

        table_range = dashboard_sheet.range('A1').resize(len(dashboard_df) + 1, num_cols)
        try:
            dashboard_sheet.tables.add(source=table_range)
            print("   ✅ DASHBOARD: Table formatting applied.")
        except Exception as table_error:
            print(f"   ⚠️  DASHBOARD: Could not create table - {table_error}")

        print("   ✅ DASHBOARD: Successfully created and formatted!")

    except Exception as e:
        print(f"   🔴 DASHBOARD: Error - {e}")
        import traceback
        traceback.print_exc()


# ==================== MAIN ASSESSMENT SCRIPT ====================

def _create_judge_json_output(all_results: Dict, original_questions_df: pd.DataFrame) -> List[Dict]:
    """
    Transforms the raw assessment results into a structured JSON format for a judge LLM.
    
    Args:
        all_results: A dictionary containing all assessment results, keyed by questionid.
        original_questions_df: The original DataFrame of questions to get original text.

    Returns:
        A list of JSON objects, one for each model's assessment of each question.
    """
    print("   Creating judge-friendly JSON payload...")
    judge_payload = []
    
    # Create a lookup for original questions by questionid for efficiency
    originals_lookup = original_questions_df.set_index('questionid').to_dict('index')

    # Iterate through each question that was assessed
    for qid, models_assessment in all_results.items():
        
        # Get original question data
        original_data = originals_lookup.get(qid)
        if not original_data:
            continue # Skip if original question not found

        # Iterate through each model's assessment for that question
        for model_key, result in models_assessment.items():
            if result.get('error'):
                continue # Skip failed assessments

            feedback = result.get('feedback', {})
            
            # Construct the answers array
            answers_list = []
            for i in range(1, 6): # Assuming max 5 answers
                answer_key = f'answer{i}'
                # Check if the answer exists in the original data and is not null/empty
                if answer_key in original_data and pd.notna(original_data[answer_key]) and original_data[answer_key] != '':
                    answer_feedback = feedback.get(answer_key, {})
                    answers_list.append({
                        "answer_id": answer_key,
                        "original_answer": _clean_text(original_data.get(answer_key, "")),
                        "rewrite": answer_feedback.get('rewrite', ""),
                        "reason": answer_feedback.get('issue', "")
                    })

            # Build the final JSON object for this assessment
            judge_item = {
                "question_id": qid,
                "assessing_model": result.get('model_name', 'unknown'),
                "original_question": _clean_text(original_data.get('question', '')),
                "question_rewrite": feedback.get('question', {}).get('rewrite', ''),
                "question_reason": feedback.get('question', {}).get('issue', ''),
                "answers": answers_list
            }
            judge_payload.append(judge_item)
            
    return judge_payload


@script
def assess_questions(book: xw.Book):
    """
    Main script to assess questions using 3 LLMs via OpenRouter in batches.
    """
    print("\n" + "="*80)
    print("🚀 QUESTION QUALITY ASSESSMENT - V2 (BATCH MODE)")
    print("="*80 + "\n")

    overall_start_time = time.time()

    try:
        # Step 1: Load configuration
        config = load_config(book)
        print("✅ Configuration loaded\n")

        # Step 2: Load T_COST table for thinking model lookup
        print("📊 Loading T_COST table for thinking model lookup...")
        cost_sheet, cost_table = find_table_in_workbook(book, "T_COST")
        thinking_models_lookup = {}
        thinking_values_lookup = {}
        if cost_table:
            cost_df = cost_table.range.options(pd.DataFrame, index=False).value
            # Ensure column names are uppercase and clean
            cost_df.columns = [str(c).upper().strip() for c in cost_df.columns]
            if 'MODEL' in cost_df.columns:
                cost_df.set_index('MODEL', inplace=True)
                if 'THINKING' in cost_df.columns:
                    thinking_models_lookup = cost_df['THINKING'].to_dict()
                    print(f"✅ Loaded thinking capabilities for {len(thinking_models_lookup)} models.")
                else:
                    print("   ⚠️  'THINKING' column not found in T_COST. Thinking parameters will not be applied.")

                if 'THINKING_VALUES' in cost_df.columns:
                    # Fill NaN with empty string before creating dict
                    thinking_values_lookup = cost_df['THINKING_VALUES'].fillna('').to_dict()
                    print(f"✅ Loaded thinking values for {len(thinking_values_lookup)} models.")
                else:
                     print("   ⚠️  'THINKING_VALUES' column not found in T_COST. Reasoning effort validation will be skipped.")
            else:
                print("   ⚠️  T_COST table is missing 'MODEL' column. Thinking parameters will not be applied.")
        else:
            print("   ⚠️  T_COST table not found. Thinking parameters will not be applied.")

        # Step 3: Load questions table
        print("📊 Loading questions from T_QUESTIONS table...")
        source_sheet, questions_table = find_table_in_workbook(book, "T_QUESTIONS")
        if not source_sheet or not questions_table:
            raise Exception("T_QUESTIONS table not found!")
        df_all = questions_table.range.options(pd.DataFrame, index=False).value
        print(f"✅ Loaded {len(df_all)} total questions")

        # Step 4: Filter by row range
        start_idx = config['start_row'] - 2
        if start_idx < 0:
            start_idx = 0

        end_idx = len(df_all)
        end_row_display = config['end_row']
        if config['end_row'] is None:
            end_row_display = len(df_all) + 1
            print("   INFO: End Row is blank, processing all rows until the end of the table.")
        else:
            end_idx = config['end_row'] - 1
            if end_idx > len(df_all):
                end_idx = len(df_all)

        df_to_process = df_all.iloc[start_idx:end_idx].copy()
        print(f"📌 Processing {len(df_to_process)} questions (rows {start_idx + 2} to {end_idx + 1})\n")

        # Step 5: Prepare results storage
        api_metrics_data = []
        results_data = []
        all_batch_results = {} # To aggregate results for the judge JSON
        
        batch_size = config['batch_size']
        total_batches = (len(df_to_process) + batch_size - 1) // batch_size

        # Step 6: Process questions in batches
        for i in range(total_batches):
            batch_start_index = i * batch_size
            batch_end_index = batch_start_index + batch_size
            batch_df = df_to_process.iloc[batch_start_index:batch_end_index]

            print(f"\n{'='*80}")
            print(f"📦 Processing Batch {i+1}/{total_batches} | Questions {batch_start_index+start_idx+2}-{min(batch_end_index+start_idx+1, end_idx+1)}")
            print(f"{'='*80}")

            # Pass batch number for detailed logging on first batch
            batch_assessment_results = assess_question_batch(batch_df, config, thinking_models_lookup, thinking_values_lookup, batch_num=(i+1))
            
            # Aggregate results for the final judge JSON
            all_batch_results.update(batch_assessment_results)

            # Process results for each question in the batch for standard output
            for _, row in batch_df.iterrows():
                question_id = row['questionid']
                assessment_for_question = batch_assessment_results.get(question_id, {})

                original_content = {'Question': _clean_text(row.get('question', ''))}
                for ans_idx in range(1, 6):
                    original_content[f'Answer {ans_idx}'] = _clean_text(row.get(f'answer{ans_idx}', ''))

                for model_key in ['model_1', 'model_2', 'model_3']:
                    if config.get(f'{model_key}_tag') != 1: continue

                    model_result = assessment_for_question.get(model_key, {})
                    full_model_name = config[model_key]
                    display_model_name = get_short_model_name(full_model_name)
                    change_required_val = model_result.get('change_required')

                    feedback = model_result.get('feedback', {})
                    results_data.append({'Model': display_model_name, 'questionid': question_id, 'Item': 'Original', 'Change Required?': change_required_val, **original_content})
                    results_data.append({
                        'Model': display_model_name, 'questionid': question_id, 'Item': 'Rewrite', 'Change Required?': change_required_val,
                        'Question': feedback.get('question', {}).get('rewrite', ''),
                        **{f'Answer {j}': feedback.get(f'answer{j}', {}).get('rewrite', '') for j in range(1, 6)}
                    })
                    results_data.append({
                        'Model': display_model_name, 'questionid': question_id, 'Item': 'Issues', 'Change Required?': change_required_val,
                        'Question': feedback.get('question', {}).get('issue', model_result.get('error', '')),
                        **{f'Answer {j}': feedback.get(f'answer{j}', {}).get('issue', '') for j in range(1, 6)}
                    })
                    results_data.append({}) # Separator row
            
            # Log API metrics ONCE per batch, per model
            for model_key in ['model_1', 'model_2', 'model_3']:
                if config.get(f'{model_key}_tag') != 1: continue
                
                first_qid_in_batch = batch_df['questionid'].iloc[0]
                model_result_for_first_q = batch_assessment_results.get(first_qid_in_batch, {}).get(model_key)

                if model_result_for_first_q:
                    api_metrics_data.append({
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Question_ID': f"Batch_{i+1}",
                        'Model_Name': model_result_for_first_q.get('model_name'), 'Model_Key': model_key,
                        'Status': 'SUCCESS' if model_result_for_first_q.get('error') is None else 'ERROR',
                        'Input_Tokens': model_result_for_first_q.get('tokens', {}).get('input', 0),
                        'Output_Tokens': model_result_for_first_q.get('tokens', {}).get('output', 0),
                        'Reasoning_Tokens': model_result_for_first_q.get('tokens', {}).get('reasoning', 0),
                        'Total_Tokens': model_result_for_first_q.get('tokens', {}).get('total', 0),
                        'Latency_Seconds': round(model_result_for_first_q.get('latency', 0), 2),
                        'Raw_Response': model_result_for_first_q.get('raw_response', '') or '',
                        'Error_Message': model_result_for_first_q.get('error', '') or ''
                    })
            
            if config['request_delay_seconds'] > 0 and (i+1) < total_batches:
                print(f"\n...Pausing for {config['request_delay_seconds']} seconds before next batch...")
                time.sleep(config['request_delay_seconds'])

        # Step 7: Write standard results and dashboard
        print(f"\n{'='*80}")
        print("💾 Writing results to ASSESSMENT_RESULTS sheet...")
        if 'ASSESSMENT_RESULTS' in [s.name for s in book.sheets]:
            book.sheets['ASSESSMENT_RESULTS'].clear()
        results_sheet = book.sheets['ASSESSMENT_RESULTS'] if 'ASSESSMENT_RESULTS' in [s.name for s in book.sheets] else book.sheets.add('ASSESSMENT_RESULTS')
        results_df = pd.DataFrame(results_data)
        if results_df.empty:
            print("   ⚠️  No results were generated. Skipping write to ASSESSMENT_RESULTS sheet.")
        else:
            results_sheet['A1'].options(pd.DataFrame, index=False).value = results_df
            print(f"✅ Results written: {len(results_df)} rows")

        print("📈 Writing API metrics...")
        if 'API_METRICS' in [s.name for s in book.sheets]:
            book.sheets['API_METRICS'].clear()
        metrics_sheet = book.sheets['API_METRICS'] if 'API_METRICS' in [s.name for s in book.sheets] else book.sheets.add('API_METRICS')
        metrics_df = pd.DataFrame(api_metrics_data)
        if metrics_df.empty:
            print("   ⚠️  No API metrics were generated. Skipping write to API_METRICS sheet.")
        else:
            metrics_sheet['A1'].options(pd.DataFrame, index=False).value = metrics_df
            print(f"✅ API metrics written: {len(metrics_df)} records")

        # Step 8: Generate and write the new Judge JSON output
        print("\n⚖️ Generating JSON output for Judge LLM...")
        try:
            judge_json_data = _create_judge_json_output(all_batch_results, df_to_process)
            
            if judge_json_data:
                sheet_name = "LLM_JUDGE_INPUT"
                if sheet_name in [s.name for s in book.sheets]:
                    judge_sheet = book.sheets[sheet_name]
                    judge_sheet.clear()
                else:
                    judge_sheet = book.sheets.add(sheet_name)
                
                json_string = json.dumps(judge_json_data, indent=2)
                judge_sheet['A1'].value = json_string
                
                print(f"✅ Successfully generated {len(judge_json_data)} records for the judge.")
                print(f"📄 Output written to '{sheet_name}' sheet, cell A1.")
            else:
                print("   ⚠️  No valid assessment data to generate Judge JSON.")

        except Exception as e:
            print(f"❌ Error generating Judge JSON output: {e}")
            import traceback
            traceback.print_exc()

        print("\n🎨 Building dashboard...")
        build_and_write_dashboard(book, config, api_metrics_data, results_data, config['system_prompt'])

        total_time_secs = time.time() - overall_start_time
        print(f"\n{'='*80}\n✅ ASSESSMENT COMPLETE! Total Time: {int(total_time_secs // 60)}m {int(total_time_secs % 60)}s\n{'='*80}")
    except Exception as e:
        print(f"\n❌ FATAL ERROR in assess_questions: {e}")
        import traceback
        traceback.print_exc()


# ==================== REFRESH DASHBOARD (Simplified helper) ====================

@script
def refresh_dashboard(book: xw.Book):
    """
    Manually refresh dashboard - reads from API_METRICS sheet
    
    Note: This reads from the sheet, so it's called manually AFTER assessment runs
    """
    print("\n🎨 Manually refreshing dashboard...\n")
    
    try:
        config = load_config(book)
        
        if 'API_METRICS' not in [s.name for s in book.sheets]:
            print("❌ API_METRICS sheet not found - cannot refresh dashboard")
            return
        
        metrics_sheet = book.sheets['API_METRICS']
        
        # Read the metrics sheet with explicit range
        try:
            # Get all data from API_METRICS - read all rows, columns A-K
            metrics_range = metrics_sheet['A1'].expand('right').expand('down')
            all_data = metrics_range.value
            
            # Convert to list of dicts, skipping header row
            if all_data and len(all_data) > 1:
                headers = all_data[0]
                metrics_data = []
                for row in all_data[1:]:
                    row_dict = {headers[i]: row[i] for i in range(len(headers))}
                    metrics_data.append(row_dict)
                
                print(f"✅ Read {len(metrics_data)} metrics records from sheet")
                
                # Try to read results too
                results_data = []
                if 'ASSESSMENT_RESULTS' in [s.name for s in book.sheets]:
                    results_sheet = book.sheets['ASSESSMENT_RESULTS']
                    results_range = results_sheet['A1'].expand('right').expand('down')
                    results_all = results_range.value
                    if results_all and len(results_all) > 1:
                        headers = results_all[0]
                        for row in results_all[1:]:
                            row_dict = {headers[i]: row[i] for i in range(len(headers))}
                            results_data.append(row_dict)
                        print(f"✅ Read {len(results_data)} results records from sheet")
                
                # Build dashboard with the data
                build_and_write_dashboard(book, config, metrics_data, results_data, config['system_prompt'])
            else:
                print("❌ No data in API_METRICS sheet")
        except Exception as e:
            print(f"❌ Error reading metrics: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error during refresh: {e}")


# ==================== TEST SCRIPT ====================


@script
def clear_all_results(book: xw.Book):
    """Clear all result sheets"""
    print("\n🧹 Clearing results...")
    try:
        for sheet_name in ['ASSESSMENT_RESULTS', 'API_METRICS', 'DASHBOARD']:
            if sheet_name in [s.name for s in book.sheets]:
                book.sheets[sheet_name].delete()
                print(f"   ✅ Deleted {sheet_name}")
        print("\n✅ All cleared")
    except Exception as e:
        print(f"❌ Error: {e}")


@script
def get_manual_test_payload(book: xw.Book):
    """
    Generate JSON payload for manual testing in AI Studio or Gemini Playground.

    Outputs ONLY the FIRST BATCH (5 questions) to MANUAL_TEST_JSON sheet cell A1.
    This ensures exact consistency between manual testing and automation.

    Usage:
    1. Set START_ROW and END_ROW in MASTER sheet
    2. Run this function
    3. Copy JSON from MANUAL_TEST_JSON sheet A1
    4. Paste into AI Studio prompt box (system instructions already configured separately)
    5. Test with different temperature/thinking settings
    6. Once satisfied, update MASTER sheet and run assess_questions() for automation
    """
    print("\n" + "="*80)
    print("🧪 GENERATING MANUAL TEST PAYLOAD")
    print("="*80)

    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config(book)

        # Load questions from T_QUESTIONS table
        print("📊 Loading questions from T_QUESTIONS table...")
        questions_sheet, questions_table = find_table_in_workbook(book, "T_QUESTIONS")
        if not questions_table:
            raise ValueError("T_QUESTIONS table not found!")

        questions_df = questions_table.range.options(pd.DataFrame, index=False).value

        # Calculate first batch range
        start_row = config['start_row']
        end_row = config['end_row'] if config['end_row'] else len(questions_df) + 1
        batch_size = config['batch_size']

        # Get first batch only
        batch_end_row = min(start_row + batch_size - 1, end_row)
        first_batch_df = questions_df.iloc[start_row - 2:batch_end_row - 1]

        print(f"   Processing questions {start_row} to {batch_end_row}")
        print(f"   Batch size: {len(first_batch_df)} questions")

        # Calculate total batches to warn user if needed
        total_questions = end_row - start_row + 1
        total_batches = (total_questions + batch_size - 1) // batch_size

        if total_batches > 1:
            print(f"\n   ⚠️  WARNING: Your range has {total_questions} questions ({total_batches} batches)")
            print(f"   ⚠️  Outputting ONLY FIRST BATCH (questions {start_row}-{batch_end_row}) for manual testing")
            print(f"   ⚠️  Adjust END_ROW in MASTER to {batch_end_row} if you only want this batch\n")

        # Generate JSON payload (same function used in automation)
        json_payload = prepare_question_batch_payload(first_batch_df)

        # Create or clear MANUAL_TEST_JSON sheet
        if 'MANUAL_TEST_JSON' in [s.name for s in book.sheets]:
            test_sheet = book.sheets['MANUAL_TEST_JSON']
            test_sheet.clear()
        else:
            test_sheet = book.sheets.add('MANUAL_TEST_JSON')

        # Write JSON to A1
        test_sheet['A1'].value = json_payload

        # Note: column_width and row_height are not supported in xlwings Lite
        # Users can manually adjust column width if needed

        print(f"\n✅ JSON payload generated successfully!")
        print(f"📄 Output location: MANUAL_TEST_JSON sheet, cell A1")
        print(f"📋 Questions included: {len(first_batch_df)}")
        print(f"\n📖 NEXT STEPS:")
        print(f"   1. Go to MANUAL_TEST_JSON sheet")
        print(f"   2. Select cell A1 and copy all content (Ctrl+C)")
        print(f"   3. Open AI Studio / Gemini Playground")
        print(f"   4. Paste system instructions (already configured separately)")
        print(f"   5. Paste this JSON payload into the prompt box")
        print(f"   6. Test with different temperature/thinking settings")
        print(f"   7. Once satisfied, update MASTER sheet settings")
        print(f"   8. Run assess_questions() for automated processing")

        print("\n" + "="*80)
        print("✅ PAYLOAD GENERATION COMPLETE")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR generating manual test payload: {e}")
        import traceback
        traceback.print_exc()


print("\n✅ Question Quality Assessment System v3.0 loaded!")
print("📋 Available scripts:")
print("   - assess_questions (MAIN: Run full assessment)")
print("   - get_manual_test_payload (NEW: Generate JSON for AI Studio testing)")
print("   - refresh_dashboard (Manually refresh dashboard)")
print("   - clear_all_results (Clear all output sheets)")
print("\n🔧 v3.0 Changes:")
print("   - 🧠 Thinking/Reasoning support for Gemini 2.5 & GPT-5 models")
print("   - 🧪 NEW: get_manual_test_payload() - Generate JSON for AI Studio testing")
print("   - 📄 System prompt now loads from TXT file (upload via VBA)")
print("   - 🔐 API key prioritizes ENVIRONMENT VARIABLES")
print("   - ⏱️  Time metrics & 💰 Cost projections (1K & 100K)")
print("\nSelect from dropdown and press F5.\n")
