"""Idempotent Relanto service-company seed data."""

from sqlalchemy.orm import Session

from app.models.service_intelligence import (
    ServiceCompany,
    ServiceOpportunity,
    ServiceOpportunityPracticeMapping,
    ServicePastDeal,
    ServicePractice,
    ServiceTechnology,
)


RELANTO_PRACTICES = [
    {
        "practice_name": "Data & AI",
        "practice_code": "PRA_DATA_AI",
        "practice_category": "AI",
        "description": "Enterprise AI, data engineering, GenAI systems, analytics modernization, AI orchestration, and decision intelligence.",
        "maturity_level": "Advanced",
        "strategic_priority": "Critical",
        "delivery_strength": 10,
        "bench_strength": 180,
        "sme_count": 35,
        "utilization_percentage": 72.5,
        "growth_priority": True,
    },
    {
        "practice_name": "AI First Lab",
        "practice_code": "PRA_AI_LAB",
        "practice_category": "Innovation",
        "description": "Agentic AI, GenAI experimentation, AI accelerators, AI-first enterprise modernization, advanced innovation initiatives.",
        "maturity_level": "Advanced",
        "strategic_priority": "Critical",
        "delivery_strength": 9,
        "bench_strength": 60,
        "sme_count": 18,
        "utilization_percentage": 65.0,
        "growth_priority": True,
    },
    {
        "practice_name": "Digital Transformation",
        "practice_code": "PRA_DIGITAL",
        "practice_category": "Engineering",
        "description": "Frontend engineering, backend engineering, mobile engineering, QA automation, DevOps, cloud-native modernization, enterprise workflow engineering.",
        "maturity_level": "Advanced",
        "strategic_priority": "Critical",
        "delivery_strength": 10,
        "bench_strength": 350,
        "sme_count": 45,
        "utilization_percentage": 78.0,
        "growth_priority": True,
    },
    {
        "practice_name": "Salesforce",
        "practice_code": "PRA_SALESFORCE",
        "practice_category": "Enterprise Platforms",
        "description": "Salesforce optimization, CRM modernization, RevOps transformation, automation, customer workflows.",
        "maturity_level": "Advanced",
        "strategic_priority": "High",
        "delivery_strength": 9,
        "bench_strength": 120,
        "sme_count": 22,
        "utilization_percentage": 74.0,
        "growth_priority": True,
    },
    {
        "practice_name": "Planning",
        "practice_code": "PRA_PLANNING",
        "practice_category": "Business Transformation",
        "description": "Enterprise planning transformation, forecasting, analytics modernization, operational intelligence, planning automation.",
        "maturity_level": "Advanced",
        "strategic_priority": "High",
        "delivery_strength": 8,
        "bench_strength": 80,
        "sme_count": 14,
        "utilization_percentage": 69.0,
        "growth_priority": True,
    },
]

RELANTO_TECHNOLOGIES = [
    ("AWS", "Cloud", "Amazon", "Advanced", 10, 10),
    ("Azure", "Cloud", "Microsoft", "Advanced", 10, 10),
    ("Google Cloud", "Cloud", "Google", "Advanced", 9, 9),
    ("Kubernetes", "DevOps", "CNCF", "Advanced", 10, 10),
    ("Terraform", "Infrastructure", "HashiCorp", "Advanced", 9, 9),
    ("Snowflake", "Data", "Snowflake", "Advanced", 9, 9),
    ("Databricks", "Data", "Databricks", "Advanced", 10, 10),
    ("OpenAI", "AI", "OpenAI", "Advanced", 10, 10),
    ("LangChain", "AI", "LangChain", "Intermediate", 9, 9),
    ("Vector Databases", "AI", "Multiple", "Intermediate", 10, 10),
    ("Salesforce", "CRM", "Salesforce", "Advanced", 10, 10),
    ("React", "Frontend", "Meta", "Advanced", 9, 8),
    ("Next.js", "Frontend", "Vercel", "Advanced", 9, 9),
    ("Python", "Backend", "Python Foundation", "Advanced", 10, 10),
    ("Node.js", "Backend", "OpenJS", "Advanced", 9, 9),
    ("PostgreSQL", "Database", "PostgreSQL", "Advanced", 9, 9),
    ("Docker", "DevOps", "Docker", "Advanced", 10, 10),
    ("Jenkins", "CI/CD", "Jenkins", "Advanced", 8, 8),
    ("GitHub Actions", "CI/CD", "GitHub", "Advanced", 9, 9),
]

RELANTO_OPPORTUNITIES = [
    ("AI Infrastructure", "OPP_AI_INFRA", "AI Transformation", "Enterprise AI infrastructure modernization involving orchestration, GPU systems, vector databases, scalable model serving, and enterprise AI operations.", 10, 9, 8, "Critical", 2500000, "AI Modernization"),
    ("Cloud Migration", "OPP_CLOUD_MIGRATION", "Cloud Transformation", "Migration of enterprise systems and workloads to scalable cloud-native architectures.", 9, 8, 7, "Critical", 1800000, "Infrastructure Modernization"),
    ("DevOps Modernization", "OPP_DEVOPS", "Engineering Transformation", "CI/CD modernization, infrastructure automation, Kubernetes enablement, platform engineering, and DevOps maturity transformation.", 9, 7, 6, "High", 1200000, "Engineering Modernization"),
    ("MLOps Scaling", "OPP_MLOPS", "AI Operations", "Scaling AI deployment, observability, governance, ML lifecycle automation, and production AI systems.", 10, 9, 8, "Critical", 2200000, "AI Operations"),
    ("Legacy Refactoring", "OPP_LEGACY", "Application Modernization", "Refactoring monolithic enterprise systems into scalable cloud-native modern architectures.", 8, 8, 7, "High", 1600000, "Application Modernization"),
    ("Cost Optimization", "OPP_COST_OPT", "Operational Efficiency", "Cloud cost optimization, infrastructure efficiency, FinOps, automation-led operational cost reduction.", 9, 6, 4, "Critical", 900000, "Cost Transformation"),
]

MAPPING_RULES = {
    "OPP_AI_INFRA": {"PRA_DATA_AI": 10, "PRA_AI_LAB": 10, "PRA_DIGITAL": 7, "PRA_PLANNING": 6},
    "OPP_MLOPS": {"PRA_DATA_AI": 10, "PRA_AI_LAB": 10, "PRA_DIGITAL": 7, "PRA_PLANNING": 5},
    "OPP_DEVOPS": {"PRA_DIGITAL": 10, "PRA_DATA_AI": 5, "PRA_PLANNING": 5},
    "OPP_CLOUD_MIGRATION": {"PRA_DIGITAL": 10, "PRA_DATA_AI": 6, "PRA_PLANNING": 5},
    "OPP_LEGACY": {"PRA_DIGITAL": 9, "PRA_DATA_AI": 5, "PRA_PLANNING": 5},
    "OPP_COST_OPT": {"PRA_DIGITAL": 8, "PRA_PLANNING": 8, "PRA_DATA_AI": 5},
}

RELANTO_PAST_DEALS = [
    {
        "client_name": "Enterprise Analytics Client",
        "project_name": "Cloud Data Platform Modernization",
        "opportunity_type": "Cloud Migration",
        "domain": "Data",
        "technologies_used": ["AWS", "Databricks", "Terraform", "Python"],
        "deal_value_usd": 1800000,
        "delivery_status": "Successful",
        "profitability_score": 8,
        "client_satisfaction_score": 9,
        "transformation_outcome": "Modernized cloud data platform and automated delivery workflows.",
        "strategic_value": "High",
    },
    {
        "client_name": "AI Product Client",
        "project_name": "GenAI Platform Foundation",
        "opportunity_type": "AI Infrastructure",
        "domain": "AI",
        "technologies_used": ["OpenAI", "LangChain", "Vector Databases", "Kubernetes", "Python"],
        "deal_value_usd": 2200000,
        "delivery_status": "Successful",
        "profitability_score": 9,
        "client_satisfaction_score": 9,
        "transformation_outcome": "Built enterprise GenAI foundation with reusable accelerators.",
        "strategic_value": "Critical",
    },
    {
        "client_name": "Digital Operations Client",
        "project_name": "DevOps and Workflow Automation",
        "opportunity_type": "DevOps Modernization",
        "domain": "Engineering",
        "technologies_used": ["Kubernetes", "Docker", "GitHub Actions", "Terraform"],
        "deal_value_usd": 1200000,
        "delivery_status": "Successful",
        "profitability_score": 8,
        "client_satisfaction_score": 8,
        "transformation_outcome": "Improved CI/CD reliability and release velocity.",
        "strategic_value": "High",
    },
]


def seed_relanto(db: Session) -> ServiceCompany:
    """Seed Relanto capability intelligence if missing, then return Relanto."""
    company = db.query(ServiceCompany).filter(ServiceCompany.company_name == "Relanto").first()
    if not company:
        company = ServiceCompany(
            company_name="Relanto",
            legal_name="Relanto Global Private Limited",
            website="https://relanto.ai",
            description="AI-ingrained consulting, enterprise transformation, cloud modernization, Salesforce optimization, workflow intelligence, planning transformation, and intelligent automation company.",
            headquarters="India",
            employee_count=1000,
            ai_maturity_level="Advanced",
            transformation_focus="Enterprise AI, Data Engineering, Workflow Automation, Planning Transformation, Salesforce Optimization, Decision Intelligence",
            market_positioning="AI-first enterprise transformation partner with accelerator-led delivery model",
            primary_regions=["India", "United States", "Canada", "UAE", "Mexico"],
            active_status=True,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    elif (
        db.query(ServicePractice).filter(ServicePractice.company_id == company.id).count() >= len(RELANTO_PRACTICES)
        and db.query(ServiceOpportunity).count() >= len(RELANTO_OPPORTUNITIES)
        and db.query(ServiceOpportunityPracticeMapping).count() >= sum(len(scores) for scores in MAPPING_RULES.values())
    ):
        return company

    practice_by_code: dict[str, ServicePractice] = {}
    for item in RELANTO_PRACTICES:
        practice = db.query(ServicePractice).filter(ServicePractice.practice_code == item["practice_code"]).first()
        if not practice:
            practice = ServicePractice(company_id=company.id, **item)
            db.add(practice)
            db.commit()
            db.refresh(practice)
        practice_by_code[practice.practice_code] = practice

    for name, category, vendor, maturity, trend, importance in RELANTO_TECHNOLOGIES:
        exists = db.query(ServiceTechnology).filter(ServiceTechnology.technology_name == name).first()
        if not exists:
            db.add(ServiceTechnology(
                technology_name=name,
                technology_category=category,
                vendor=vendor,
                maturity_level=maturity,
                market_trend_score=trend,
                strategic_importance=importance,
            ))
    db.commit()

    opportunity_by_code: dict[str, ServiceOpportunity] = {}
    for name, code, category, description, growth, complexity, risk, priority, deal_size, transformation in RELANTO_OPPORTUNITIES:
        opportunity = db.query(ServiceOpportunity).filter(ServiceOpportunity.opportunity_code == code).first()
        if not opportunity:
            opportunity = ServiceOpportunity(
                opportunity_name=name,
                opportunity_code=code,
                opportunity_category=category,
                description=description,
                market_growth_score=growth,
                implementation_complexity=complexity,
                delivery_risk_level=risk,
                strategic_priority=priority,
                avg_deal_size_usd=deal_size,
                transformation_type=transformation,
            )
            db.add(opportunity)
            db.commit()
            db.refresh(opportunity)
        opportunity_by_code[code] = opportunity

    for opportunity_code, practice_scores in MAPPING_RULES.items():
        opportunity = opportunity_by_code[opportunity_code]
        for practice_code, score in practice_scores.items():
            practice = practice_by_code[practice_code]
            exists = db.query(ServiceOpportunityPracticeMapping).filter(
                ServiceOpportunityPracticeMapping.opportunity_id == opportunity.id,
                ServiceOpportunityPracticeMapping.practice_id == practice.id,
            ).first()
            if not exists:
                db.add(ServiceOpportunityPracticeMapping(
                    opportunity_id=opportunity.id,
                    practice_id=practice.id,
                    relevance_score=score,
                    mapping_type="Primary",
                    execution_dependency="Strategic execution dependency",
                ))
    db.commit()

    for deal in RELANTO_PAST_DEALS:
        exists = db.query(ServicePastDeal).filter(
            ServicePastDeal.company_id == company.id,
            ServicePastDeal.project_name == deal["project_name"],
        ).first()
        if not exists:
            db.add(ServicePastDeal(company_id=company.id, **deal))
    db.commit()
    return company
