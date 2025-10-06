import { useQuery } from '@tanstack/react-query';

export interface GoldenQuery {
  id: string;
  sequence: number;
  complexity: 'SIMPLE' | 'MEDIUM' | 'COMPLEX' | 'EXPERT';
  question: string;
  sql: string;
  businessValue: string;
  // Validation status
  sql_tested?: boolean;
  sql_passed?: boolean;
  sql_error?: string;
  capi_tested?: boolean;
  capi_passed?: boolean;
  capi_error?: string;
}

export interface TableField {
  name: string;
  type: string;
  mode?: string;
  description?: string;
}

export interface TableSchema {
  name: string;
  description: string;
  rowCount: number;
  fieldCount: number;
  fields: TableField[];
}

export interface DemoAssets {
  jobId: string;
  customerUrl: string;
  demoTitle: string;
  executiveSummary: string;
  businessChallenges: string[];
  talkingTrack: string;
  goldenQueries: GoldenQuery[];
  schema: TableSchema[];
  metadata: {
    datasetId: string;
    datasetFullName: string;
    projectId: string;
    totalRows: number;
    totalStorageMB: number;
    generationTimestamp: string;
    totalTables: number;
  };
  provisionUrl: string;
  totalTime: string;
}

// Mock data based on Shopify example from SUMMARY.md
const MOCK_SHOPIFY_ASSETS: DemoAssets = {
  jobId: 'demo_shopify_20251004_1234',
  customerUrl: 'https://www.shopify.com',
  demoTitle: 'From Dashboard Chaos to Merchant Intelligence: How Shopify Empowers Every Team Member to Unlock Platform Insights',
  executiveSummary: 'Transform your merchant analytics from scattered dashboards to conversational intelligence. Enable every team member—from executives to support staff—to unlock platform insights through natural language queries.',
  businessChallenges: [
    'Merchant success teams struggle to identify at-risk merchants before churn occurs',
    'Platform economics hidden in complex multi-table queries requiring data teams',
    'Payment gateway optimization decisions based on incomplete merchant cohort analysis',
    'App ecosystem revenue opportunities buried in installation and usage patterns',
    'Customer lifetime value analysis requires joining 8+ tables manually'
  ],
  talkingTrack: 'Start by showing executive-level GMV trends, then drill into merchant cohorts. Demonstrate how support can identify at-risk merchants instantly. Close with the payment gateway ROI analysis that shows $247M opportunity.',
  goldenQueries: [
    {
      id: 'q1',
      sequence: 1,
      complexity: 'SIMPLE',
      question: 'What is our total GMV (Gross Merchandise Value) this month?',
      sql: 'SELECT SUM(total_amount) as total_gmv FROM orders WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)',
      businessValue: 'Quick health check for platform performance. Essential for daily standups and executive dashboards.'
    },
    {
      id: 'q2',
      sequence: 2,
      complexity: 'SIMPLE',
      question: 'How many active merchants do we have?',
      sql: 'SELECT COUNT(DISTINCT merchant_id) as active_merchants FROM merchants WHERE status = "active"',
      businessValue: 'Core KPI for platform growth. Sales teams use this for pipeline planning.'
    },
    {
      id: 'q3',
      sequence: 3,
      complexity: 'MEDIUM',
      question: 'Show me GMV by payment gateway for the last quarter',
      sql: 'SELECT p.gateway_name, SUM(o.total_amount) as gmv FROM orders o JOIN payments p ON o.payment_id = p.payment_id WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) GROUP BY p.gateway_name ORDER BY gmv DESC',
      businessValue: 'Identifies payment processing opportunities. Shopify Payments adoption drives take rate expansion.'
    },
    {
      id: 'q4',
      sequence: 4,
      complexity: 'MEDIUM',
      question: 'Which merchants have the highest customer retention rate?',
      sql: 'SELECT m.merchant_name, COUNT(DISTINCT c.customer_id) as total_customers, COUNT(DISTINCT CASE WHEN o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) THEN c.customer_id END) as recent_customers FROM merchants m JOIN orders o ON m.merchant_id = o.merchant_id JOIN customers c ON o.customer_id = c.customer_id GROUP BY m.merchant_id, m.merchant_name HAVING total_customers > 100 ORDER BY (recent_customers / total_customers) DESC LIMIT 20',
      businessValue: 'Success stories for case studies. These merchants become advocates and referral sources.'
    },
    {
      id: 'q5',
      sequence: 5,
      complexity: 'MEDIUM',
      question: 'What are the top 10 most installed apps across all stores?',
      sql: 'SELECT a.app_name, COUNT(DISTINCT sai.store_id) as install_count, AVG(a.monthly_price) as avg_price FROM apps a JOIN store_app_installs sai ON a.app_id = sai.app_id WHERE sai.status = "active" GROUP BY a.app_id, a.app_name ORDER BY install_count DESC LIMIT 10',
      businessValue: 'App ecosystem insights drive partnership strategy and merchant success playbooks.'
    },
    {
      id: 'q6',
      sequence: 6,
      complexity: 'COMPLEX',
      question: 'Compare average order value for merchants on Plus vs Standard plans',
      sql: 'SELECT m.subscription_tier, COUNT(DISTINCT o.order_id) as total_orders, AVG(o.total_amount) as avg_order_value, SUM(o.total_amount) as total_gmv FROM merchants m JOIN orders o ON m.merchant_id = o.merchant_id WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY) GROUP BY m.subscription_tier ORDER BY avg_order_value DESC',
      businessValue: 'Quantifies Plus tier value prop. Shows Plus merchants drive 2.3x higher AOV, justifying upgrade investment.'
    },
    {
      id: 'q7',
      sequence: 7,
      complexity: 'COMPLEX',
      question: 'Identify merchants at risk of churning based on declining order volume',
      sql: 'WITH monthly_orders AS (SELECT merchant_id, DATE_TRUNC(order_date, MONTH) as month, COUNT(*) as order_count FROM orders WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY) GROUP BY merchant_id, month) SELECT m.merchant_name, m.merchant_id, mo1.order_count as last_month_orders, mo2.order_count as two_months_ago, mo3.order_count as three_months_ago, ((mo1.order_count - mo3.order_count) / mo3.order_count * 100) as decline_pct FROM merchants m JOIN monthly_orders mo1 ON m.merchant_id = mo1.merchant_id AND mo1.month = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH) JOIN monthly_orders mo2 ON m.merchant_id = mo2.merchant_id AND mo2.month = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 2 MONTH), MONTH) JOIN monthly_orders mo3 ON m.merchant_id = mo3.merchant_id AND mo3.month = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH), MONTH) WHERE mo1.order_count < mo3.order_count ORDER BY decline_pct ASC LIMIT 50',
      businessValue: 'Proactive churn prevention. CS can intervene before merchants leave, protecting $2-5M ARR monthly.'
    },
    {
      id: 'q8',
      sequence: 8,
      complexity: 'COMPLEX',
      question: 'Show me the lifetime value of customers by merchant cohort (signup month)',
      sql: 'SELECT DATE_TRUNC(m.created_at, MONTH) as cohort_month, COUNT(DISTINCT m.merchant_id) as merchants_in_cohort, COUNT(DISTINCT o.order_id) as total_orders, SUM(o.total_amount) as total_gmv, AVG(o.total_amount) as avg_order_value FROM merchants m JOIN orders o ON m.merchant_id = o.merchant_id GROUP BY cohort_month ORDER BY cohort_month DESC LIMIT 24',
      businessValue: 'Cohort retention analysis drives CAC/LTV optimization. Shows merchant value trajectory over time.'
    },
    {
      id: 'q9',
      sequence: 9,
      complexity: 'EXPERT',
      question: 'Compare customer lifetime value and order frequency for merchants using Shopify Payments versus third-party gateways, but only for merchants who have been active for at least 12 months and process more than 100 orders per month',
      sql: 'WITH merchant_stats AS (SELECT m.merchant_id, m.merchant_name, CASE WHEN p.gateway_name = "Shopify Payments" THEN "Shopify Payments" ELSE "Third-Party" END as gateway_type, COUNT(DISTINCT o.order_id) as total_orders, COUNT(DISTINCT c.customer_id) as unique_customers, SUM(o.total_amount) as total_gmv, AVG(o.total_amount) as avg_order_value FROM merchants m JOIN orders o ON m.merchant_id = o.merchant_id JOIN payments p ON o.payment_id = p.payment_id JOIN customers c ON o.customer_id = c.customer_id WHERE DATE_DIFF(CURRENT_DATE(), m.created_at, MONTH) >= 12 GROUP BY m.merchant_id, m.merchant_name, gateway_type HAVING total_orders > 100) SELECT gateway_type, COUNT(DISTINCT merchant_id) as merchant_count, AVG(total_orders) as avg_orders_per_merchant, AVG(unique_customers) as avg_customers_per_merchant, AVG(total_gmv / unique_customers) as avg_customer_ltv, AVG(total_orders / unique_customers) as avg_order_frequency FROM merchant_stats GROUP BY gateway_type',
      businessValue: 'Critical payment strategy insight: Shopify Payments merchants have 2.3x higher customer LTV ($487 vs $211). Drives $247M payment volume migration opportunity.'
    },
    {
      id: 'q10',
      sequence: 10,
      complexity: 'EXPERT',
      question: 'What is the correlation between number of installed apps and merchant GMV growth rate?',
      sql: 'WITH merchant_app_counts AS (SELECT m.merchant_id, COUNT(DISTINCT sai.app_id) as app_count FROM merchants m LEFT JOIN store_app_installs sai ON m.merchant_id = sai.store_id WHERE sai.status = "active" GROUP BY m.merchant_id), gmv_growth AS (SELECT o.merchant_id, SUM(CASE WHEN o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) THEN o.total_amount ELSE 0 END) as recent_gmv, SUM(CASE WHEN o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY) AND o.order_date < DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) THEN o.total_amount ELSE 0 END) as previous_gmv FROM orders o GROUP BY o.merchant_id) SELECT CASE WHEN mac.app_count = 0 THEN "0 apps" WHEN mac.app_count BETWEEN 1 AND 3 THEN "1-3 apps" WHEN mac.app_count BETWEEN 4 AND 7 THEN "4-7 apps" ELSE "8+ apps" END as app_tier, COUNT(DISTINCT mac.merchant_id) as merchant_count, AVG((gg.recent_gmv - gg.previous_gmv) / NULLIF(gg.previous_gmv, 0) * 100) as avg_gmv_growth_pct FROM merchant_app_counts mac JOIN gmv_growth gg ON mac.merchant_id = gg.merchant_id WHERE gg.previous_gmv > 0 GROUP BY app_tier ORDER BY avg_gmv_growth_pct DESC',
      businessValue: 'App ecosystem ROI proof: merchants with 8+ apps grow 3.2x faster. Informs app marketplace strategy and $100M+ ecosystem expansion opportunity.'
    },
    {
      id: 'q11',
      sequence: 11,
      complexity: 'EXPERT',
      question: 'Identify the most valuable customer segments by combining product category preferences with order frequency and average spend',
      sql: 'WITH customer_segments AS (SELECT c.customer_id, COUNT(DISTINCT o.order_id) as order_count, AVG(o.total_amount) as avg_spend, STRING_AGG(DISTINCT pc.category_name, ", " ORDER BY pc.category_name) as preferred_categories FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_line_items oli ON o.order_id = oli.order_id JOIN products p ON oli.product_id = p.product_id JOIN product_categories pc ON p.category_id = pc.category_id WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY) GROUP BY c.customer_id) SELECT preferred_categories, COUNT(DISTINCT customer_id) as segment_size, AVG(order_count) as avg_orders_per_customer, AVG(avg_spend) as avg_spend_per_order, AVG(order_count * avg_spend) as avg_customer_ltv FROM customer_segments WHERE order_count >= 3 GROUP BY preferred_categories HAVING segment_size > 100 ORDER BY avg_customer_ltv DESC LIMIT 20',
      businessValue: 'Precision marketing intelligence. Enables targeted campaigns with 2-3x higher conversion than broad-based promotions.'
    },
    {
      id: 'q12',
      sequence: 12,
      complexity: 'EXPERT',
      question: 'Calculate the payback period for merchants by subscription tier, factoring in payment processing fees and transaction volume',
      sql: 'WITH merchant_economics AS (SELECT m.merchant_id, m.merchant_name, m.subscription_tier, msh.monthly_subscription_cost, COUNT(DISTINCT o.order_id) as total_orders, SUM(o.total_amount) as total_gmv, AVG(CASE WHEN p.gateway_name = "Shopify Payments" THEN 0.029 ELSE 0.015 END) as avg_transaction_fee_pct FROM merchants m JOIN merchant_subscription_history msh ON m.merchant_id = msh.merchant_id JOIN orders o ON m.merchant_id = o.merchant_id JOIN payments p ON o.payment_id = p.payment_id WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY) AND msh.end_date IS NULL GROUP BY m.merchant_id, m.merchant_name, m.subscription_tier, msh.monthly_subscription_cost) SELECT subscription_tier, COUNT(DISTINCT merchant_id) as merchant_count, AVG(monthly_subscription_cost) as avg_subscription_cost, AVG(total_gmv * avg_transaction_fee_pct) as avg_annual_transaction_revenue, AVG(monthly_subscription_cost * 12) as avg_annual_subscription_revenue, AVG(monthly_subscription_cost / (total_gmv * avg_transaction_fee_pct / 12)) as avg_payback_months FROM merchant_economics WHERE total_gmv > 0 GROUP BY subscription_tier ORDER BY avg_payback_months ASC',
      businessValue: 'Unit economics clarity: Plus tier pays back in 3.2 months vs 8.7 months for Standard. Validates pricing strategy and informs sales incentives.'
    }
  ],
  schema: [
    {
      name: 'merchants',
      description: 'Core merchant accounts on the Shopify platform',
      rowCount: 25000,
      fieldCount: 8,
      fields: [
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique merchant identifier' },
        { name: 'merchant_name', type: 'STRING', mode: 'REQUIRED', description: 'Business name' },
        { name: 'email', type: 'STRING', description: 'Primary contact email' },
        { name: 'status', type: 'STRING', description: 'Account status (active, paused, closed)' },
        { name: 'subscription_tier', type: 'STRING', description: 'Plan level (Basic, Standard, Advanced, Plus)' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Account creation date' },
        { name: 'industry', type: 'STRING', description: 'Business industry vertical' },
        { name: 'country', type: 'STRING', description: 'Primary business country' }
      ]
    },
    {
      name: 'stores',
      description: 'Individual storefronts (merchants can have multiple stores)',
      rowCount: 28000,
      fieldCount: 7,
      fields: [
        { name: 'store_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique store identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to merchants' },
        { name: 'store_name', type: 'STRING', description: 'Store display name' },
        { name: 'domain', type: 'STRING', description: 'Store domain name' },
        { name: 'theme_name', type: 'STRING', description: 'Active Shopify theme' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Store launch date' },
        { name: 'is_active', type: 'BOOLEAN', description: 'Store active status' }
      ]
    },
    {
      name: 'orders',
      description: 'All customer orders across all merchants',
      rowCount: 180000,
      fieldCount: 9,
      fields: [
        { name: 'order_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique order identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to merchants' },
        { name: 'customer_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to customers' },
        { name: 'payment_id', type: 'STRING', description: 'Foreign key to payments' },
        { name: 'order_date', type: 'TIMESTAMP', description: 'Order creation timestamp' },
        { name: 'total_amount', type: 'FLOAT', description: 'Order total in USD' },
        { name: 'status', type: 'STRING', description: 'Order status (pending, completed, refunded)' },
        { name: 'channel_id', type: 'STRING', description: 'Sales channel (online, POS, mobile)' },
        { name: 'fulfillment_status', type: 'STRING', description: 'Shipping status' }
      ]
    },
    {
      name: 'payments',
      description: 'Payment transaction records',
      rowCount: 180000,
      fieldCount: 6,
      fields: [
        { name: 'payment_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique payment identifier' },
        { name: 'gateway_name', type: 'STRING', description: 'Payment processor (Shopify Payments, Stripe, PayPal, etc)' },
        { name: 'amount', type: 'FLOAT', description: 'Payment amount' },
        { name: 'currency', type: 'STRING', description: 'Payment currency code' },
        { name: 'status', type: 'STRING', description: 'Payment status (pending, authorized, captured, failed)' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Payment timestamp' }
      ]
    },
    {
      name: 'customers',
      description: 'End customers who purchase from merchants',
      rowCount: 95000,
      fieldCount: 7,
      fields: [
        { name: 'customer_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique customer identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Associated merchant' },
        { name: 'email', type: 'STRING', description: 'Customer email' },
        { name: 'first_name', type: 'STRING', description: 'Customer first name' },
        { name: 'last_name', type: 'STRING', description: 'Customer last name' },
        { name: 'country', type: 'STRING', description: 'Customer country' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Customer account creation date' }
      ]
    },
    {
      name: 'apps',
      description: 'Available apps in the Shopify App Store',
      rowCount: 450,
      fieldCount: 8,
      fields: [
        { name: 'app_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique app identifier' },
        { name: 'app_name', type: 'STRING', description: 'App display name' },
        { name: 'category', type: 'STRING', description: 'App category (marketing, inventory, shipping, etc)' },
        { name: 'developer_name', type: 'STRING', description: 'App developer' },
        { name: 'rating', type: 'FLOAT', description: 'Average user rating (1-5)' },
        { name: 'review_count', type: 'INTEGER', description: 'Total number of reviews' },
        { name: 'monthly_price', type: 'FLOAT', description: 'Monthly subscription price' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'App listing date' }
      ]
    },
    {
      name: 'store_app_installs',
      description: 'App installations per store',
      rowCount: 62000,
      fieldCount: 5,
      fields: [
        { name: 'install_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique installation identifier' },
        { name: 'store_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to stores' },
        { name: 'app_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to apps' },
        { name: 'installed_at', type: 'TIMESTAMP', description: 'Installation timestamp' },
        { name: 'status', type: 'STRING', description: 'Installation status (active, uninstalled)' }
      ]
    },
    {
      name: 'channels',
      description: 'Sales channels available to merchants',
      rowCount: 8,
      fieldCount: 4,
      fields: [
        { name: 'channel_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique channel identifier' },
        { name: 'channel_name', type: 'STRING', description: 'Channel name (Online Store, POS, Mobile, Facebook, Instagram, etc)' },
        { name: 'channel_type', type: 'STRING', description: 'Channel type category' },
        { name: 'is_active', type: 'BOOLEAN', description: 'Channel availability' }
      ]
    },
    {
      name: 'product_categories',
      description: 'Product taxonomy for classification',
      rowCount: 180,
      fieldCount: 4,
      fields: [
        { name: 'category_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique category identifier' },
        { name: 'category_name', type: 'STRING', description: 'Category display name' },
        { name: 'parent_category_id', type: 'STRING', description: 'Parent category for hierarchy' },
        { name: 'description', type: 'STRING', description: 'Category description' }
      ]
    },
    {
      name: 'products',
      description: 'Products sold by merchants',
      rowCount: 85000,
      fieldCount: 8,
      fields: [
        { name: 'product_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique product identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to merchants' },
        { name: 'product_name', type: 'STRING', description: 'Product title' },
        { name: 'category_id', type: 'STRING', description: 'Foreign key to product_categories' },
        { name: 'price', type: 'FLOAT', description: 'Product price' },
        { name: 'inventory_quantity', type: 'INTEGER', description: 'Current inventory count' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Product creation date' },
        { name: 'is_active', type: 'BOOLEAN', description: 'Product availability status' }
      ]
    },
    {
      name: 'order_line_items',
      description: 'Individual items within orders',
      rowCount: 340000,
      fieldCount: 6,
      fields: [
        { name: 'line_item_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique line item identifier' },
        { name: 'order_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to orders' },
        { name: 'product_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to products' },
        { name: 'quantity', type: 'INTEGER', description: 'Quantity ordered' },
        { name: 'unit_price', type: 'FLOAT', description: 'Price per unit' },
        { name: 'total_price', type: 'FLOAT', description: 'Line item total (quantity * unit_price)' }
      ]
    },
    {
      name: 'merchant_subscription_history',
      description: 'Merchant plan change history',
      rowCount: 32000,
      fieldCount: 6,
      fields: [
        { name: 'subscription_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique subscription record identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to merchants' },
        { name: 'subscription_tier', type: 'STRING', description: 'Plan level' },
        { name: 'monthly_subscription_cost', type: 'FLOAT', description: 'Monthly plan cost' },
        { name: 'start_date', type: 'TIMESTAMP', description: 'Subscription start date' },
        { name: 'end_date', type: 'TIMESTAMP', description: 'Subscription end date (NULL if current)' }
      ]
    },
    {
      name: 'merchant_events',
      description: 'Key merchant lifecycle events',
      rowCount: 48000,
      fieldCount: 5,
      fields: [
        { name: 'event_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique event identifier' },
        { name: 'merchant_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to merchants' },
        { name: 'event_type', type: 'STRING', description: 'Event type (signup, upgrade, downgrade, churn, reactivation)' },
        { name: 'event_timestamp', type: 'TIMESTAMP', description: 'Event occurrence time' },
        { name: 'event_metadata', type: 'STRING', description: 'Additional event context (JSON)' }
      ]
    },
    {
      name: 'payment_methods',
      description: 'Customer payment methods on file',
      rowCount: 112000,
      fieldCount: 6,
      fields: [
        { name: 'payment_method_id', type: 'STRING', mode: 'REQUIRED', description: 'Unique payment method identifier' },
        { name: 'customer_id', type: 'STRING', mode: 'REQUIRED', description: 'Foreign key to customers' },
        { name: 'method_type', type: 'STRING', description: 'Payment method type (card, bank_account, wallet)' },
        { name: 'card_brand', type: 'STRING', description: 'Card brand if applicable (Visa, Mastercard, Amex)' },
        { name: 'is_default', type: 'BOOLEAN', description: 'Default payment method flag' },
        { name: 'created_at', type: 'TIMESTAMP', description: 'Payment method addition date' }
      ]
    }
  ],
  metadata: {
    datasetId: 'shopify_capi_demo_20251004',
    datasetFullName: 'bq-demos-469816.shopify_capi_demo_20251004',
    projectId: 'bq-demos-469816',
    totalRows: 403200,
    totalStorageMB: 25.51,
    generationTimestamp: '2025-10-04T14:32:18Z',
    totalTables: 15
  },
  provisionUrl: 'https://chat.demo.com?website=shopify.com&dataset=shopify_capi_demo_20251004',
  totalTime: '11m 23s'
};

export const useDemoAssets = (jobId?: string) => {
  return useQuery<DemoAssets>({
    queryKey: ['demo-assets', jobId],
    queryFn: async () => {
      if (!jobId) {
        throw new Error('Job ID is required');
      }

      const response = await fetch(`/api/provision/assets/${jobId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch demo assets: ${response.statusText}`);
      }

      const data = await response.json();

      // Transform backend response to match DemoAssets interface
      return {
        jobId: data.job_id,
        customerUrl: data.customer_url,
        demoTitle: data.demo_title || 'Demo Title',
        executiveSummary: data.executive_summary || '',
        businessChallenges: data.business_challenges || [],
        talkingTrack: data.talking_track || '',
        goldenQueries: data.golden_queries || [],
        schema: data.schema || [],
        metadata: data.metadata || {
          datasetId: '',
          datasetFullName: '',
          projectId: '',
          totalRows: 0,
          totalStorageMB: 0,
          generationTimestamp: '',
          totalTables: 0
        },
        // CRITICAL FIX: Point to root (nice UI) with dataset/agent/website params
        provisionUrl: `/?dataset_id=${data.metadata?.datasetId || ''}&agent_id=${data.metadata?.agentId || 'default'}&website=${encodeURIComponent(data.customerUrl || '')}`,
        totalTime: data.total_time || 'N/A'
      } as DemoAssets;
    },
    enabled: !!jobId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
