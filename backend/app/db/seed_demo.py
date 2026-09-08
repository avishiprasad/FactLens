from app.db.database import SessionLocal

from app.repositories.document_repository import create_document
from app.repositories.page_repository import create_page
from app.repositories.fact_repository import create_fact
from app.repositories.relationship_repository import (
    create_relationship,
)


def seed_demo_data():

    db = SessionLocal()

    try:

        print("Seeding FactLens demo data...")

        # ==================================================
        # DOCUMENT 1
        # Delhivery Annual Report FY24
        # ==================================================

        annual_report = create_document(
            db=db,
            document_id="delhivery-annual-report-fy24",
            filename=(
                "02-delhivery-annual-report-fy24-excerpt.pdf"
            ),
        )

        annual_page_6 = create_page(
            db=db,
            document_id=annual_report.id,
            page_number=6,
            text=(
                "Revenue from services* (₹ million) "
                "FY20 27,748 FY21 36,355 FY22 70,536 "
                "FY23 72,236 FY24 81,415"
            ),
        )

        annual_revenue = create_fact(
            db=db,
            subject="Delhivery",
            predicate="Revenue from services",
            value="81415",
            value_type="number",
            unit="₹ million",
            period="FY24",
            scope=None,
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Revenue from services* (₹ million) "
                "FY24 81,415"
            ),
            evidence_verified=True,
            page_id=annual_page_6.id,
        )

        # ==================================================
        # DOCUMENT 2
        # Delhivery Q4 FY24 Earnings Presentation
        # ==================================================

        earnings = create_document(
            db=db,
            document_id="delhivery-q4-fy24",
            filename=(
                "03-delhivery-q4-fy24-earnings-presentation.pdf"
            ),
        )

        earnings_page_9 = create_page(
            db=db,
            document_id=earnings.id,
            page_number=9,
            text=(
                "Revenue from services (₹ Cr) "
                "FY22 7,054 FY23 7,224 FY24 8,142"
            ),
        )

        presentation_revenue = create_fact(
            db=db,
            subject="Delhivery",
            predicate="Revenue from services",
            value="8142",
            value_type="number",
            unit="₹ Cr",
            period="FY24",
            scope=None,
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Revenue from services (₹ Cr) "
                "FY24 8,142"
            ),
            evidence_verified=True,
            page_id=earnings_page_9.id,
        )

        # ==================================================
        # CORROBORATION
        # ==================================================

        revenue_relationship = create_relationship(
            db=db,
            relationship_type="CORROBORATES",
            confidence=0.99,
            explanation=(
                "The two documents report the same "
                "Delhivery FY24 revenue from services. "
                "The values are consistent after converting "
                "₹ million and ₹ crore to a common base unit."
            ),
            facts=[
                {
                    "fact_id": annual_revenue.id,
                    "role": "source",
                },
                {
                    "fact_id": presentation_revenue.id,
                    "role": "compared",
                },
            ],
        )

        print(
            "Created revenue corroboration:",
            revenue_relationship.id,
        )

        # ==================================================
        # WORKFORCE
        # ==================================================

        annual_page_2 = create_page(
            db=db,
            document_id=annual_report.id,
            page_number=2,
            text=(
                "Workforce strength: 98,135. "
                "Includes permanent employees, contractual "
                "workers and last mile delivery partner agents."
            ),
        )

        workforce = create_fact(
            db=db,
            subject="Delhivery",
            predicate="Workforce strength",
            value="98135",
            value_type="number",
            unit="people",
            period="FY24",
            scope=(
                "Includes permanent employees, contractual "
                "workers and last mile delivery partner agents."
            ),
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Workforce strength: 98,135"
            ),
            evidence_verified=True,
            page_id=annual_page_2.id,
        )

        # ==================================================
        # TEAM SIZE + PARTNER AGENTS
        # ==================================================

        earnings_page_8 = create_page(
            db=db,
            document_id=earnings.id,
            page_number=8,
            text=(
                "Team size Q4 FY24: 63,713. "
                "Partner agents Q4 FY24: 34,422."
            ),
        )

        team_size = create_fact(
            db=db,
            subject="Delhivery",
            predicate="Team size",
            value="63713",
            value_type="number",
            unit="people",
            period="Q4 FY24",
            scope=(
                "Permanent employees and contractual "
                "workers, excluding partner agents."
            ),
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Team size Q4 FY24: 63,713"
            ),
            evidence_verified=True,
            page_id=earnings_page_8.id,
        )

        partner_agents = create_fact(
            db=db,
            subject="Delhivery",
            predicate="Partner agents",
            value="34422",
            value_type="number",
            unit="people",
            period="Q4 FY24",
            scope=(
                "Last-mile delivery partner agents "
                "in the last month."
            ),
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Partner agents Q4 FY24: 34,422"
            ),
            evidence_verified=True,
            page_id=earnings_page_8.id,
        )

        # ==================================================
        # THREE-FACT WORKFORCE RECONCILIATION
        # ==================================================

        reconciliation_relationship = create_relationship(
            db=db,
            relationship_type="RECONCILED",
            confidence=0.98,
            explanation=(
                "The reported workforce of 98,135 is "
                "mathematically reconciled by combining "
                "63,713 team members and 34,422 partner "
                "agents: 63,713 + 34,422 = 98,135. "
                "The apparent difference is explained "
                "by scope."
            ),
            facts=[
                {
                    "fact_id": team_size.id,
                    "role": "component",
                },
                {
                    "fact_id": partner_agents.id,
                    "role": "component",
                },
                {
                    "fact_id": workforce.id,
                    "role": "total",
                },
            ],
        )

        print(
            "Created workforce reconciliation:",
            reconciliation_relationship.id,
        )

        # ==================================================
        # DOCUMENT 3
        # RBI Annual Report
        # ==================================================

        rbi = create_document(
            db=db,
            document_id="rbi-annual-report-fy25",
            filename=(
                "02-rbi-annual-report-2024-25-excerpt.pdf"
            ),
        )

        rbi_page = create_page(
            db=db,
            document_id=rbi.id,
            page_number=17,
            text=(
                "Real GDP growth for 2025-26 is projected "
                "at 6.5 per cent, with risks evenly balanced."
            ),
        )

        rbi_fact = create_fact(
            db=db,
            subject="India",
            predicate="Real GDP growth",
            value="6.5",
            value_type="percentage",
            unit="percent",
            period="FY2025-26",
            scope="RBI forecast",
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Real GDP growth for 2025-26 is projected "
                "at 6.5 per cent"
            ),
            evidence_verified=True,
            page_id=rbi_page.id,
        )

        # ==================================================
        # DOCUMENT 4
        # IMF Article IV
        # ==================================================

        imf = create_document(
            db=db,
            document_id="imf-india-2025",
            filename=(
                "03-imf-india-2025-article-iv-excerpt.pdf"
            ),
        )

        imf_page = create_page(
            db=db,
            document_id=imf.id,
            page_number=13,
            text=(
                "Real GDP growth is projected at "
                "6.6 percent in FY2025/26."
            ),
        )

        imf_fact = create_fact(
            db=db,
            subject="India",
            predicate="Real GDP growth",
            value="6.6",
            value_type="percentage",
            unit="percent",
            period="FY2025-26",
            scope="IMF forecast",
            confidence=0.99,
            extraction_method="seed",
            evidence_text=(
                "Real GDP growth is projected at "
                "6.6 percent in FY2025/26."
            ),
            evidence_verified=True,
            page_id=imf_page.id,
        )

        # ==================================================
        # FORECAST DISAGREEMENT
        # ==================================================

        forecast_relationship = create_relationship(
            db=db,
            relationship_type="LIKELY_DISAGREEMENT",
            confidence=0.90,
            explanation=(
                "Both forecasts describe India's real GDP "
                "growth for FY2025-26, but the independently "
                "produced estimates differ slightly: "
                "RBI 6.5% versus IMF 6.6%. "
                "This is treated as a likely disagreement "
                "rather than a hard contradiction."
            ),
            facts=[
                {
                    "fact_id": rbi_fact.id,
                    "role": "source",
                },
                {
                    "fact_id": imf_fact.id,
                    "role": "compared",
                },
            ],
        )

        print(
            "Created forecast relationship:",
            forecast_relationship.id,
        )

        print()
        print("================================")
        print("DEMO DATA SEEDED SUCCESSFULLY")
        print("================================")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()