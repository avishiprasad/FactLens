from app.extraction.llm_extractor import extract_facts


text = """
Delhivery Limited

Revenue from services (₹ million)

FY20     FY21     FY22     FY23     FY24
27,748   36,355   70,536   72,236   81,415
"""


facts = extract_facts(
    text=text,
    document_id="test_document",
    page_number=1
)


print("\nEXTRACTED FACTS\n")

for fact in facts:

    print("----------------------------")

    print("Subject:", fact["subject"])
    print("Predicate:", fact["predicate"])
    print("Value:", fact["value"])
    print("Unit:", fact["unit"])
    print("Period:", fact["period"])
    print("Scope:", fact["scope"])
    print("Evidence:", fact["evidence_text"])
    print("Confidence:", fact["confidence"])