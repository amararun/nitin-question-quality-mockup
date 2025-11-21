# React Mockup - Sample Data Guide

This directory contains the implementation plan and sample data for the Question Quality Assessment React mockup.

## ✅ READY TO USE - Dummy Data Included!

**Good news:** Full dummy sample files are already created! AI coder can start building immediately.

## 📁 Directory Structure

```
PLAN_MOCKUP/
├── MOCKUP_IMPLEMENTATION_PLAN.md    # Complete implementation guide
├── README.md                         # This file
└── sample_files/                     # Sample data files
    ├── dummy_questions_sample.json       # ✅ 40 questions (READY)
    ├── dummy_dashboard_metrics.json      # ✅ Dashboard data (READY)
    ├── dummy_api_logs.json               # ✅ 8 API logs (READY)
    ├── dummy_validation_report.json      # ✅ Validation report (READY)
    ├── TEMPLATE_*.json                   # Templates (for reference)
```

## 🚀 For AI Coder: START NOW

**You have everything needed to build the complete mockup:**

1. Read `MOCKUP_IMPLEMENTATION_PLAN.md` - Complete implementation guide
2. Use `dummy_*.json` files - All sample data ready
3. Follow phases 1-5 sequentially
4. Each phase is independently testable

**No blockers. Start Phase 1 immediately!**

---

## 📊 Dummy Data Summary

### dummy_questions_sample.json (40 questions)
- **Variety included:**
  - Different worksheet_ids (S07, S08, S09, S10)
  - Some with AI processing, some without
  - Different review statuses: pending, approved, rejected
  - Different classifications: all_ok, mistake, hallucinated
  - Some with corrections, some with "No changes needed"
  - Mix of topics (Atoms, Motion, Light, Photosynthesis, etc.)
  - One question with image field populated

- **Distribution:**
  - ai_processed: true (38 questions), false (2 questions)
  - human_reviewed: true (22 questions), false (18 questions)
  - review_status: approved (22), pending (16), rejected (2)
  - review_classification: all_ok (20), hallucinated (1), mistake (1), null (18)

### dummy_dashboard_metrics.json
- Total questions: 40
- API calls: 8 successful
- Changes recommended: 12 (31.58%)
- Total cost: $0.0491
- Total time: 187 seconds

### dummy_api_logs.json (8 API calls)
- All successful calls
- Timestamps spread over 2 minutes
- Batch sizes: 5, 5, 5, 5, 5, 5, 4, 2 questions
- Full request/response JSON included

### dummy_validation_report.json
- 27 records attempted, 25 updated, 2 failed
- Performance: 22.3 seconds, 1.21 records/second
- Comprehensive validation checks across 6 sections
- Realistic error examples

---

## 🎯 What You Need To Do

### 1. Run Your Excel Tool
- Process 40 Science questions through your xlwings tool
- Use worksheet_id: `S09TISNID12` (or any Science worksheet)
- Make sure you have a mix of:
  - Questions with corrections
  - Questions with no changes
  - Different error types (spelling, grammar, punctuation)

### 2. Export Question Data
Create `sample_files/questions_sample.json`:

```json
[
  {
    "questionid": 65080,
    "worksheet_id": "S09ATOTAN12",
    "question": "<p>Which of the following statements is/are true?</p>\n<p>A: The symbol of silicon is Si.<br />B: The symbol of gold is Go.</p>",
    "questionImage": null,
    "answer1": "<p>A only</p>",
    "answer1Image": null,
    "answer2": "<p>B only</p>",
    "answer2Image": null,
    "answer3": "<p>Both A and B</p>",
    "answer3Image": null,
    "answer4": "<p>Neither A nor B</p>",
    "answer4Image": null,
    "answer5": null,
    "answer5Image": null,
    "correctanswer": "a",
    "hint": "<p>The symbol of gold is Au.</p>",
    "topic": "Atoms and Molecules",

    "ai_question_rewrite": "<p>Which of the following statements is/are true?</p>\n<p>A: The symbol of silicon is Si.<br />B: The symbol of gold is Go.</p>",
    "ai_question_reason": "No changes needed.",
    "ai_answer1_rewrite": "<p>A only</p>",
    "ai_answer1_reason": "No changes needed.",
    ...

    "ai_processed": true,
    "human_reviewed": false,
    "review_status": "pending",
    "review_classification": null,
    "final_question": null,
    "final_answer1": null,
    ...
  },
  ... (40 total)
]
```

**How to create this:**
1. Export your questions from Excel to CSV
2. Export the LLM assessment results to CSV
3. Use a script or manually merge into JSON format above
4. Include all columns from your database schema

### 3. Export LLM Responses (Already in questions_sample.json)
If you prefer separate file, create `sample_files/llm_responses_sample.json`:

```json
[
  {
    "questionid": 65080,
    "ai_question_rewrite": "...",
    "ai_question_reason": "...",
    ...
  }
]
```

But this is optional if already in questions_sample.json.

### 4. Export Dashboard Metrics
Create `sample_files/dashboard_metrics.json`:

**From your Excel DASHBOARD sheet**, copy the values:

```json
{
  "api_calls": {
    "total": 2,
    "successful": 2,
    "failed": 0
  },
  "questions": {
    "total": 10,
    "processed": 10,
    "changes_recommended": 5,
    "change_rate_percent": 50.0
  },
  "tokens": {
    "input_total": 5832,
    "output_total": 2503,
    "reasoning_total": 0
  },
  "cost": {
    "total_usd": 0.0065,
    "per_question_usd": 0.00065,
    "per_100k_usd": 64.64
  },
  "time": {
    "total_seconds": 41,
    "per_question_seconds": 4.1,
    "per_api_call_seconds": 20.5
  }
}
```

### 5. Create API Logs
Create `sample_files/api_logs.json`:

**From your Excel or Python logs**, extract 5-10 API calls:

```json
[
  {
    "id": "log_001",
    "timestamp": "2025-11-19T14:32:15.234Z",
    "model": "google/gemini-2.5-flash-lite-preview-09-2025",
    "batch_id": "batch_001",
    "question_ids": [65080, 64292, 115135, 227044, 227092],
    "status": "success",
    "tokens_used": {
      "input": 2916,
      "output": 1251,
      "reasoning": 0
    },
    "cost_usd": 0.00325,
    "response_time_ms": 4120,
    "request_json": "{\"model\": \"google/gemini-2.5-flash-lite\", \"messages\": [...], \"max_tokens\": 7000}",
    "response_json": "{\"id\": \"chatcmpl-xyz\", \"choices\": [{\"message\": {...}}], \"usage\": {...}}",
    "error_message": null
  },
  ...
]
```

**How to create this:**
- Check your Python `main_v2.py` console output or logs
- Each API call should have request/response details
- Copy 5-10 examples

### 6. Create Validation Report Template
Create `sample_files/validation_report.json`:

```json
{
  "summary": {
    "total_records": 23,
    "updated_records": 21,
    "failed_records": 2,
    "start_time": "2025-11-19T14:32:10Z",
    "end_time": "2025-11-19T14:32:28Z",
    "duration_seconds": 18
  },
  "performance": {
    "total_time_seconds": 18.4,
    "avg_time_per_record_ms": 800,
    "throughput_records_per_second": 1.25
  },
  "errors": {
    "count": 2,
    "breakdown": [
      {
        "error_type": "Foreign key violation",
        "count": 1,
        "sample_questionids": [156789]
      },
      {
        "error_type": "Null constraint violation",
        "count": 1,
        "sample_questionids": [156790]
      }
    ]
  },
  "validation": {
    "pre_update_count": 19847,
    "post_update_count": 19847,
    "data_integrity_check": "passed",
    "foreign_key_violations": 0,
    "null_constraint_violations": 0
  },
  "rollback_available": true,
  "backup_location": "/backups/2025-11-19_143210.sql"
}
```

This is mostly dummy data for mockup purposes. Use realistic-looking numbers.

---

## 🚀 Quick Export Commands

### From Excel to JSON (Manual)
1. Save each sheet as CSV
2. Use online CSV-to-JSON converter (like csvjson.com)
3. Clean up and format

### From Excel to JSON (Python Script)
```python
import pandas as pd
import json

# Export questions
df = pd.read_excel('your_file.xlsm', sheet_name='QUESTION_SAMPLE')
df.to_json('sample_files/questions_sample.json', orient='records', indent=2)

# Export dashboard
dashboard = {
    "api_calls": {"total": 2, "successful": 2, "failed": 0},
    # ... copy values from Excel
}
with open('sample_files/dashboard_metrics.json', 'w') as f:
    json.dump(dashboard, f, indent=2)
```

---

## ✅ Verification Checklist

Before giving to AI coder, verify:
- [ ] `questions_sample.json` has 40 records
- [ ] All required fields present (questionid, worksheet_id, question, answer1-4, etc.)
- [ ] Some questions have `ai_question_rewrite` populated, some don't
- [ ] `dashboard_metrics.json` has all sections
- [ ] `api_logs.json` has 5-10 log entries
- [ ] `validation_report.json` has all 5 sections
- [ ] All JSON files are valid (no syntax errors)

Test JSON validity: Use https://jsonlint.com/

---

## 📋 Sample Data Checklist by File

### questions_sample.json
- [x] Exists in `docs/PLANs/SAMPLE_DATA.tsv` (need to convert to JSON)
- [ ] Add AI response fields (ai_question_rewrite, ai_question_reason, etc.)
- [ ] Add review fields (review_status, review_classification, etc.)
- [ ] Add flags (ai_processed, human_reviewed)

### dashboard_metrics.json
- [ ] Run Excel tool on 10 questions
- [ ] Copy values from DASHBOARD sheet
- [ ] Format as JSON

### api_logs.json
- [ ] Copy console logs from Python script
- [ ] Extract 5-10 API calls
- [ ] Include full request/response JSON

### validation_report.json
- [ ] Create dummy data (this is for mockup only)
- [ ] Use realistic-looking numbers

---

**Once all files are ready, just zip this entire `PLAN_MOCKUP` folder and give to AI coder!**
