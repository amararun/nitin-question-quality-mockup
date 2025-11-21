"""
Question Quality Assessment System - xlwings Lite
Assesses educational questions against quality guidelines using 3 LLMs via OpenRouter

Author: AI Coding Assistant
Version: 1.0
Date: 2025
"""

import xlwings as xw
from xlwings import script
import pandas as pd
import json
from datetime import datetime
from typing import Tuple, Optional, Dict, List
import time
import re

# ==================== CONFIGURATION LOADER ====================

def load_config(book: xw.Book) -> Dict:
    """Load configuration from MASTER sheet starting at B3"""
    print("📋 Loading configuration from MASTER sheet...")

    try:
        master_sheet = book.sheets["MASTER"]

        # Read configuration starting from B3
        config = {
            "api_key": str(master_sheet["B3"].value or ""),
            "model_1": str(master_sheet["B4"].value or "anthropic/claude-3-5-sonnet-20241022"),
            "model_2": str(master_sheet["B5"].value or "openai/gpt-4o"),
            "model_3": str(master_sheet["B6"].value or "google/gemini-pro-1.5"),
            "temperature": float(master_sheet["B7"].value or 0.3),
            "top_p": float(master_sheet["B8"].value or 0.9),
            "max_tokens": int(master_sheet["B9"].value or 2000),
            "batch_size": int(master_sheet["B10"].value or 10),
            "start_row": int(master_sheet["B11"].value or 2),
            "end_row": int(master_sheet["B12"].value or 5),
            "strip_html": str(master_sheet["B13"].value or "TRUE").upper() == "TRUE",
            "http_referer": str(master_sheet["B14"].value or "https://github.com"),
            "x_title": str(master_sheet["B15"].value or "Question Quality Assessor")
        }

        # Safety check: Ensure start_row is at least 2 (skip header)
        if config["start_row"] < 2:
            print(f"⚠️  START_ROW was {config['start_row']}, adjusting to 2 (header row)")
            config["start_row"] = 2

        print(f"✅ Configuration loaded:")
        print(f"   Models: {config['model_1']}, {config['model_2']}, {config['model_3']}")
        print(f"   Processing rows: {config['start_row']} to {config['end_row']}")
        print(f"   Temperature: {config['temperature']}, Top-P: {config['top_p']}, Max Tokens: {config['max_tokens']}")
        print(f"   Strip HTML: {config['strip_html']}, Batch Size: {config['batch_size']}")

        if not config["api_key"] or config["api_key"] == "":
            print("⚠️  WARNING: OPENROUTER_API_KEY is empty! API calls will fail.")

        return config

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        raise


def load_system_instructions(book: xw.Book) -> str:
    """Load and concatenate system instructions from SYSTEM_INSTRUCTIONS sheet"""
    print("📜 Loading system instructions...")

    try:
        inst_sheet = book.sheets["SYSTEM_INSTRUCTIONS"]

        # Read all text from column A until empty cell
        instructions = []
        row = 1
        while True:
            cell_value = inst_sheet[f"A{row}"].value
            if cell_value is None or str(cell_value).strip() == "":
                break
            instructions.append(str(cell_value))
            row += 1

        full_instructions = "\n".join(instructions)
        print(f"✅ Loaded {len(instructions)} instruction lines ({len(full_instructions)} chars)")

        return full_instructions

    except Exception as e:
        print(f"❌ Error loading system instructions: {e}")
        raise


# ==================== TABLE HELPER ====================

def find_table_in_workbook(book: xw.Book, table_name: str) -> Tuple[Optional[xw.Sheet], Optional[xw.Table]]:
    """
    MANDATORY HELPER: xlwings Lite Table objects have no .sheet attribute
    Returns: (sheet, table) or (None, None) if not found
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
    timeout: int = 30
) -> Tuple[Optional[Dict], Optional[str], float]:
    """
    Call OpenRouter API with specified model

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

    print(f"   🌐 Calling OpenRouter API: {model_name}")
    print(f"      Request payload: temperature={config['temperature']}, top_p={config['top_p']}, max_tokens={config['max_tokens']}")

    start_time = time.time()

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        latency = time.time() - start_time

        print(f"      Status: {response.status_code} | Latency: {latency:.2f}s")

        if response.status_code == 200:
            response_json = response.json()
            print(f"      ✅ SUCCESS!")
            print(f"      📄 Raw Response:")
            print(f"      {json.dumps(response_json, indent=2)}")
            return response_json, None, latency
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"      ❌ Error: {error_msg}")
            return None, error_msg, latency

    except requests.exceptions.Timeout:
        latency = time.time() - start_time
        error_msg = f"Timeout after {timeout}s"
        print(f"      ⏱️  {error_msg}")
        return None, error_msg, latency

    except Exception as e:
        latency = time.time() - start_time
        error_msg = str(e)
        print(f"      ❌ Exception: {error_msg}")
        return None, error_msg, latency


def parse_llm_response(response: Dict) -> Optional[Dict]:
    """
    Parse OpenRouter response and extract the LLM's JSON output

    Expected format:
    {
        "change_required": 0 or 1,
        "issues": "compact issues text with \n",
        "rewrite": "suggested rewrite"
    }
    """
    try:
        # OpenRouter response structure: choices[0].message.content
        content = response["choices"][0]["message"]["content"]

        print(f"      📝 LLM Content (raw): {content[:200]}...")

        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        parsed = json.loads(content)

        # Validate structure
        if not all(k in parsed for k in ["change_required", "issues", "rewrite"]):
            print(f"      ⚠️  Missing required keys in response. Keys found: {list(parsed.keys())}")
            return None

        # Ensure change_required is 0 or 1
        if parsed["change_required"] not in [0, 1]:
            print(f"      ⚠️  Invalid change_required value: {parsed['change_required']}")
            return None

        print(f"      ✅ Parsed successfully: change={parsed['change_required']}, issues_len={len(parsed['issues'])}")

        return parsed

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"      ⚠️  Parse error: {e}")
        return None


# ==================== QUESTION PROCESSING ====================

def prepare_question_payload(row_data: pd.Series, config: Dict) -> str:
    """
    Prepare question content for LLM assessment

    Args:
        row_data: DataFrame row containing question data
        config: Configuration dict

    Returns:
        Formatted question text
    """

    def clean_text(text):
        if pd.isna(text):
            return ""
        text = str(text)
        if config['strip_html']:
            # Simple HTML tag removal
            text = re.sub(r'<[^>]+>', '', text)
            # Decode common HTML entities
            text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&quot;', '"').replace('&amp;', '&')
        return text.strip()

    question_text = clean_text(row_data.get('question', ''))

    # Build answer options
    answers = []
    for i in range(1, 6):
        answer_col = f'answer{i}'
        if answer_col in row_data and not pd.isna(row_data[answer_col]):
            answer_text = clean_text(row_data[answer_col])
            if answer_text:
                # Use letters a, b, c, d, e
                answers.append(f"{chr(96+i)}) {answer_text}")

    hint_text = clean_text(row_data.get('hint', ''))
    correct_answer = clean_text(row_data.get('correctanswer', ''))
    topic = clean_text(row_data.get('topic', 'N/A'))
    difficulty = clean_text(row_data.get('difficultylevel', 'Not specified'))
    question_type = clean_text(row_data.get('question_type', ''))

    # Check for images
    has_images = False
    image_cols = ['questionImage', 'answer1Image', 'answer2Image', 'answer3Image',
                  'answer4Image', 'answer5Image', 'hintImage']
    for col in image_cols:
        if col in row_data and not pd.isna(row_data[col]) and str(row_data[col]).strip():
            has_images = True
            break

    # Format payload
    payload = f"""QUESTION ID: {row_data.get('questionid', 'N/A')}

QUESTION TEXT:
{question_text}

ANSWER OPTIONS:
{chr(10).join(answers)}

CORRECT ANSWER: {correct_answer}

HINT/EXPLANATION:
{hint_text}
"""

    if question_type:
        payload += f"\nQUESTION TYPE: {question_type}"

    payload += f"\nTOPIC: {topic}"
    payload += f"\nDIFFICULTY: {difficulty}"

    if has_images:
        payload += "\n\n[NOTE: This question contains images which cannot be assessed]"

    return payload


def assess_single_question(
    row_data: pd.Series,
    config: Dict,
    system_instructions: str
) -> Dict:
    """
    Assess a single question with all 3 models

    Returns:
        {
            'model_1': {'change': 0/1, 'issues': '...', 'rewrite': '...', 'tokens': {...}, 'latency': 1.5, 'error': None},
            'model_2': {...},
            'model_3': {...}
        }
    """
    question_payload = prepare_question_payload(row_data, config)

    print(f"\n   📄 Question Payload Preview (first 300 chars):")
    print(f"   {question_payload[:300]}...")

    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": question_payload}
    ]

    results = {}

    for i, model_key in enumerate(['model_1', 'model_2', 'model_3'], 1):
        model_name = config[model_key]
        print(f"\n   📊 Model {i}/3: {model_name}")
        print(f"   {'='*70}")

        response, error, latency = call_openrouter_api(model_name, messages, config)

        if error:
            results[model_key] = {
                'change': None,
                'issues': f"API Error: {error}",
                'rewrite': "",
                'tokens': {'input': 0, 'output': 0, 'total': 0},
                'latency': latency,
                'error': error,
                'raw_response': None
            }
            continue

        # Extract tokens
        usage = response.get('usage', {})
        tokens = {
            'input': usage.get('prompt_tokens', 0),
            'output': usage.get('completion_tokens', 0),
            'total': usage.get('total_tokens', 0)
        }

        print(f"      📊 Tokens: Input={tokens['input']}, Output={tokens['output']}, Total={tokens['total']}")

        # Parse LLM's JSON response
        parsed = parse_llm_response(response)

        if parsed:
            results[model_key] = {
                'change': parsed.get('change_required', 0),
                'issues': parsed.get('issues', ''),
                'rewrite': parsed.get('rewrite', ''),
                'tokens': tokens,
                'latency': latency,
                'error': None,
                'raw_response': json.dumps(response)
            }
            print(f"      ✅ Assessment Complete:")
            print(f"         - Change Required: {parsed.get('change_required')}")
            print(f"         - Issues: {parsed.get('issues', '')[:80]}...")
            print(f"         - Rewrite: {parsed.get('rewrite', '')[:80]}...")
        else:
            results[model_key] = {
                'change': None,
                'issues': "Failed to parse LLM response",
                'rewrite': "",
                'tokens': tokens,
                'latency': latency,
                'error': "Parse error",
                'raw_response': json.dumps(response)
            }
            print(f"      ⚠️  Failed to parse response - storing raw data")

    return results


# ==================== MAIN ASSESSMENT SCRIPT ====================

@script
def assess_questions(book: xw.Book):
    """
    Main script to assess questions using 3 LLMs via OpenRouter
    """
    print("\n" + "="*80)
    print("🚀 QUESTION QUALITY ASSESSMENT - STARTING")
    print("="*80 + "\n")

    overall_start_time = time.time()
    model_times = {'model_1': 0.0, 'model_2': 0.0, 'model_3': 0.0}

    try:
        # Step 1: Load configuration
        config = load_config(book)
        system_instructions = load_system_instructions(book)

        # Step 2: Find and load questions table
        print("\n📊 Loading questions from T_QUESTIONS table...")
        source_sheet, questions_table = find_table_in_workbook(book, "T_QUESTIONS")

        if not source_sheet or not questions_table:
            print("❌ ERROR: T_QUESTIONS table not found!")
            print("   Please ensure the table exists and is named 'T_QUESTIONS'")
            return

        # Load questions into DataFrame
        df_all = questions_table.range.options(pd.DataFrame, index=False).value
        print(f"✅ Loaded {len(df_all)} total questions from table")
        print(f"   Columns: {list(df_all.columns)[:10]}...")

        # Step 3: Filter by row range (adjust for 0-based index)
        # User specifies START_ROW=2 (first data row), END_ROW=5 (last row to process)
        # In DataFrame, row 2 is index 0, row 5 is index 3
        start_idx = config['start_row'] - 2  # Row 2 = index 0
        end_idx = config['end_row'] - 1      # Row 5 = index 3 (inclusive)

        if start_idx < 0:
            start_idx = 0
        if end_idx >= len(df_all):
            end_idx = len(df_all) - 1

        df_to_process = df_all.iloc[start_idx:end_idx+1].copy()
        print(f"📌 Processing rows {config['start_row']} to {config['end_row']} ({len(df_to_process)} questions)")
        print(f"   DataFrame indices: {start_idx} to {end_idx}")

        # Step 4: Prepare results storage
        api_metrics_data = []
        results_data = []

        # Step 5: Process each question
        for idx, (df_idx, row) in enumerate(df_to_process.iterrows(), 1):
            question_id = row.get('questionid', 'N/A')
            print(f"\n{'='*80}")
            print(f"📝 Question {idx}/{len(df_to_process)} | ID: {question_id} | Row: {config['start_row'] + idx - 1}")
            print(f"{'='*80}")

            # Assess with all 3 models
            assessment_results = assess_single_question(row, config, system_instructions)

            # Build results row
            result_row = row.to_dict()

            for model_key in ['model_1', 'model_2', 'model_3']:
                model_result = assessment_results[model_key]
                prefix = model_key.upper()

                result_row[f'{prefix}_CHANGE'] = model_result['change']
                result_row[f'{prefix}_ISSUES'] = model_result['issues']
                result_row[f'{prefix}_REWRITE'] = model_result['rewrite']

                # Accumulate model times
                model_times[model_key] += model_result['latency']

                # Log API metrics
                api_metrics_data.append({
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Question_ID': question_id,
                    'Model_Name': config[model_key],
                    'Model_Key': model_key,
                    'Status': 'SUCCESS' if model_result['error'] is None else 'ERROR',
                    'Input_Tokens': model_result['tokens']['input'],
                    'Output_Tokens': model_result['tokens']['output'],
                    'Total_Tokens': model_result['tokens']['total'],
                    'Latency_Seconds': round(model_result['latency'], 2),
                    'Raw_Response': model_result['raw_response'] or '',
                    'Error_Message': model_result['error'] or ''
                })

            results_data.append(result_row)

            # Batch delay (if configured)
            if idx % config['batch_size'] == 0 and idx < len(df_to_process):
                print(f"\n⏸️  Batch complete ({idx} questions). Pausing 5 seconds...")
                time.sleep(5)

        # Step 6: Write results to ASSESSMENT_RESULTS sheet
        print(f"\n{'='*80}")
        print("💾 Writing results to ASSESSMENT_RESULTS sheet...")

        results_df = pd.DataFrame(results_data)

        # Create or clear ASSESSMENT_RESULTS sheet
        if 'ASSESSMENT_RESULTS' in [s.name for s in book.sheets]:
            results_sheet = book.sheets['ASSESSMENT_RESULTS']
            results_sheet.clear()
        else:
            results_sheet = book.sheets.add('ASSESSMENT_RESULTS')

        # Write results with index=False
        results_sheet['A1'].options(index=False).value = results_df
        print(f"✅ Wrote {len(results_df)} rows × {len(results_df.columns)} columns to ASSESSMENT_RESULTS")

        # Format headers
        try:
            header_range = results_sheet['A1'].resize(1, len(results_df.columns))
            header_range.color = '#4472C4'
            header_range.font.color = '#FFFFFF'
            header_range.font.bold = True
            print("✅ Applied header formatting")
        except Exception as e:
            print(f"⚠️  Could not apply header formatting: {e}")

        # Step 7: Write API metrics
        print("\n📈 Writing API metrics to API_METRICS sheet...")

        metrics_df = pd.DataFrame(api_metrics_data)

        if 'API_METRICS' in [s.name for s in book.sheets]:
            metrics_sheet = book.sheets['API_METRICS']
            metrics_sheet.clear()
        else:
            metrics_sheet = book.sheets.add('API_METRICS')

        metrics_sheet['A1'].options(index=False).value = metrics_df
        print(f"✅ Wrote {len(metrics_df)} API call records")

        # Format headers
        try:
            header_range = metrics_sheet['A1'].resize(1, len(metrics_df.columns))
            header_range.color = '#4472C4'
            header_range.font.color = '#FFFFFF'
            header_range.font.bold = True
        except:
            pass

        # Step 8: Calculate and display summary
        total_time = time.time() - overall_start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        print(f"\n{'='*80}")
        print(f"✅ ASSESSMENT COMPLETE!")
        print(f"{'='*80}")
        print(f"⏱️  Total Time: {time_formatted} ({total_time:.1f} seconds)")
        print(f"📊 Questions Processed: {len(df_to_process)}")
        print(f"🎯 API Calls Made: {len(api_metrics_data)}")
        print(f"💰 Total Tokens Used: {metrics_df['Total_Tokens'].sum():,}")

        print(f"\n⏱️  Time Breakdown by Model:")
        for model_key in ['model_1', 'model_2', 'model_3']:
            model_time = model_times[model_key]
            hours = int(model_time // 3600)
            minutes = int((model_time % 3600) // 60)
            seconds = int(model_time % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"   {config[model_key]}: {time_str} ({model_time:.1f}s)")

        avg_time_per_question = total_time / len(df_to_process) if len(df_to_process) > 0 else 0
        print(f"\n📊 Average Time per Question: {avg_time_per_question:.2f} seconds")

        # Step 9: Trigger dashboard refresh
        print(f"\n🎨 Refreshing dashboard...")
        refresh_dashboard(book)

        print(f"\n{'='*80}")
        print("🎉 ALL DONE! Check the ASSESSMENT_RESULTS and DASHBOARD sheets.")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


# ==================== DASHBOARD UPDATER ====================

@script
def refresh_dashboard(book: xw.Book):
    """
    Calculate and update DASHBOARD sheet with summary statistics
    """
    print("\n🎨 Refreshing dashboard...")

    try:
        # Load API metrics
        metrics_sheet = book.sheets['API_METRICS']
        metrics_df = metrics_sheet['A1'].options(pd.DataFrame, index=False).value

        if metrics_df is None or len(metrics_df) == 0:
            print("⚠️  No metrics data found. Cannot refresh dashboard.")
            return

        # Load config to get model names
        config = load_config(book)

        # Calculate statistics per model
        dashboard_data = []

        for model_key in ['model_1', 'model_2', 'model_3']:
            model_name = config[model_key]
            model_metrics = metrics_df[metrics_df['Model_Key'] == model_key]

            total_calls = len(model_metrics)
            successful_calls = len(model_metrics[model_metrics['Status'] == 'SUCCESS'])
            failed_calls = total_calls - successful_calls
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

            # Load assessment results to count change recommendations
            if 'ASSESSMENT_RESULTS' in [s.name for s in book.sheets]:
                results_sheet = book.sheets['ASSESSMENT_RESULTS']
                results_df = results_sheet['A1'].options(pd.DataFrame, index=False).value

                change_col = f'{model_key.upper()}_CHANGE'
                if change_col in results_df.columns:
                    # Count where change = 1
                    changes_recommended = (results_df[change_col] == 1).sum()
                    change_rate = (changes_recommended / successful_calls * 100) if successful_calls > 0 else 0
                else:
                    changes_recommended = 0
                    change_rate = 0
            else:
                changes_recommended = 0
                change_rate = 0

            # Token statistics
            total_input = int(model_metrics['Input_Tokens'].sum())
            total_output = int(model_metrics['Output_Tokens'].sum())
            total_tokens = int(model_metrics['Total_Tokens'].sum())

            # Time statistics
            total_seconds = model_metrics['Latency_Seconds'].sum()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            avg_time_per_question = total_seconds / successful_calls if successful_calls > 0 else 0

            # Cost estimation (rough approximation)
            # You'll need to update these with actual pricing from OpenRouter
            if 'claude' in model_name.lower():
                cost_per_1k_input = 0.003
                cost_per_1k_output = 0.015
            elif 'gpt-4o' in model_name.lower():
                cost_per_1k_input = 0.0025
                cost_per_1k_output = 0.010
            elif 'gemini' in model_name.lower():
                cost_per_1k_input = 0.00125
                cost_per_1k_output = 0.005
            else:
                cost_per_1k_input = 0.003
                cost_per_1k_output = 0.010

            estimated_cost = (total_input / 1000 * cost_per_1k_input) + (total_output / 1000 * cost_per_1k_output)

            dashboard_data.append({
                'Model': model_name,
                'Total_Calls': total_calls,
                'Successful': successful_calls,
                'Failed': failed_calls,
                'Success_Rate_%': round(success_rate, 1),
                'Questions_Processed': successful_calls,
                'Changes_Recommended': int(changes_recommended),
                'Change_Rate_%': round(change_rate, 1),
                'Input_Tokens': total_input,
                'Output_Tokens': total_output,
                'Total_Tokens': total_tokens,
                'Total_Time_HH_MM_SS': time_formatted,
                'Avg_Seconds_Per_Question': round(avg_time_per_question, 2),
                'Estimated_Cost_USD': round(estimated_cost, 4)
            })

        # Create dashboard DataFrame
        dashboard_df = pd.DataFrame(dashboard_data)

        # Write to DASHBOARD sheet
        if 'DASHBOARD' in [s.name for s in book.sheets]:
            dashboard_sheet = book.sheets['DASHBOARD']
            dashboard_sheet.clear()
        else:
            dashboard_sheet = book.sheets.add('DASHBOARD')

        dashboard_sheet['A1'].options(index=False).value = dashboard_df

        # Apply formatting
        try:
            header_range = dashboard_sheet['A1'].resize(1, len(dashboard_df.columns))
            header_range.color = '#4472C4'
            header_range.font.color = '#FFFFFF'
            header_range.font.bold = True
            print("✅ Dashboard updated successfully with formatting")
        except Exception as e:
            print(f"✅ Dashboard updated (formatting skipped: {e})")

    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        import traceback
        traceback.print_exc()


# ==================== TEST SCRIPT ====================

@script
def test_single_question(book: xw.Book):
    """
    Debug tool: Test assessment on a single question (first in range)
    """
    print("\n" + "="*80)
    print("🧪 TEST MODE: Processing first question only")
    print("="*80 + "\n")

    try:
        config = load_config(book)
        system_instructions = load_system_instructions(book)

        # Load first question
        source_sheet, questions_table = find_table_in_workbook(book, "T_QUESTIONS")

        if not source_sheet or not questions_table:
            print("❌ ERROR: T_QUESTIONS table not found!")
            return

        df = questions_table.range.options(pd.DataFrame, index=False).value

        start_idx = config['start_row'] - 2
        if start_idx < 0:
            start_idx = 0

        if start_idx >= len(df):
            print(f"❌ ERROR: START_ROW ({config['start_row']}) is beyond available data ({len(df)} rows)")
            return

        test_row = df.iloc[start_idx]

        print(f"Testing Question ID: {test_row.get('questionid')}")
        print(f"Question: {str(test_row.get('question', ''))[:100]}...\n")

        # Assess
        results = assess_single_question(test_row, config, system_instructions)

        # Print results
        print("\n" + "="*80)
        print("📊 TEST RESULTS:")
        print("="*80)

        for model_key, result in results.items():
            print(f"\n🔹 {config[model_key]}:")
            print(f"   Change Required: {result['change']}")
            print(f"   Issues:\n      {result['issues']}")
            print(f"   Rewrite: {result['rewrite'][:150]}...")
            print(f"   Tokens: Input={result['tokens']['input']}, Output={result['tokens']['output']}, Total={result['tokens']['total']}")
            print(f"   Latency: {result['latency']:.2f}s")
            if result['error']:
                print(f"   ❌ Error: {result['error']}")

        print("\n" + "="*80)
        print("🧪 TEST COMPLETE")
        print("="*80 + "\n")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# ==================== UTILITY SCRIPTS ====================

@script
def clear_all_results(book: xw.Book):
    """
    Utility: Clear all assessment results and metrics (fresh start)
    """
    print("\n🧹 Clearing all results...")

    try:
        sheets_to_clear = ['ASSESSMENT_RESULTS', 'API_METRICS', 'DASHBOARD']

        for sheet_name in sheets_to_clear:
            if sheet_name in [s.name for s in book.sheets]:
                book.sheets[sheet_name].delete()
                print(f"   ✅ Deleted {sheet_name}")

        print("\n✅ All results cleared. Ready for fresh run.")

    except Exception as e:
        print(f"❌ Error clearing results: {e}")


# ==================== END OF MAIN.PY ====================

print("\n✅ Question Quality Assessment System loaded successfully!")
print("📋 Available scripts:")
print("   - assess_questions: Main assessment script")
print("   - test_single_question: Test with first question only")
print("   - refresh_dashboard: Recalculate dashboard metrics")
print("   - clear_all_results: Delete all results and start fresh")
print("\nSelect a script from the dropdown and press F5 to run.\n")
