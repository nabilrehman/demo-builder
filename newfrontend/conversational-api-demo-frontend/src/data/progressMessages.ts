// Progress messages extracted from CE-PROGRESS-MESSAGES.md
// Provides witty, contextual messages for the 7-stage provisioning pipeline

export type StageStatus = 'pending' | 'running' | 'complete' | 'failed';

export interface StageMessage {
  icon: string;
  message: string;
}

export interface StageInfo {
  number: number;
  name: string;
  estimatedDuration: string;
}

// 7 stages of the provisioning pipeline
export const STAGES: StageInfo[] = [
  { number: 1, name: 'Research Agent', estimatedDuration: '15-30s' },
  { number: 2, name: 'Demo Story Agent', estimatedDuration: '4-7m' },
  { number: 3, name: 'Data Modeling Agent', estimatedDuration: '30-60s' },
  { number: 4, name: 'Synthetic Data Generator', estimatedDuration: '30-90s' },
  { number: 5, name: 'Infrastructure Agent', estimatedDuration: '2-5m' },
  { number: 6, name: 'CAPI Instruction Generator', estimatedDuration: '2-5m' },
  { number: 7, name: 'Demo Validator', estimatedDuration: '30-90s' },
];

// Running messages for each stage (rotate every 4 seconds)
export const RUNNING_MESSAGES: Record<number, StageMessage[]> = {
  1: [
    { icon: '📊', message: 'Scraping customer website... attempting to understand their business better than they do.' },
    { icon: '🔍', message: 'Analyzing homepage... if their "About Us" page says "we\'re passionate about synergy," we might be in trouble.' },
    { icon: '🧠', message: 'Claude 4.5 is reading their mission statement... and trying not to laugh at the buzzwords.' },
    { icon: '🌐', message: 'Extracting business domain... categorizing as "definitely uses spreadsheets."' },
    { icon: '✨', message: 'Identifying use cases... spoiler: they need data analytics (they just don\'t know it yet).' },
  ],
  2: [
    { icon: '✍️', message: 'Claude 4.5 is channeling its inner Principal Architect... this is where the magic happens.' },
    { icon: '🎭', message: 'Creating executive-level narrative... because "show me a dashboard" isn\'t a compelling demo.' },
    { icon: '💡', message: 'Generating golden queries... the kind that make CTOs say "wait, we can do THAT?"' },
    { icon: '📖', message: 'Writing demo script... with just enough technical depth to sound smart without being scary.' },
    { icon: '🧩', message: 'Designing business challenges... that coincidentally align perfectly with our product capabilities.' },
    { icon: '🎯', message: 'Claude is still thinking... this is strategic storytelling, not Mad Libs.' },
    { icon: '⏰', message: 'Almost there... good narratives take time (and 128K context windows).' },
  ],
  3: [
    { icon: '🗄️', message: 'Gemini is designing schema... thinking in tables, not entities.' },
    { icon: '🔗', message: 'Creating relationships... one-to-many, many-to-many, and "oh god why is this so complicated?"' },
    { icon: '📐', message: 'Optimizing for story-driven queries... because demo data should actually answer the golden queries.' },
    { icon: '🧮', message: 'Calculating table sizes... aiming for "realistic" not "production nightmare."' },
    { icon: '⚙️', message: 'Finalizing schema... and praying Gemini doesn\'t use REPEATED fields (we have a history).' },
  ],
  4: [
    { icon: '🎲', message: 'Generating fake data... that\'s more realistic than half our customers\' production data.' },
    { icon: '👥', message: 'Creating synthetic customers... with names like "Jennifer Martinez" and emails like "jennifer.martinez.1847@example.com"' },
    { icon: '💰', message: 'Generating transaction data... with suspiciously round numbers and perfect distributions.' },
    { icon: '📈', message: 'Faker is working overtime... producing data that "looks real enough™"' },
    { icon: '📦', message: 'Writing CSV files... rows and counting...' },
    { icon: '⚡', message: 'Almost done... generating faster than most ETL pipelines can load it.' },
  ],
  5: [
    { icon: '☁️', message: 'Creating BigQuery dataset... because "the data has to live somewhere™"' },
    { icon: '🏗️', message: 'Provisioning dataset... with a naming scheme that actually makes sense.' },
    { icon: '📤', message: 'Uploading CSV files... crossing fingers that BigQuery likes our schema.' },
    { icon: '⏳', message: 'Loading tables... BigQuery is working hard.' },
    { icon: '📊', message: 'Loading tables... BigQuery is chewing through data like a hungry hippo.' },
    { icon: '🔄', message: 'Loading tables... still faster than most enterprise data pipelines.' },
    { icon: '💾', message: 'Loading tables... the boring middle part of data loading.' },
    { icon: '📈', message: 'Loading tables... almost there, unless we hit a REPEATED field error (RIP Klick demo).' },
    { icon: '✨', message: 'Finalizing dataset... adding descriptions, metadata, and other things people will ignore.' },
  ],
  6: [
    { icon: '📝', message: 'Claude 4.5 is writing YAML... the most verbose configuration format known to humanity.' },
    { icon: '🧠', message: 'Generating system instructions... teaching CAPI to be an expert in this industry.' },
    { icon: '📋', message: 'Documenting table definitions... with descriptions longer than most READMEs.' },
    { icon: '🔗', message: 'Defining relationships... explaining to AI what "foreign key" means (again).' },
    { icon: '💡', message: 'Embedding golden queries... with SQL that actually works (we hope).' },
    { icon: '📖', message: 'Writing glossaries... because "GMV" means different things to different people.' },
    { icon: '⏰', message: 'Claude is still typing... this YAML file is going to be THICC (40KB+).' },
    { icon: '✍️', message: 'Finalizing YAML... current size growing...' },
  ],
  7: [
    { icon: '🧪', message: 'Testing golden queries... let\'s see if our SQL actually works.' },
    { icon: '✅', message: 'Validating queries... (fingers crossed)' },
    { icon: '✅', message: 'Validating queries... this one has 3 CTEs and a window function (show off).' },
    { icon: '⚡', message: 'Validating queries... BigQuery is earning its paycheck today.' },
    { icon: '📊', message: 'Checking data quality... making sure we didn\'t generate garbage (mostly).' },
    { icon: '🔍', message: 'Final validation checks... because "it works on my machine™" isn\'t good enough.' },
  ],
};

// Completion messages for each stage
export const COMPLETION_MESSAGES: Record<number, (data?: any) => string> = {
  1: (data) => `🎯 Industry identified: ${data?.industry || 'Unknown'}. Claude is already planning the perfect sales pitch.`,
  2: (data) => `🎉 Demo Title: "${data?.demoTitle || 'Untitled Demo'}"\n💎 Golden Queries: ${data?.queryCount || 0} queries ranging from "executive dashboard" to "holy sh*t that's complex"`,
  3: (data) => `📊 Schema designed: ${data?.tableCount || 0} tables with ${data?.totalFields || 0} fields\n🎯 Optimized for ${data?.queryCount || 0} golden queries`,
  4: (data) => `📊 Generated ${data?.totalRows?.toLocaleString() || 0} rows across ${data?.tableCount || 0} tables (${data?.totalSize || 0} MB)\n🎯 Data volume: enough to demo, not enough to crash BigQuery`,
  5: (data) => `🎉 BigQuery dataset provisioned: ${data?.datasetName || 'Unknown'}\n📊 ${data?.tableCount || 0} tables • ${data?.totalRows?.toLocaleString() || 0} rows • ${data?.totalSize || 0} MB\n🌐 Console: ${data?.consoleUrl || ''}`,
  6: (data) => `📄 CAPI YAML generated: ${data?.fileSize || 0} KB of pure configuration glory\n🎯 Includes ${data?.tableCount || 0} tables, ${data?.relationshipCount || 0} relationships, ${data?.queryCount || 0} golden queries\n💾 File: ${data?.filePath || ''}`,
  7: (data) => `✅ Queries Validated: ${data?.validatedCount || 0}/${data?.totalCount || 0} (some queries don't have SQL yet - that's CAPI's job)\n📊 Data Quality: PASSED\n🎉 DEMO READY FOR PRESENTATION!`,
};

// Failure messages for each stage
export const FAILURE_MESSAGES: Record<number, string> = {
  1: '🚨 Website scraping failed. Either they have aggressive bot detection or their site is just that broken.',
  2: '💀 Claude couldn\'t generate a compelling story. The industry might be too niche, or we\'ve found the one business case CAPI can\'t solve.',
  3: '🛑 Schema generation failed. Gemini might have suggested REPEATED fields again. We\'ll never learn.',
  4: '💥 Data generation crashed. Either Faker ran out of fake names or we tried to generate too much.',
  5: '🔥 BigQuery provisioning failed. Check logs for:\n   • REPEATED field errors (most likely)\n   • Permission issues (less likely)\n   • Cosmic rays flipping bits (very unlikely but technically possible)',
  6: '📛 YAML generation failed. Claude either crashed or produced invalid YAML (JSON in disguise).',
  7: '⚠️ Validation failed. SQL might be broken, data might be corrupt, or BigQuery is having a bad day.',
};

// Pending message
export const PENDING_MESSAGE = '⏸️ Waiting to start...';

// Get rotating running message based on elapsed time
export const getRunningMessage = (stage: number, elapsedSeconds: number): StageMessage => {
  const messages = RUNNING_MESSAGES[stage] || [];
  if (messages.length === 0) {
    return { icon: '⏳', message: 'Processing...' };
  }

  // Rotate every 8 seconds
  const index = Math.floor(elapsedSeconds / 8) % messages.length;
  return messages[index];
};

// Format elapsed time
export const formatElapsedTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;

  if (mins === 0) {
    return `0:${secs.toString().padStart(2, '0')}`;
  }

  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
