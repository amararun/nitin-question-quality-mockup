# Question Quality Assessment - Implementation Plan
**Scope: Science Subject Only (20K questions) | Version: 1.1 | Date: 2025-11-19**

## Team
- **Nitin** - CEO, Final approvals
- **Shabnam** - Prompt creation, Human reviews
- **Amar** - Technical implementation (available 2-3 days/week)

---

## Compact Plan (Tab-delimited for Excel)

Copy below into Excel:

```
Phase	Step	Task	Days	Owner	Challenge	Solution to Investigate
P1	1.1	Finalize Science prompt in Playground	10	Shabnam	Rules vary by question type (MCQ, fill-blank, assertion-reason)	Test diverse sample; may need conditional logic in prompt
P1	1.2	Replicate settings in xlwings tool	1	Amar	LLM inconsistency across runs	Lock temperature at 0.0; test reproducibility
P1	1.3	Finalize model selection and cost estimate	2	Amar	Cost projection for 20K questions	Run 50 questions; extrapolate cost per 100K for Nitin sign-off
P2	2.1	Run batch of 50-100 Science questions	1	Amar	Manual review tedious	Use Judge LLM to pre-filter; Shabnam reviews flagged only
P2	2.2	Shabnam reviews output quality	3	Shabnam	Different error patterns in different topics	Track which topics fail; may need topic-specific rules
P2	2.3	Iterate prompt based on feedback	7	Amar+Shabnam	Multiple iterations needed	Budget 3-4 prompt revisions before finalizing
P3	3.1	Create Python script for batch API calls	3	Claude Code	N/A	Reuse xlwings logic; add checkpointing
P3	3.2	Set up local MySQL staging database	2	Amar	Need MySQL installed locally	Use XAMPP or Docker MySQL
P3	3.3	Design staging table schema with AI columns	1	Amar	Schema must match production structure	Add ai_rewrite, ai_reason, review_status columns
P3	3.4	Run 5K Science questions (pilot)	3	Amar	API rate limiting at scale	Implement exponential backoff; add delays between batches
P3	3.5	Run remaining 15K Science questions	5	Amar	Connection loss loses progress	Checkpoint after each batch; track last_processed_id; resume
P3	-	Challenge: Cost management	-	-	20K × 8K tokens = 160M tokens	Batch 5-10 questions per call; use flash-lite (~$8-15 per run)
P3	-	Challenge: Batch insert performance	-	-	20K individual INSERTs too slow	Use executemany() with 500-1000 rows per batch
P3	-	Challenge: Error handling	-	-	API failures, JSON parse errors	Log all errors with questionid; create retry queue
P3	-	Challenge: Memory management	-	-	20K questions in memory	Process in chunks of 1000; stream to DB
P4	4.1	Get staging DB access from Nitin	3	Amar	Need AWS RDS credentials	Request read/write access to staging schema only
P4	4.2	Nitin creates staging table on AWS	2	Nitin	Cannot create tables in live DB	Nitin creates questions_ai_staging table
P4	4.3	Migrate Python script to use staging DB	2	Amar	Connection string changes	Use PyMySQL; test connection pooling
P4	4.4	Run full 20K Science on staging	5	Amar	Network drops to AWS RDS	Auto-reconnect; smaller batch commits (100 rows)
P4	-	Challenge: Concurrent access	-	-	Others may read/write same data	Use separate staging table; add processing_status column
P4	-	Challenge: Audit trail	-	-	Track what AI changed	Add ai_processed_at, ai_model columns
P5	5.1	Design review UI mockup	2	Amar+Nitin	UI needs to show original vs rewrite	Side-by-side diff view; color-code changes
P5	5.2	Build PHP page to display one question	5	Dev team	Old PHP version (no framework)	Keep simple; plain PHP with MySQL queries
P5	5.3	Add Accept/Reject buttons + DB update	3	Dev team	Track who approved what	Log user_id + timestamp with each action
P5	5.4	Add navigation and filters	3	Dev team	20K one-by-one impractical	Filter by ai_change_required=1; bulk approve unchanged
P5	5.5	Test with sample data	3	Shabnam	N/A	Test with 100 questions before full rollout
P5	-	Challenge: Review throughput	-	-	Shabnam can review 500/day	20K ÷ 500 = 40 days if all need review; filter to changes only
P6	6.1	Create UPDATE script for approved items	1	Claude Code	N/A	Simple UPDATE WHERE review_status='approved'
P6	6.2	Test on small batch (10 rows)	1	Amar	Verify no data corruption	Compare before/after for HTML entities, special chars
P6	6.3	Get sign-off from Nitin	1	Nitin	Final approval needed	Show sample of approved changes
P6	6.4	Run live update with backup	2	Nitin+Amar	Rollback capability needed	Take full backup before; keep originals in staging
P6	-	Challenge: Partial updates	-	-	Only update specific fields	UPDATE SET only question/answer columns; preserve others
P6	-	Challenge: Validation	-	-	Ensure clean data	Check: no NULL rewrites, balanced HTML tags, length limits
```

---

## Timeline Summary

| Phase | Description | Days | Cumulative |
|-------|-------------|------|------------|
| P1 | Prompt Finalization | 13 | 13 days |
| P2 | Volume Testing (Excel) | 11 | 24 days |
| P3 | Python + Local DB | 14 | 38 days |
| P4 | AWS Staging DB | 12 | 50 days |
| P5 | PHP Review UI | 16 | 66 days |
| P6 | Live Update | 5 | **71 days** |

**Total: ~71 calendar days (~10 weeks)** accounting for Amar's 2-3 days/week availability.

---

## Cost Estimate (20K Science Questions)

| Item | Calculation | Cost |
|------|-------------|------|
| Input tokens | 20K × 3K = 60M | $4.50 |
| Output tokens | 20K × 500 = 10M | $3.00 |
| **Per run** | | **~$8** |
| **5 iterations** | | **~$40** |

Using Gemini Flash Lite @ $0.075/M input, $0.30/M output.

---

## Additional Challenges Not in Main Plan

| Challenge | Impact | Solution |
|-----------|--------|----------|
| HTML entities (&nbsp;, &divide;, <sup>) corrupt in round-trip | High | Test early with complex questions; may need encoding/decoding |
| Image questions (questionImage field) | Medium | Skip AI assessment; flag for manual review |
| Token variance (50-500 per question) | Medium | Dynamic batch sizing based on question length |
| utf8mb3 charset issues | Low | Test mathematical symbols; may need utf8mb4 |

---

*Ready for review with Nitin. Each row explains what takes time and why.*
