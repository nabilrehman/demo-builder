# CE Provisioning Progress Messages
## Real-Time Progress + Humor for Customer Engineer Dashboard

This file defines the progress messaging system for the 7-stage agentic demo provisioning pipeline. Each message combines **actual progress data** with **contextual humor** similar to the 122 witty loading messages in the existing UI.

---

## Message Structure

Each progress update includes:
- **Stage Number** (1-7)
- **Agent Name**
- **Status** (pending/running/complete/failed)
- **Elapsed Time**
- **Witty Message** (contextual to the agent's work)

---

## Stage 1: Research Agent (15-30 seconds)

### Running Messages (rotate every 4 seconds):
```
Stage 1/7: Research Agent • Running (0:05)
📊 Scraping customer website... attempting to understand their business better than they do.

Stage 1/7: Research Agent • Running (0:10)
🔍 Analyzing homepage... if their "About Us" page says "we're passionate about synergy," we might be in trouble.

Stage 1/7: Research Agent • Running (0:15)
🧠 Claude 4.5 is reading their mission statement... and trying not to laugh at the buzzwords.

Stage 1/7: Research Agent • Running (0:20)
🌐 Extracting business domain... categorizing as "definitely uses spreadsheets."

Stage 1/7: Research Agent • Running (0:25)
✨ Identifying use cases... spoiler: they need data analytics (they just don't know it yet).
```

### Completion Message:
```
Stage 1/7: Research Agent • Complete (0:15) ✅
🎯 Industry identified: [ACTUAL INDUSTRY]. Claude is already planning the perfect sales pitch.
```

### Failure Message:
```
Stage 1/7: Research Agent • Failed (0:30) ❌
🚨 Website scraping failed. Either they have aggressive bot detection or their site is just that broken.
```

---

## Stage 2: Demo Story Agent (4-7 minutes)

### Running Messages (rotate every 4 seconds):
```
Stage 2/7: Demo Story Agent • Running (0:30)
✍️ Claude 4.5 is channeling its inner Principal Architect... this is where the magic happens.

Stage 2/7: Demo Story Agent • Running (1:15)
🎭 Creating executive-level narrative... because "show me a dashboard" isn't a compelling demo.

Stage 2/7: Demo Story Agent • Running (2:00)
💡 Generating golden queries... the kind that make CTOs say "wait, we can do THAT?"

Stage 2/7: Demo Story Agent • Running (3:00)
📖 Writing demo script... with just enough technical depth to sound smart without being scary.

Stage 2/7: Demo Story Agent • Running (4:00)
🧩 Designing business challenges... that coincidentally align perfectly with our product capabilities.

Stage 2/7: Demo Story Agent • Running (5:00)
🎯 Claude is still thinking... this is strategic storytelling, not Mad Libs.

Stage 2/7: Demo Story Agent • Running (5:30)
⏰ Almost there... good narratives take time (and 128K context windows).
```

### Completion Message:
```
Stage 2/7: Demo Story Agent • Complete (5:24) ✅
🎉 Demo Title: "[ACTUAL DEMO TITLE]"
💎 Golden Queries: [COUNT] queries ranging from "executive dashboard" to "holy sh*t that's complex"
```

### Failure Message:
```
Stage 2/7: Demo Story Agent • Failed (6:00) ❌
💀 Claude couldn't generate a compelling story. The industry might be too niche, or we've found the one business case CAPI can't solve.
```

---

## Stage 3: Data Modeling Agent (30-60 seconds)

### Running Messages (rotate every 4 seconds):
```
Stage 3/7: Data Modeling Agent • Running (0:10)
🗄️ Gemini is designing schema... thinking in tables, not entities.

Stage 3/7: Data Modeling Agent • Running (0:20)
🔗 Creating relationships... one-to-many, many-to-many, and "oh god why is this so complicated?"

Stage 3/7: Data Modeling Agent • Running (0:30)
📐 Optimizing for story-driven queries... because demo data should actually answer the golden queries.

Stage 3/7: Data Modeling Agent • Running (0:40)
🧮 Calculating table sizes... aiming for "realistic" not "production nightmare."

Stage 3/7: Data Modeling Agent • Running (0:50)
⚙️ Finalizing schema... and praying Gemini doesn't use REPEATED fields (we have a history).
```

### Completion Message:
```
Stage 3/7: Data Modeling Agent • Complete (0:42) ✅
📊 Schema designed: [TABLE_COUNT] tables with [TOTAL_FIELDS] fields
🎯 Optimized for [QUERY_COUNT] golden queries
```

### Failure Message:
```
Stage 3/7: Data Modeling Agent • Failed (1:00) ❌
🛑 Schema generation failed. Gemini might have suggested REPEATED fields again. We'll never learn.
```

---

## Stage 4: Synthetic Data Generator (30-90 seconds)

### Running Messages (rotate every 4 seconds):
```
Stage 4/7: Synthetic Data Generator • Running (0:10)
🎲 Generating fake data... that's more realistic than half our customers' production data.

Stage 4/7: Synthetic Data Generator • Running (0:20)
👥 Creating synthetic customers... with names like "Jennifer Martinez" and emails like "jennifer.martinez.1847@example.com"

Stage 4/7: Synthetic Data Generator • Running (0:30)
💰 Generating transaction data... with suspiciously round numbers and perfect distributions.

Stage 4/7: Synthetic Data Generator • Running (0:40)
📈 Faker is working overtime... producing data that "looks real enough™"

Stage 4/7: Synthetic Data Generator • Running (0:50)
📦 Writing CSV files... [CURRENT_ROWS] rows and counting...

Stage 4/7: Synthetic Data Generator • Running (1:00)
⚡ Almost done... generating faster than most ETL pipelines can load it.
```

### Completion Message:
```
Stage 4/7: Synthetic Data Generator • Complete (0:35) ✅
📊 Generated [TOTAL_ROWS] rows across [TABLE_COUNT] tables ([TOTAL_SIZE] MB)
🎯 Data volume: enough to demo, not enough to crash BigQuery
```

### Failure Message:
```
Stage 4/7: Synthetic Data Generator • Failed (1:30) ❌
💥 Data generation crashed. Either Faker ran out of fake names or we tried to generate too much.
```

---

## Stage 5: Infrastructure Agent (2-5 minutes)

### Running Messages (rotate every 4 seconds):
```
Stage 5/7: Infrastructure Agent • Running (0:15)
☁️ Creating BigQuery dataset... because "the data has to live somewhere™"

Stage 5/7: Infrastructure Agent • Running (0:30)
🏗️ Provisioning dataset: [DATASET_NAME]... with a naming scheme that actually makes sense.

Stage 5/7: Infrastructure Agent • Running (1:00)
📤 Uploading CSV files... crossing fingers that BigQuery likes our schema.

Stage 5/7: Infrastructure Agent • Running (1:30)
⏳ Loading table 1/[TABLE_COUNT]... [TABLE_NAME] ([ROW_COUNT] rows)

Stage 5/7: Infrastructure Agent • Running (2:00)
📊 Loading table 3/[TABLE_COUNT]... BigQuery is chewing through data like a hungry hippo.

Stage 5/7: Infrastructure Agent • Running (2:30)
🔄 Loading table 5/[TABLE_COUNT]... still faster than most enterprise data pipelines.

Stage 5/7: Infrastructure Agent • Running (3:00)
💾 Loading table 8/[TABLE_COUNT]... the boring middle part of data loading.

Stage 5/7: Infrastructure Agent • Running (3:30)
📈 Loading table 11/[TABLE_COUNT]... almost there, unless we hit a REPEATED field error (RIP Klick demo).

Stage 5/7: Infrastructure Agent • Running (4:00)
✨ Finalizing dataset... adding descriptions, metadata, and other things people will ignore.
```

### Completion Message:
```
Stage 5/7: Infrastructure Agent • Complete (3:12) ✅
🎉 BigQuery dataset provisioned: [FULL_DATASET_NAME]
📊 [TABLE_COUNT] tables • [TOTAL_ROWS] rows • [TOTAL_SIZE] MB
🌐 Console: https://console.cloud.google.com/bigquery?project=[PROJECT]&d=[DATASET]
```

### Failure Message:
```
Stage 5/7: Infrastructure Agent • Failed (4:30) ❌
🔥 BigQuery provisioning failed. Check logs for:
   • REPEATED field errors (most likely)
   • Permission issues (less likely)
   • Cosmic rays flipping bits (very unlikely but technically possible)
Error: [ACTUAL_ERROR_MESSAGE]
```

---

## Stage 6: CAPI Instruction Generator (2-5 minutes)

### Running Messages (rotate every 4 seconds):
```
Stage 6/7: CAPI Instruction Generator • Running (0:20)
📝 Claude 4.5 is writing YAML... the most verbose configuration format known to humanity.

Stage 6/7: CAPI Instruction Generator • Running (0:45)
🧠 Generating system instructions... teaching CAPI to be an expert in [INDUSTRY].

Stage 6/7: CAPI Instruction Generator • Running (1:15)
📋 Documenting table definitions... with descriptions longer than most READMEs.

Stage 6/7: CAPI Instruction Generator • Running (2:00)
🔗 Defining relationships... explaining to AI what "foreign key" means (again).

Stage 6/7: CAPI Instruction Generator • Running (2:30)
💡 Embedding golden queries... with SQL that actually works (we hope).

Stage 6/7: CAPI Instruction Generator • Running (3:00)
📖 Writing glossaries... because "GMV" means different things to different people.

Stage 6/7: CAPI Instruction Generator • Running (3:30)
⏰ Claude is still typing... this YAML file is going to be THICC (40KB+).

Stage 6/7: CAPI Instruction Generator • Running (4:00)
✍️ Finalizing YAML... current size: [FILE_SIZE] KB and growing...
```

### Completion Message:
```
Stage 6/7: CAPI Instruction Generator • Complete (3:45) ✅
📄 CAPI YAML generated: [FILE_SIZE] KB of pure configuration glory
🎯 Includes [TABLE_COUNT] tables, [RELATIONSHIP_COUNT] relationships, [QUERY_COUNT] golden queries
💾 File: [FILE_PATH]
```

### Failure Message:
```
Stage 6/7: CAPI Instruction Generator • Failed (5:00) ❌
📛 YAML generation failed. Claude either crashed or produced invalid YAML (JSON in disguise).
Error: [ACTUAL_ERROR_MESSAGE]
```

---

## Stage 7: Demo Validator (30-90 seconds)

### Running Messages (rotate every 4 seconds):
```
Stage 7/7: Demo Validator • Running (0:10)
🧪 Testing golden queries... let's see if our SQL actually works.

Stage 7/7: Demo Validator • Running (0:20)
✅ Validating query 1/[TOTAL]... "[QUERY_QUESTION]" (fingers crossed)

Stage 7/7: Demo Validator • Running (0:35)
✅ Validating query 5/[TOTAL]... this one has 3 CTEs and a window function (show off).

Stage 7/7: Demo Validator • Running (0:50)
⚡ Validating query 10/[TOTAL]... BigQuery is earning its paycheck today.

Stage 7/7: Demo Validator • Running (1:10)
📊 Checking data quality... making sure we didn't generate garbage (mostly).

Stage 7/7: Demo Validator • Running (1:20)
🔍 Final validation checks... because "it works on my machine™" isn't good enough.
```

### Completion Message:
```
Stage 7/7: Demo Validator • Complete (0:52) ✅
✅ Queries Validated: [SQL_COUNT]/[TOTAL_COUNT] (some queries don't have SQL yet - that's CAPI's job)
📊 Data Quality: PASSED
🎉 DEMO READY FOR PRESENTATION!
```

### Failure Message:
```
Stage 7/7: Demo Validator • Failed (1:30) ❌
⚠️ Validation failed. SQL might be broken, data might be corrupt, or BigQuery is having a bad day.
Error: [ACTUAL_ERROR_MESSAGE]
```

---

## Complete Pipeline Success (Total Time: 8-12 minutes)

```
🎊 PROVISIONING COMPLETE! 🎊

✅ All 7 stages completed successfully in [TOTAL_TIME]

📋 CUSTOMER: [CUSTOMER_NAME]
🏢 INDUSTRY: [INDUSTRY]
🗄️ DATASET: [DATASET_FULL_NAME]

📊 DATA STATISTICS:
   • Tables: [TABLE_COUNT]
   • Total Rows: [TOTAL_ROWS]
   • Total Size: [TOTAL_SIZE] MB

💡 GOLDEN QUERIES: [QUERY_COUNT] queries
   → SIMPLE: [SIMPLE_COUNT]
   → MEDIUM: [MEDIUM_COUNT]
   → COMPLEX: [COMPLEX_COUNT]
   → EXPERT: [EXPERT_COUNT]

📄 GENERATED ARTIFACTS:
   ✓ Demo Report: [REPORT_FILE]
   ✓ CAPI YAML: [YAML_FILE] ([FILE_SIZE] KB)
   ✓ Schema: /tmp/schema_[COMPANY].json
   ✓ Demo Story: /tmp/demo_story_[COMPANY].json

🚀 NEXT STEPS:
   1. Review demo report for complete narrative flow
   2. Create CAPI agent with generated YAML
   3. Test golden queries in CAPI interface
   4. Customize demo story for sales call
   5. Present to customer and watch their minds explode 🤯

🌐 BigQuery Console:
   https://console.cloud.google.com/bigquery?project=[PROJECT]&d=[DATASET]

🎬 Launch Chat Interface:
   [CHAT_URL]?website=[CUSTOMER_DOMAIN]

---

This demo was generated autonomously by 7 AI agents working in perfect harmony.
(Well, mostly perfect. Claude and Gemini only argued about schema design twice.)
```

---

## Pipeline Failure (Any Stage)

```
💥 PROVISIONING FAILED 💥

❌ Failed at Stage [STAGE_NUMBER]/7: [AGENT_NAME]

⏱️ Time to Failure: [ELAPSED_TIME]
🔧 Error: [ERROR_MESSAGE]

📊 PROGRESS BEFORE FAILURE:
   ✅ Stage 1: Research Agent
   ✅ Stage 2: Demo Story Agent
   ✅ Stage 3: Data Modeling Agent
   ❌ Stage 4: Synthetic Data Generator ← FAILED HERE
   ⏸️ Stage 5: Infrastructure Agent (not started)
   ⏸️ Stage 6: CAPI Instruction Generator (not started)
   ⏸️ Stage 7: Demo Validator (not started)

🔍 COMMON CAUSES:
   • REPEATED field in schema (BigQuery CSV loader can't handle arrays)
   • Invalid customer URL (website unreachable or bot-protected)
   • LLM rate limiting (Gemini or Claude API throttled)
   • BigQuery permissions issue (check IAM roles)
   • Cosmic rays (low probability but technically possible)

💡 SUGGESTED FIXES:
   1. Check error logs for specific failure reason
   2. Retry provisioning (might be transient issue)
   3. Review generated schema for REPEATED fields
   4. Verify GCP project permissions
   5. Sacrifice a rubber duck to the debugging gods

🔄 RETRY OPTIONS:
   • Retry from beginning (full pipeline)
   • Resume from failed stage (if artifacts exist)
   • Skip failed stage (dangerous but sometimes necessary)

📞 SUPPORT:
   If this error persists, check PROGRESS.md for known issues or cry into your keyboard.
```

---

## Implementation Notes for Frontend

### TypeScript Interface:
```typescript
interface ProvisioningProgress {
  stage: number; // 1-7
  agentName: string; // "Research Agent", etc.
  status: 'pending' | 'running' | 'complete' | 'failed';
  elapsedSeconds: number;
  message: string; // The witty message
  data?: {
    // Stage-specific data
    industry?: string;
    tableCount?: number;
    rowCount?: number;
    fileSize?: number;
    errorMessage?: string;
  };
}
```

### Message Rotation Logic:
```typescript
// Rotate through running messages every 4 seconds
// Show actual progress data in the message template
// Use template literals to inject real data:

const getMessage = (progress: ProvisioningProgress): string => {
  const templates = STAGE_MESSAGES[progress.stage][progress.status];
  const elapsed = formatTime(progress.elapsedSeconds);
  const template = templates[Math.floor(Math.random() * templates.length)];

  return template
    .replace('[ELAPSED]', elapsed)
    .replace('[TABLE_COUNT]', progress.data?.tableCount?.toString() || '?')
    .replace('[ROW_COUNT]', progress.data?.rowCount?.toLocaleString() || '?');
};
```

### Progress Display Component:
```tsx
<div className="provisioning-progress">
  <div className="stage-indicator">
    Stage {progress.stage}/7: {progress.agentName}
  </div>
  <div className="status-badge" data-status={progress.status}>
    {progress.status === 'running' && `Running (${formatTime(progress.elapsedSeconds)})`}
    {progress.status === 'complete' && '✅ Complete'}
    {progress.status === 'failed' && '❌ Failed'}
  </div>
  <div className="witty-message">
    {getMessage(progress)}
  </div>
</div>
```

---

## Message Style Guide

**Tone:** Technical + Self-aware + Optimistic (but realistic)

**Do:**
- Combine real data with humor
- Show actual progress (stage, time, counts)
- Acknowledge when things take time ("this is normal")
- Reference actual work being done
- Use emojis sparingly but effectively

**Don't:**
- Make jokes that undermine confidence
- Hide errors or pretend failures are okay
- Use humor that non-technical CEs won't understand
- Forget to show actual progress numbers
- Be too serious (this is still a demo tool)

**Examples of Good Messages:**
- "Stage 2/7: Demo Story Agent • Running (3:24) — Claude is still thinking... good narratives take time"
- "Stage 5/7: Infrastructure Agent • Complete (3:12) ✅ — 15 tables • 403,200 rows • 25.51 MB"

**Examples of Bad Messages:**
- "Doing stuff... please wait" (no data, not helpful)
- "LOL this is taking forever haha" (undermines confidence)
- "Quantum entangling the flux capacitor" (too obscure)

---

**END OF CE PROGRESS MESSAGES**

This system provides the perfect balance of **informative progress tracking** and **contextual humor** that matches the existing UI's 122 witty loading messages, while giving Customer Engineers real-time visibility into the autonomous provisioning pipeline.
