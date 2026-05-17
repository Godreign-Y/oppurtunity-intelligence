import asyncio
from src.db.database import AsyncSessionLocal
from src.db.crud import get_company_by_name, create_company, create_funding_event
from src.schemas.funding import CompanyCreate, FundingEventCreate
from src.collectors.rss_fetcher import RSSFetcher
from src.processors.llm_extractor import LLMExtractor
from src.processors.classifier import CompanyClassifier

async def run_pipeline():
    """
    Orchestrates the data collection, processing, and database saving.
    """
    print("Starting Funding Intelligence Pipeline...")
    
    # 1. Initialize components
    fetcher = RSSFetcher()
    extractor = LLMExtractor()
    classifier = CompanyClassifier()

    # 2. Fetch raw signals
    raw_signals = await fetcher.fetch_signals()
    print(f"Found {len(raw_signals)} potential articles from RSS.")

    async with AsyncSessionLocal() as session:
        for signal in raw_signals:
            # 3. Extract entities
            print(f"Extracting entities for: {signal['title']}")
            extracted = await extractor.extract_entities(signal["raw_text"])
            
            # Rate Limiting: Wait 3 seconds to avoid 429 errors from Gemini
            await asyncio.sleep(3)
            
            if not extracted or not extracted.get("company_name"):
                print("Could not extract company name. Skipping.")
                continue
                
            company_name = extracted["company_name"]
            
            # 4. Classify company (Product vs Service)
            is_product = await classifier.classify_company(company_name, signal["raw_text"])
            
            # Rate Limiting: Wait 3 seconds to avoid 429 errors from Gemini
            await asyncio.sleep(3)
            
            if not is_product:
                print(f"Skipping {company_name} - classified as service-based.")
                continue
                
            # 5. Database operations
            company = await get_company_by_name(session, company_name)
            if not company:
                company_data = CompanyCreate(
                    name=company_name,
                    industry="Technology", # Defaulting for now
                    is_product_based=True,
                    description=f"Extracted from: {signal['title']}"
                )
                company = await create_company(session, company_data)
                
            # Calculate simple opportunity score
            score = 10
            if extracted.get("stage") and "Series" in extracted["stage"]:
                score += 20
            if extracted.get("amount") and extracted["amount"] > 10:
                score += 15

            event_data = FundingEventCreate(
                company_name=company_name,
                amount=extracted.get("amount"),
                stage=extracted.get("stage"),
                source_url=signal["source_url"],
                raw_text=signal["raw_text"],
                opportunity_score=score
            )
            
            await create_funding_event(session, event_data, company.id)
            print(f"Successfully tracked funding event for {company_name}")

    print("Pipeline execution complete.")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
