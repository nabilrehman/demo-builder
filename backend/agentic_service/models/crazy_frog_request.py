"""
Crazy Frog Mode - Advanced Provisioning Request Model

Allows Customer Engineers to provide rich context for highly customized demo generation.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class CrazyFrogProvisioningRequest(BaseModel):
    """
    Advanced provisioning request with rich CE context.

    The more context provided, the better the demo will be customized
    to the customer's specific use case and environment.
    """

    customer_url: str = Field(
        ...,
        description="Customer website URL for research and branding extraction"
    )

    use_case_context: str = Field(
        ...,
        min_length=50,
        description="Detailed use case context (min 50 chars, recommended 300+). "
                    "Include: business challenges, current analytics gaps, key stakeholders, "
                    "desired outcomes, specific scenarios to demonstrate."
    )

    # Optional hints for better customization
    industry_hint: Optional[str] = Field(
        None,
        description="Industry vertical (e.g., Healthcare, Financial Services, Retail, Manufacturing, SaaS)"
    )

    target_persona: Optional[str] = Field(
        None,
        description="Primary audience for the demo (e.g., CFO, CMO, CTO, Data Analyst, Business User)"
    )

    demo_complexity: Optional[str] = Field(
        None,
        description="Desired demo complexity level: Simple, Medium, Advanced"
    )

    special_focus: Optional[str] = Field(
        None,
        description="Special focus area (e.g., Revenue Analytics, Operational Efficiency, "
                    "Marketing Attribution, Customer Insights, Custom)"
    )

    integrations: Optional[str] = Field(
        None,
        description="Specific data sources or integrations to highlight (e.g., Salesforce, "
                    "Google Analytics, SAP, custom systems)"
    )

    avoid_topics: Optional[str] = Field(
        None,
        description="Topics or scenarios to avoid in the demo (competitive sensitivities, "
                    "data privacy concerns, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_url": "https://example-retailer.com",
                "use_case_context": "Leading e-commerce retailer with 500M+ annual revenue. "
                                   "Current pain: Marketing team uses static dashboards that require SQL expertise. "
                                   "They want to analyze: 1) Customer cohort behavior, 2) Product affinity analysis, "
                                   "3) Marketing attribution across channels, 4) Seasonal trends and forecasting. "
                                   "Key stakeholders: CMO (needs strategic insights), Marketing Analysts (need self-service). "
                                   "Success criteria: Enable non-technical users to ask complex analytical questions.",
                "industry_hint": "Retail & E-commerce",
                "target_persona": "CMO",
                "demo_complexity": "Advanced",
                "special_focus": "Marketing Attribution",
                "integrations": "Google Analytics, Salesforce Commerce Cloud",
                "avoid_topics": "competitor comparisons, pricing strategies"
            }
        }
