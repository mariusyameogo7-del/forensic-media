import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workers.analysis.worker.engines.c2pa_engine import C2PAEngine
from workers.analysis.worker.adapters.mock_adapters import MockAIProvider, MockWebContextProvider, MockFactCheckProvider
from workers.analysis.worker.engines.synthesis_engine import SynthesisEngine
from apps.api.app.models.enums import AIStatus, ProvenanceStatus, ConclusionLevel


def test_chatgpt_dalle3_c2pa_detection():
    print("--- 1. Test Detection C2PA & ChatGPT / DALL-E 3 ---")
    
    # Simulate a JPEG with C2PA JUMBF block containing OpenAI DALL-E 3 & trainedAlgorithmicMedia
    simulated_chatgpt_bytes = (
        b"\xFF\xD8\xFF\xE0\x00\x10JFIF"
        b"\xFF\xEB\x00\x80c2paJUMB\x00\x00\x00"
        b"<x:xmpmeta xmlns:x='adobe:ns:meta/'>"
        b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>"
        b"<rdf:Description rdf:about=''>"
        b"<Iptc4xmpExt:DigitalSourceType>http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia</Iptc4xmpExt:DigitalSourceType>"
        b"<photoshop:Credit>OpenAI DALL-E 3 (ChatGPT)</photoshop:Credit>"
        b"</rdf:Description></rdf:RDF></x:xmpmeta>"
        b"\xFF\xD9"
    )

    c2pa_engine = C2PAEngine()
    c2pa_result = c2pa_engine.run(simulated_chatgpt_bytes, "chatgpt_image.jpg")

    print("C2PA Resultat :", c2pa_result["claim_generator"], "| AI Declared:", c2pa_result["ai_declared"])
    assert c2pa_result["has_manifest"] == True
    assert c2pa_result["ai_declared"] == True
    assert "OpenAI" in str(c2pa_result["claim_generator"]) or "DALL" in str(c2pa_result["claim_generator"])
    print("[OK] C2PA ChatGPT / DALL-E 3 detecte avec succes !")

    ai_provider = MockAIProvider()
    ai_result = ai_provider.analyze(simulated_chatgpt_bytes)
    print("AI Detecteur :", ai_result.category.value, "| Confidence:", ai_result.confidence)
    assert ai_result.category == AIStatus.DECLARED
    print("[OK] Statut IA DECLARED (100% reconnu comme IA generative certifiee) !")

    synthesis = SynthesisEngine()
    (conc, prov, integ, ai_st, ctx, sum_fr, evs) = synthesis.run(
        c2pa_data=c2pa_result,
        metadata_data=None,
        hash_data=None,
        ai_data={"category": ai_result.category, "raw_score": ai_result.raw_score},
        web_matches=[],
        fact_checks=[],
        claim="Image de test creee sur ChatGPT"
    )

    print("\nSynthese globale :")
    print("  Conclusion :", conc.value)
    print("  Provenance :", prov.value)
    print("  Indices IA :", ai_st.value)
    print("  Preuves    :", len(evs))
    assert ai_st == AIStatus.DECLARED
    assert prov == ProvenanceStatus.VERIFIED
    print("[OK] Synthese prudente validee avec preuves d'origine certifiee !")


def test_global_context_anywhere():
    print("\n--- 2. Test Contexte Web Mondial (Toutes Villes / Pays) ---")
    web_provider = MockWebContextProvider()
    
    cities = ["Abidjan", "Dakar", "Paris", "Bamako", "Kinshasa", "Lomé", "Niamey"]
    for city in cities:
        matches = web_provider.search(b"dummy", claim=f"Photo prise hier a {city}")
        assert len(matches) > 0
        print(f"[OK] Contexte Web reconnu pour '{city}' -> {matches[0].title}")


if __name__ == "__main__":
    test_chatgpt_dalle3_c2pa_detection()
    test_global_context_anywhere()
    print("\nTOUS LES TESTS D'INTELLIGENCE ET DE DETECTION SONT VALIDÉS !")
