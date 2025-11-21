# Question Quality Assessment - React Mockup Implementation Plan

**Version:** 1.0
**Date:** 2025-11-19
**Target:** AI Coder Implementation Guide
**Tech Stack:** React, TypeScript, Vite, shadcn/ui, TailwindCSS

---

## 🎯 PROJECT CONTEXT

### Business Problem
Educational platform has 300K+ MCQ questions in MySQL database. Questions contain grammar/spelling/punctuation errors. Need LLM-based correction system with human review before updating live database.

### Current State
- Python/xlwings tool processes questions through OpenRouter API
- Iterative prompt engineering for Science subject (20K questions)
- Manual review in Excel spreadsheets

### Mockup Objective
Create **non-functional React prototype** demonstrating:
1. How users will browse/search questions
2. How LLM batch processing will work (simulated)
3. How human reviewers will approve/reject corrections
4. How batch updates to production DB will be validated

**Critical:** This is a VISUAL MOCKUP ONLY. No real database, no real API calls. All data hardcoded. Purpose is to demo UI/UX to stakeholders and guide future development.

---

## 🏗️ ARCHITECTURE OVERVIEW

### Navigation Structure
**Top Navigation Bar** with 3 main sections:
1. **Review** - Browse questions, see AI corrections, manual review
2. **LLM Connection** - Configure and run batch processing (simulated)
3. **Batch Update** - Push approved changes to DB (simulated)

### Data Flow (Simulated)
```
[Sample Data] → [Review Module: Shows records]
                ↓
[User clicks Process] → [LLM Connection: Simulates 5-7s API call]
                ↓
[State Updated] → [Review Module: Shows AI rewrites]
                ↓
[Human Review] → [Approve/Reject with classification]
                ↓
[Batch Update] → [Simulates DB update with progress + validation report]
```

### State Management
Use **React Context API** to maintain:
- Current worksheet_id
- Processed state (has LLM been run in this session?)
- Approved records
- Filter selections
- Active navigation tab

Store in **localStorage** to persist during demo session.

---

## 📁 PROJECT FILE STRUCTURE

```
question-quality-mockup/
├── public/
│   └── dummy-question-image.jpg          # Educational image for mockup
├── src/
│   ├── components/
│   │   ├── ui/                          # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── select.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── card.tsx
│   │   │   ├── progress.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── TopNav.tsx               # Main navigation
│   │   │   └── Layout.tsx               # Page wrapper
│   │   ├── review/
│   │   │   ├── ReviewModule.tsx         # Main review interface
│   │   │   ├── QuestionTable.tsx        # Collapsed table view
│   │   │   ├── QuestionModal.tsx        # Expanded detail view
│   │   │   ├── FilterPanel.tsx          # Worksheet ID + filters
│   │   │   └── ClassificationButtons.tsx
│   │   ├── llm/
│   │   │   ├── LLMModule.tsx            # Main LLM interface
│   │   │   ├── ParametersTab.tsx        # Config + Submit
│   │   │   ├── APIDetailsTab.tsx        # API call results
│   │   │   ├── DashboardTab.tsx         # Metrics dashboard
│   │   │   └── APILogsTab.tsx           # Request/response logs
│   │   ├── batch/
│   │   │   ├── BatchUpdateModule.tsx    # Main batch interface
│   │   │   ├── ProgressIndicator.tsx    # Update progress bar
│   │   │   ├── ValidationReport.tsx     # Multi-section report
│   │   │   └── RollbackButton.tsx       # Rollback simulation
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── CopyButton.tsx
│   │       └── DownloadButton.tsx
│   ├── context/
│   │   └── AppContext.tsx               # Global state
│   ├── data/
│   │   ├── mockQuestions.ts             # Hardcoded question data
│   │   ├── mockLLMResponses.ts          # Hardcoded AI rewrites
│   │   ├── mockDashboard.ts             # Hardcoded metrics
│   │   ├── mockAPILogs.ts               # Hardcoded logs
│   │   └── mockValidation.ts            # Hardcoded validation data
│   ├── types/
│   │   └── index.ts                     # TypeScript interfaces
│   ├── lib/
│   │   └── utils.ts                     # Helper functions
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🎨 DESIGN SYSTEM SPECIFICATIONS

### Color Palette
```typescript
const colors = {
  primary: '#3b82f6',      // Blue - primary actions
  success: '#22c55e',      // Green - approved, success
  warning: '#eab308',      // Yellow - warnings, pending
  error: '#ef4444',        // Red - errors, rejected
  neutral: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    500: '#64748b',
    700: '#334155',
    900: '#0f172a',
  },
}
```

### Typography
- Body: `text-sm` (14px) for most content
- Tables: `text-xs` (12px) for data-dense areas
- Headings: `text-lg` (18px) section titles, `text-xl` (20px) page titles
- Font: System font stack (Inter/SF Pro)

### Spacing
- Tight: `p-1` (4px), `p-2` (8px) for compact tables
- Standard: `p-4` (16px) for cards, `p-6` (24px) for sections
- Loose: `p-8` (32px) for page padding

### Component Patterns
1. **Tables**: Fixed header, scrollable body, alternating row colors
2. **Modals**: Max-width 90vw, max-height 90vh, scrollable content
3. **Cards**: White background, subtle border, slight shadow
4. **Buttons**: Primary (blue), Secondary (gray), Destructive (red)
5. **Badges**: Pill-shaped, colored by status (Approved=green, Pending=yellow, Error=red)

---

## 📊 DATA STRUCTURE SPECIFICATIONS

### Question Record (TypeScript Interface)
```typescript
interface Question {
  questionid: number;
  worksheet_id: string;           // e.g., "S09TISNID12"
  question: string;               // HTML with <p>, <ol>, etc.
  questionImage?: string;         // Filename or null
  answer1: string;
  answer1Image?: string;
  answer2: string;
  answer2Image?: string;
  answer3: string;
  answer3Image?: string;
  answer4: string;
  answer4Image?: string;
  answer5?: string;
  answer5Image?: string;
  correctanswer: string;          // 'a', 'b', 'c', 'd', 'e'
  hint?: string;
  topic?: string;

  // AI Processing fields (added by LLM)
  ai_question_rewrite?: string;
  ai_question_reason?: string;
  ai_answer1_rewrite?: string;
  ai_answer1_reason?: string;
  ai_answer2_rewrite?: string;
  ai_answer2_reason?: string;
  ai_answer3_rewrite?: string;
  ai_answer3_reason?: string;
  ai_answer4_rewrite?: string;
  ai_answer4_reason?: string;
  ai_answer5_rewrite?: string;
  ai_answer5_reason?: string;

  // Review fields (added by human)
  review_status?: 'pending' | 'approved' | 'rejected';
  review_classification?: 'all_ok' | 'mistake' | 'hallucinated' | 'other';
  final_question?: string;
  final_answer1?: string;
  final_answer2?: string;
  final_answer3?: string;
  final_answer4?: string;
  final_answer5?: string;

  // Metadata
  ai_processed: boolean;
  human_reviewed: boolean;
}
```

### Dashboard Metrics
```typescript
interface DashboardMetrics {
  api_calls: {
    total: number;
    successful: number;
    failed: number;
  };
  questions: {
    total: number;
    processed: number;
    changes_recommended: number;
    change_rate_percent: number;
  };
  tokens: {
    input_total: number;
    output_total: number;
    reasoning_total: number;
  };
  cost: {
    total_usd: number;
    per_question_usd: number;
    per_100k_usd: number;
  };
  time: {
    total_seconds: number;
    per_question_seconds: number;
    per_api_call_seconds: number;
  };
}
```

### API Log Entry
```typescript
interface APILogEntry {
  id: string;
  timestamp: string;              // ISO 8601
  model: string;                  // e.g., "google/gemini-2.5-flash-lite"
  batch_id: string;
  question_ids: number[];
  status: 'success' | 'failed';
  tokens_used: {
    input: number;
    output: number;
    reasoning?: number;
  };
  cost_usd: number;
  response_time_ms: number;
  request_json?: string;          // Full request (expandable)
  response_json?: string;         // Full response (expandable)
  error_message?: string;
}
```

### Validation Report
```typescript
interface ValidationReport {
  summary: {
    total_records: number;
    updated_records: number;
    failed_records: number;
    start_time: string;
    end_time: string;
    duration_seconds: number;
  };
  performance: {
    total_time_seconds: number;
    avg_time_per_record_ms: number;
    throughput_records_per_second: number;
  };
  errors: {
    count: number;
    breakdown: Array<{
      error_type: string;
      count: number;
      sample_questionids: number[];
    }>;
  };
  validation: {
    pre_update_count: number;
    post_update_count: number;
    data_integrity_check: 'passed' | 'failed';
    foreign_key_violations: number;
    null_constraint_violations: number;
  };
  rollback_available: boolean;
  backup_location?: string;
}
```

---

## 🚀 PHASE-BY-PHASE IMPLEMENTATION

### PHASE 1: Project Setup + Review Module (Core)
**Goal:** Users can browse questions and see basic table view.

**Deliverable:** Working Review module with question browsing (no AI data yet).

#### Tasks:
1. **Initialize Project** (15 min)
   ```bash
   npm create vite@latest question-quality-mockup -- --template react-ts
   cd question-quality-mockup
   npm install
   ```

2. **Install Dependencies** (10 min)
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   npm install class-variance-authority clsx tailwind-merge lucide-react
   ```

3. **Setup shadcn/ui** (20 min)
   ```bash
   npx shadcn-ui@latest init
   npx shadcn-ui@latest add button table dialog input select badge tabs card
   ```

4. **Create Base Layout** (30 min)
   - `src/components/layout/Layout.tsx`: Page wrapper with header
   - `src/components/layout/TopNav.tsx`: Navigation bar with 3 items (Review, LLM Connection, Batch Update)
   - Use state to track active nav item
   - Style: White background, subtle border-bottom, blue active indicator

5. **Create AppContext** (20 min)
   - `src/context/AppContext.tsx`: Context provider with:
     - `worksheetId: string`
     - `activeNav: 'review' | 'llm' | 'batch'`
     - `processedState: boolean` (has LLM been run?)
     - `questions: Question[]`
     - Helper functions: `setWorksheetId`, `setActiveNav`, `markAsProcessed`
   - Use localStorage for persistence

6. **Create Mock Question Data** (30 min)
   - `src/data/mockQuestions.ts`:
     - Import sample data from `sample_files/questions_sample.json` (user will provide)
     - For now, create 40 dummy questions with worksheet_id "S09TISNID12"
     - Fields: questionid, worksheet_id, question, answer1-4, correctanswer
     - Leave AI fields blank initially

7. **Build QuestionTable Component** (45 min)
   - `src/components/review/QuestionTable.tsx`:
     - Display 10 rows at a time
     - Columns shown: questionid, worksheet_id, question (truncated), status badge
     - Status badge: Gray "Not Processed" initially
     - Next/Previous pagination buttons
     - Each row has "Expand" button (eye icon)
     - Use shadcn `<Table>` component
     - Style: Compact (`text-xs`), alternating row colors, fixed header

8. **Build FilterPanel Component** (30 min)
   - `src/components/review/FilterPanel.tsx`:
     - Input for worksheet_id
     - Refresh button
     - Dropdowns: Review Status (All/Pending/Approved), LLM Classification (All/All OK/Mistake/Hallucinated)
     - On refresh: Fetch questions matching worksheet_id from mock data
     - Style: Card with light gray background, horizontal layout

9. **Build ReviewModule Component** (30 min)
   - `src/components/review/ReviewModule.tsx`:
     - Container combining FilterPanel + QuestionTable
     - Pass filtered questions to table
     - Handle pagination state

10. **Wire Up Layout** (15 min)
    - `src/App.tsx`:
      - Wrap with AppContext provider
      - Render Layout component
      - Conditionally render ReviewModule when activeNav === 'review'

**Testing:**
- User can enter worksheet_id, see 10 questions in table
- Pagination works (Next/Previous)
- Status shows "Not Processed" for all rows
- Expand button exists but doesn't do anything yet

---

### PHASE 2: Question Detail Modal
**Goal:** Users can click Expand and see full question details in modal.

**Deliverable:** Modal showing all 30+ fields in organized layout.

#### Tasks:
1. **Build QuestionModal Component** (90 min)
   - `src/components/review/QuestionModal.tsx`:
     - shadcn `<Dialog>` with full-screen width (90vw × 90vh)
     - Scrollable content area
     - **Layout Structure:**
       ```
       [Header: Question ID + Worksheet ID + Close button]

       [Left Column (50%)]
         - Original Question (HTML rendered)
         - Image placeholder if questionImage exists
         - Answer Options (A-E)
         - Correct Answer badge
         - Hint (if exists)

       [Right Column (50%)]
         - LLM Rewrite Section:
           - Question Rewrite (if exists, else "No changes")
           - Question Reason
           - Answer Rewrites (each with reason)
         - Classification Buttons (All OK, Mistake, Hallucinated, Other)
         - Edit Box (labeled "Final Version"):
           - Pre-populated with: If ai_question_rewrite exists, show rewrite; else show original
           - User can modify
         - Approve Button (green, primary)
         - Status Badge (shows current review_status)
       ```
     - **Judgment Call: Edit Box Content**
       - Initial state: Show AI rewrite if exists, else original question
       - User modifies this to create final version
       - On Approve: Copy edit box content to `final_question` field
     - Style: Two-column grid on desktop, stacked on mobile
     - Use `dangerouslySetInnerHTML` to render HTML question content

2. **Add Classification Buttons** (30 min)
   - `src/components/review/ClassificationButtons.tsx`:
     - Four buttons: All OK (green), Mistake (red), Hallucinated (yellow), Other (gray)
     - On click: Update question's `review_classification` field
     - Visual feedback: Selected button has filled background

3. **Wire Modal to Table** (20 min)
   - QuestionTable: Pass onClick handler to Expand button
   - Open QuestionModal with selected question
   - Modal updates question data in context on Approve

4. **Add Dummy Image** (10 min)
   - `public/dummy-question-image.jpg`: Download any small educational image (diagram, formula, etc.)
   - In modal: If questionImage field exists, show `<img src="/dummy-question-image.jpg" />`

**Testing:**
- Click Expand → Modal opens with question details
- Can see all 30+ fields in organized layout
- Classification buttons work (visual feedback)
- Edit box is editable
- Approve button updates status (but doesn't close modal)
- ESC or X closes modal

---

### PHASE 3: LLM Connection Module
**Goal:** Simulate batch LLM processing with loading state and results.

**Deliverable:** Working LLM module that "processes" questions and updates Review module.

#### Tasks:
1. **Build LLMModule Component** (30 min)
   - `src/components/llm/LLMModule.tsx`:
     - shadcn `<Tabs>` component with 4 tabs:
       1. Parameters
       2. API Details
       3. Dashboard
       4. API Logs
     - Initially only Parameters tab is enabled; others are grayed out

2. **Build ParametersTab** (45 min)
   - `src/components/llm/ParametersTab.tsx`:
     - Form inputs:
       - Model: Dropdown (Google/Gemini Flash Lite, OpenAI GPT-4, etc.)
       - Max Tokens: Number input (default 7000)
       - Temperature: Number input (default 0.2)
       - Top-P: Number input (default 1)
       - Enable Thinking: Toggle switch
       - Enable Reasoning: Toggle switch
     - Worksheet ID: Input (pre-filled from context)
     - Batch Size: Number input (default 10)
     - Submit Button: "Process Questions"
     - Style: Two-column grid layout, compact form

3. **Implement Mock Processing** (60 min)
   - On Submit click:
     1. Disable Submit button
     2. Show loading spinner overlay with text: "Processing 10 questions... Please wait"
     3. Use `setTimeout` for 5-7 seconds (random)
     4. During wait: Optionally show fake progress: "Processed 3/10 questions..."
     5. After timeout:
        - Update context: `markAsProcessed(true)`
        - Populate mock AI responses for all questions (import from `mockLLMResponses.ts`)
        - Enable tabs 2-4
        - Switch to Dashboard tab
        - Show success toast: "✓ API call completed. 10 questions processed."

4. **Create Mock LLM Response Data** (45 min)
   - `src/data/mockLLMResponses.ts`:
     - For each question in mock data, add:
       - `ai_question_rewrite`: Slightly corrected version (fix 1-2 grammar/spelling errors)
       - `ai_question_reason`: "Fixed spelling error: 'symble' → 'symbol'" (example)
       - Similar for each answer option
     - Use realistic corrections based on actual LLM output patterns
     - Some questions have no changes (ai_rewrite === original)

5. **Build APIDetailsTab** (30 min)
   - `src/components/llm/APIDetailsTab.tsx`:
     - Display summary card:
       - Model used
       - Total questions processed
       - Total tokens used
       - Total cost
       - Time taken
     - Use hardcoded values (import from `mockDashboard.ts`)
     - Style: Grid of 2-3 cards with icons

6. **Build DashboardTab** (90 min)
   - `src/components/llm/DashboardTab.tsx`:
     - **Top Row: Metric Cards** (4 cards)
       - Total Questions, Change Rate %, Total Cost, Total Time
       - Large number + label + icon
     - **Second Row: Charts** (2 small charts)
       - Bar chart: Questions by status (Processed, Changes, No Changes)
       - Line chart: Token usage over time (fake data)
       - Use simple SVG or just show placeholder boxes labeled "Chart: ..."
     - **Bottom: Data Tables** (3 tables side-by-side)
       - Cost Breakdown (Input, Output, Total)
       - Token Usage (Input, Output, Reasoning)
       - Performance Metrics (Avg time, Throughput)
     - Copy button on each table
     - Style: Dashboard layout with whitespace, cards with shadows

7. **Build APILogsTab** (45 min)
   - `src/components/llm/APILogsTab.tsx`:
     - Table of log entries (5-10 rows)
     - Columns: Timestamp, Model, Batch ID, Status, Tokens, Cost, Time
     - Click row → Expand to show full request/response JSON
     - Use `<details>` element or accordion
     - Copy button for each JSON block
     - Style: Monospace font for JSON, compact table

8. **Create Mock Dashboard/Log Data** (30 min)
   - `src/data/mockDashboard.ts`: Hardcoded metrics matching DashboardMetrics interface
   - `src/data/mockAPILogs.ts`: 5-10 log entries matching APILogEntry interface

**Testing:**
- Click "LLM Connection" nav item → Parameters tab visible
- Fill in parameters, click Process
- Loading spinner shows for 5-7 seconds
- After completion: Dashboard tab active, shows metrics
- Switch to API Logs tab, see log entries
- Click log entry → JSON expands
- Go back to Review module → Questions now show "Processed" status badge
- Click Expand on processed question → See AI rewrites in modal

---

### PHASE 4: Batch Update Module
**Goal:** Simulate updating production database with validation report.

**Deliverable:** Working batch update with progress indicator and detailed validation report.

#### Tasks:
1. **Build BatchUpdateModule Component** (30 min)
   - `src/components/batch/BatchUpdateModule.tsx`:
     - Input: Worksheet ID (pre-filled from context)
     - Filter: Only show questions with `review_status === 'approved'`
     - Display count: "23 approved questions ready for update"
     - Submit Button: "Update Production Database"
     - Warning message: "⚠️ This will update live data. Ensure all approvals are correct."

2. **Implement Progress Indicator** (60 min)
   - `src/components/batch/ProgressIndicator.tsx`:
     - On Submit click:
       1. Disable button
       2. Show progress bar with label: "Updating 23 records..."
       3. Simulate progress over 15-20 seconds:
          - Start at 0%, increment by random 5-10% every 1-2 seconds
          - Show: "7 of 23 records updated..."
          - Use shadcn `<Progress>` component
       4. At 100%: Show checkmark + "✓ Update complete"
       5. Display ValidationReport component

3. **Build ValidationReport Component** (90 min)
   - `src/components/batch/ValidationReport.tsx`:
     - **Header:** "Database Update Validation Report" + timestamp
     - **Section 1: Records Summary** (Card)
       - Total Records: 23
       - Successfully Updated: 21
       - Failed: 2
       - Start Time: 2025-11-19 14:32:10
       - End Time: 2025-11-19 14:32:28
       - Duration: 18 seconds
     - **Section 2: Performance Metrics** (Card)
       - Total Time: 18.4s
       - Avg Time per Record: 0.8s
       - Throughput: 1.25 records/second
     - **Section 3: Error Breakdown** (Card + Table)
       - Error Count: 2
       - Table with columns: Error Type, Count, Sample Question IDs
       - Example: "Foreign key violation | 1 | [156789]"
       - Example: "Null constraint violation | 1 | [156790]"
     - **Section 4: Data Integrity Validation** (Card)
       - Pre-Update Record Count: 19,847
       - Post-Update Record Count: 19,847 (unchanged)
       - Data Integrity Check: ✓ Passed
       - Foreign Key Violations: 0
       - Null Constraint Violations: 0
       - Checksum Validation: (Judgment call on what makes sense)
         - Maybe: "Unmodified column checksums match" ✓
         - Or: "Sample verification: 10/10 records correct" ✓
     - **Section 5: Rollback Information** (Card)
       - Backup Available: ✓ Yes
       - Backup Location: `/backups/2025-11-19_143210.sql` (dummy path)
       - Rollback Available: ✓ Yes
       - Rollback Button (see next task)
     - **Section 6: Additional Validation Checks** (Card)
       - HTML Tags Balanced: ✓ Passed (all question/answer HTML valid)
       - Character Encoding: ✓ Passed (no corruption)
       - Field Length Limits: ✓ Passed (no truncation)
       - Referential Integrity: ✓ Passed
     - Style: Cards arranged in 2-column grid, lots of whitespace, use green checkmarks

4. **Add Download/Copy Buttons** (30 min)
   - Download PDF button (mocked): Click → Show toast "Downloading report.pdf..."
   - Copy CSV button: Click → Copy validation data to clipboard as tab-delimited text
   - Use `navigator.clipboard.writeText()`

5. **Build RollbackButton Component** (30 min)
   - `src/components/batch/RollbackButton.tsx`:
     - Red button: "Rollback to Previous State"
     - Confirmation dialog: "Are you sure? This will restore the database to pre-update state."
     - On confirm:
       1. Show loading spinner: "Rolling back... Please wait"
       2. Use `setTimeout` for 10 seconds
       3. After timeout: Show success message: "✓ Original database restored from backup"
       4. Update count in BatchUpdateModule: "0 approved questions (rollback completed)"

6. **Create Mock Validation Data** (20 min)
   - `src/data/mockValidation.ts`: Hardcoded ValidationReport data matching interface

**Testing:**
- Click "Batch Update" nav item
- See count of approved questions (need to approve some in Review module first)
- Click "Update Production Database"
- Progress bar animates over 15-20 seconds
- Validation report displays with all 6 sections
- Download button shows toast
- Copy button copies to clipboard
- Rollback button works (confirmation → progress → success message)

---

### PHASE 5: Polish & Refinements
**Goal:** Fix bugs, improve UX, add final touches.

**Deliverable:** Production-ready mockup for demo.

#### Tasks:
1. **State Synchronization** (45 min)
   - Ensure Review module updates when LLM processing completes
   - Ensure status badges reflect current state
   - Add refresh button that checks localStorage and updates display
   - Test: Process questions in LLM module → Go to Review → See "Processed" badges

2. **Filter Functionality** (30 min)
   - Review Status dropdown: Filter table by pending/approved/all
   - LLM Classification dropdown: Filter by all_ok/mistake/hallucinated/other
   - Both filters work together (AND logic)

3. **Responsive Design** (45 min)
   - Test on mobile viewport
   - Modal: Stack columns vertically on small screens
   - Dashboard: Cards stack on mobile
   - Tables: Horizontal scroll on mobile

4. **Loading States** (30 min)
   - Add skeleton loaders for tables while "loading"
   - Spinner components for long operations
   - Disable buttons during processing

5. **Error Handling** (30 min)
   - Mock: If batch size > 50, show error: "Batch size too large. Max 50 questions."
   - Mock: If worksheet_id not found, show: "No questions found for this worksheet."

6. **Accessibility** (20 min)
   - Add ARIA labels to buttons
   - Keyboard navigation for modal
   - Focus management (trap focus in modal)

7. **Final Design Polish** (60 min)
   - Consistent spacing throughout
   - Hover states on all interactive elements
   - Smooth transitions (fade in/out for modals, progress bars)
   - Icon consistency (use lucide-react icons)
   - Typography hierarchy (ensure headings stand out)

8. **Demo Data Variety** (30 min)
   - Ensure mock data has variety:
     - Some questions with no AI changes
     - Some with spelling corrections
     - Some with grammar corrections
     - Some marked as "Mistake" by human
     - Some marked as "Hallucinated"
   - Add 2-3 different worksheet_ids so user can test filtering

**Testing:**
- Full end-to-end flow:
  1. Enter worksheet_id → See questions
  2. Click LLM Connection → Process → See results
  3. Go to Review → See processed questions
  4. Expand question → Review → Classify → Approve
  5. Go to Batch Update → Update DB → See validation report
  6. Test rollback
- Test on different screen sizes
- Test all filters and navigation

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Review Module Core
- [ ] Project initialized with Vite + React + TypeScript
- [ ] shadcn/ui installed and configured
- [ ] Layout components (TopNav, Layout) created
- [ ] AppContext with state management
- [ ] Mock question data created
- [ ] QuestionTable displays 10 rows
- [ ] FilterPanel with worksheet_id input
- [ ] Pagination works
- [ ] Status badges show "Not Processed"

### Phase 2: Question Detail Modal
- [ ] QuestionModal component created
- [ ] Two-column layout (Original | AI Rewrite)
- [ ] All 30+ fields displayed
- [ ] Classification buttons work
- [ ] Edit box editable and updates state
- [ ] Approve button marks as approved
- [ ] Modal doesn't close on approve
- [ ] Dummy image displays if questionImage exists

### Phase 3: LLM Connection Module
- [ ] LLMModule with tabs created
- [ ] ParametersTab with form inputs
- [ ] Submit triggers loading spinner
- [ ] Mock processing updates state after 5-7s
- [ ] Mock AI responses populate questions
- [ ] APIDetailsTab shows summary
- [ ] DashboardTab shows metrics + charts + tables
- [ ] APILogsTab shows expandable logs
- [ ] Review module updates with "Processed" badges

### Phase 4: Batch Update Module
- [ ] BatchUpdateModule shows approved count
- [ ] Progress indicator animates over 15-20s
- [ ] ValidationReport displays 6 sections
- [ ] All validation metrics populated
- [ ] Download PDF button (mocked)
- [ ] Copy CSV button works
- [ ] Rollback button with confirmation
- [ ] Rollback simulates 10s process

### Phase 5: Polish
- [ ] State synchronization working
- [ ] Filters work (Review Status, LLM Classification)
- [ ] Responsive on mobile
- [ ] Loading states and skeletons
- [ ] Error handling for edge cases
- [ ] Accessibility (ARIA, keyboard nav)
- [ ] Design polish (spacing, hover, transitions)
- [ ] Variety in mock data

---

## 🎯 JUDGMENT CALLS MADE

### 1. Edit Box Content
**Decision:** Pre-populate with AI rewrite if exists, else original question.
**Rationale:** Allows human to start with LLM suggestion and refine. If no LLM suggestion, they can manually edit original.

### 2. Validation Metrics
**Decision:** Include 6 sections with focus on data integrity:
- Records summary (basic counts)
- Performance metrics (time, throughput)
- Error breakdown (types + sample IDs)
- Data integrity (foreign keys, nulls, checksums)
- Rollback info
- Additional checks (HTML, encoding, lengths)

**Rationale:** Real-world DB updates need confidence checks. These cover common failure modes and give reviewer assurance.

### 3. Checksum Validation Approach
**Decision:** Use "Unmodified column checksums match" check.
**Rationale:** In real implementation, could compute SHA hash of columns NOT being updated before/after batch operation. If hashes differ, something went wrong. For mockup, just show "✓ Passed".

### 4. Progress Indicator Details
**Decision:** Show both percentage bar and "X of Y records updated" text, update every 1-2 seconds.
**Rationale:** Users want both overall progress (%) and concrete progress (count). Dual indicator reduces anxiety during long wait.

### 5. Dashboard Layout
**Decision:** Cards (top) → Charts (middle) → Tables (bottom).
**Rationale:** F-pattern reading. Users see key metrics first, then visual trends, then detailed breakdowns if needed.

### 6. Modal Column Layout
**Decision:** 50/50 split on desktop (Original | AI+Review), stacked on mobile.
**Rationale:** Side-by-side comparison is essential for reviewing corrections. Mobile users can scroll.

### 7. Classification Without Comments
**Decision:** No comment field for classification, just button selection.
**Rationale:** Keeps UI simple. If needed, can be added in Phase 5. User can describe issues in edit box if critical.

---

## 🗂️ SAMPLE DATA REQUIREMENTS

User will provide these files in `docs/PLANs/PLAN_MOCKUP/sample_files/`:

### Required Files:
1. **`questions_sample.json`**
   - Array of 40 Question objects
   - Mix of worksheet_ids (S09..., S10..., S08...)
   - Some with questionImage fields populated
   - Include all 30+ columns from database

2. **`llm_responses_sample.json`**
   - Array of AI rewrite objects for each question
   - Format: `{ questionid, ai_question_rewrite, ai_question_reason, ai_answer1_rewrite, ai_answer1_reason, ... }`
   - Variety: Some with no changes, some with spelling fixes, some with grammar fixes

3. **`dashboard_metrics.json`**
   - Single DashboardMetrics object with realistic values
   - Example: `{ api_calls: { total: 2, successful: 2, failed: 0 }, ... }`

4. **`api_logs.json`**
   - Array of 5-10 APILogEntry objects
   - Include full request_json and response_json (large strings)

5. **`validation_report.json`**
   - Single ValidationReport object with all sections populated
   - Realistic error examples if any

### Fallback:
If user doesn't provide files, AI coder should generate dummy data following TypeScript interfaces above.

---

## ⚡ QUICK START FOR AI CODER

1. **Read this entire plan** to understand context and architecture.
2. **Check `sample_files/` directory** for provided data. If missing, generate dummy data.
3. **Start with Phase 1** - don't skip ahead. Each phase builds on previous.
4. **Test each phase** before moving to next. Use checklist above.
5. **Follow design system** - use specified colors, spacing, typography.
6. **Use shadcn/ui components** - don't build from scratch.
7. **All data is hardcoded** - no fetch calls, no real APIs.
8. **Focus on visual fidelity** - this is a mockup to impress stakeholders.

---

## 📸 VISUAL REFERENCE NOTES

### Review Module:
- Think: "Data table with expand drawers" (like Vercel's deployment list)
- Compact, scannable, clear status indicators

### LLM Connection Module:
- Think: "Processing dashboard" (like Stripe API logs)
- Tabs for different views, metrics prominently displayed

### Batch Update Module:
- Think: "Deployment status page" (like Netlify deploy logs)
- Progress → Success → Detailed report

### Overall Vibe:
- Professional SaaS app (Notion, Linear, Vercel aesthetic)
- Lots of whitespace
- Subtle shadows and borders
- Blue as primary color
- Clean, modern, minimalistic

---

## 🚨 COMMON PITFALLS TO AVOID

1. **Don't overcomplicate state management** - Context API is sufficient for mockup.
2. **Don't build real API calls** - Everything hardcoded. Use setTimeout for delays.
3. **Don't skip responsive design** - Even though desktop-first, should work on mobile.
4. **Don't use inconsistent colors** - Stick to design system palette.
5. **Don't forget loading states** - Every async action needs spinner/skeleton.
6. **Don't make tables hard to read** - Use alternating rows, fixed headers.
7. **Don't forget copy/download buttons** - Stakeholders will want to test these.
8. **Don't use complex chart libraries** - Simple SVG or even placeholder boxes are fine.

---

## ✅ DEFINITION OF DONE

Mockup is complete when:
1. ✅ All 3 navigation sections (Review, LLM Connection, Batch Update) are functional
2. ✅ User can simulate full workflow: Browse → Process → Review → Approve → Batch Update
3. ✅ All modals, tables, tabs, filters work as specified
4. ✅ Progress indicators and loading states are smooth
5. ✅ Validation report shows 6 detailed sections
6. ✅ Download and copy buttons are present (even if mocked)
7. ✅ Design matches specifications (colors, spacing, typography)
8. ✅ Responsive on desktop and mobile
9. ✅ No console errors
10. ✅ State persists across browser refresh (localStorage)

---

## 📞 QUESTIONS FOR USER (After Implementation Start)

1. **Sample data not provided** - Should I generate dummy data or wait?
2. **Chart libraries** - Use Recharts or just show placeholder boxes?
3. **Authentication** - Add fake login screen or start directly in app?
4. **Worksheet ID validation** - Should invalid IDs show error or just empty table?
5. **Max questions per batch** - Any limit or allow any number?

---

**END OF IMPLEMENTATION PLAN**

*This plan is optimized for AI coder execution. Follow phases sequentially. Each phase is independently testable. Good luck!* 🚀
