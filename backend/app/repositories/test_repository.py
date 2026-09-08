from app.db.database import SessionLocal

from app.repositories.document_repository import (
    create_document,
    get_document,
)

from app.repositories.page_repository import (
    create_page,
    get_pages_for_document,
)

from app.repositories.fact_repository import (
    create_fact,
    get_facts_for_page,
)

from app.repositories.relationship_repository import (
    create_relationship,
    get_all_relationships,
)


db = SessionLocal()


try:

    print("\n================================")
    print("REPOSITORY LAYER TEST")
    print("================================\n")

    # ----------------------------------------
    # 1. Create document
    # ----------------------------------------

    document = create_document(
        db=db,
        document_id="test-document-001",
        filename="test.pdf",
        file_hash="test-hash",
    )

    print(
        "Document created:",
        document.document_id
    )

    # ----------------------------------------
    # 2. Create page
    # ----------------------------------------

    page = create_page(
        db=db,
        document_id=document.id,
        page_number=1,
        text="Revenue from services was ₹8,142 crore in FY24.",
    )

    print(
        "Page created:",
        page.page_number
    )

    # ----------------------------------------
    # 3. Create fact
    # ----------------------------------------

    fact = create_fact(
        db=db,
        subject="Delhivery",
        predicate="Revenue from services",
        value="8142",
        value_type="number",
        unit="₹ crore",
        period="FY24",
        scope=None,
        confidence=0.95,
        extraction_method="test",
        evidence_text="Revenue from services was ₹8,142 crore in FY24.",
        evidence_verified=True,
        page_id=page.id,
    )

    print(
        "Fact created:",
        fact.predicate,
        "=",
        fact.value,
        fact.unit,
    )

    # ----------------------------------------
    # 4. Retrieve document
    # ----------------------------------------

    retrieved_document = get_document(
        db,
        "test-document-001",
    )

    assert retrieved_document is not None

    print(
        "Document retrieval: PASSED"
    )

    # ----------------------------------------
    # 5. Retrieve facts
    # ----------------------------------------

    facts = get_facts_for_page(
        db,
        page.id,
    )

    assert len(facts) == 1

    print(
        "Fact retrieval: PASSED"
    )

    # ----------------------------------------
    # 6. Create self relationship
    # ----------------------------------------
    #
    # Temporary database test only.
    # We will use two real facts later.
    #

    relationship = create_relationship(
        db=db,
        fact_a_id=fact.id,
        fact_b_id=fact.id,
        relationship_type="TEST",
        confidence=1.0,
        explanation="Repository test relationship.",
    )

    print(
        "Relationship created:",
        relationship.relationship_type,
    )

    relationships = get_all_relationships(db)

    assert len(relationships) >= 1

    print(
        "Relationship retrieval: PASSED"
    )

    print("\n================================")
    print("REPOSITORY TEST PASSED")
    print("================================")


finally:

    db.close()