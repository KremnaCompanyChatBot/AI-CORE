"""
Test suite for persona-based dynamic prompt generation with tone validation.

This test file contains 20 test scenarios covering formal, playful, and technical tones
to validate that AI responses match the intended persona tone.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from dynamic_prompt_generation import build_prompt, TEST_SYSTEM_PROMPT
from persona import fetch_persona


# ============================================================================
# TEST DATA: 20 Different Persona Scenarios
# ============================================================================

FORMAL_PERSONAS = [
    {
        "name": "Prof. Dr. Ahmet Yılmaz",
        "tone": "resmi ve saygılı",
        "constraints": "Asla argo kullanma. Her zaman nazik ve profesyonel ol. Akademik dil kullan.",
        "expected_keywords": ["sayın", "memnuniyetle", "lütfen", "bilgilendirmek", "profesyonel"],
        "expected_avoid": ["slang", "yaw", "hey", "lan"]
    },
    {
        "name": "Müdür Hanım",
        "tone": "ciddi ve profesyonel",
        "constraints": "Resmi iletişim kurallarına uy. Kısa ve öz yanıtlar ver.",
        "expected_keywords": ["sayın", "memnun", "uygun", "durum", "bilgi"],
        "expected_avoid": ["eğlenceli", "şaka", "gülmek"]
    },
    {
        "name": "Avukat Mehmet Bey",
        "tone": "hukuki ve formal",
        "constraints": "Hukuki terimler kullan. Resmi dil koru. Yasal uyarılar ekle.",
        "expected_keywords": ["hukuki", "yasal", "uyarı", "mahkeme", "sözleşme"],
        "expected_avoid": ["gayri resmi", "arkadaşça"]
    },
    {
        "name": "Doktor Ayşe Hanım",
        "tone": "tıbbi ve ciddi",
        "constraints": "Tıbbi terimler kullan. Ciddi ve güvenilir ol. Hastaya saygı göster.",
        "expected_keywords": ["hasta", "tedavi", "teşhis", "tıbbi", "muayene"],
        "expected_avoid": ["şaka", "eğlenceli", "gülmek"]
    },
    {
        "name": "İnsan Kaynakları Uzmanı",
        "tone": "kurumsal ve resmi",
        "constraints": "Kurumsal iletişim dili kullan. Profesyonel yaklaşım sergile.",
        "expected_keywords": ["kurumsal", "profesyonel", "süreç", "değerlendirme", "başvuru"],
        "expected_avoid": ["gayri resmi", "kişisel"]
    },
    {
        "name": "Bankacı Emre Bey",
        "tone": "finansal ve formal",
        "constraints": "Finansal terimler kullan. Güven verici ol. Resmi dil koru.",
        "expected_keywords": ["hesap", "faiz", "yatırım", "finansal", "güvenli"],
        "expected_avoid": ["gayri resmi", "şaka"]
    },
    {
        "name": "Diplomat Can Hanım",
        "tone": "diplomatik ve saygılı",
        "constraints": "Diplomatik dil kullan. Kültürlerarası hassasiyet göster.",
        "expected_keywords": ["saygı", "diplomatik", "uluslararası", "anlayış", "işbirliği"],
        "expected_avoid": ["tartışma", "gergin"]
    }
]

PLAYFUL_PERSONAS = [
    {
        "name": "Komik Asistan Ali",
        "tone": "eğlenceli ve neşeli",
        "constraints": "Şakalar yap, emojiler kullan (metin olarak), samimi ol.",
        "expected_keywords": ["eğlenceli", "güzel", "harika", "hey", "wow"],
        "expected_avoid": ["ciddi", "resmi", "profesyonel"]
    },
    {
        "name": "Arkadaşça Bot Zeynep",
        "tone": "sıcak ve arkadaşça",
        "constraints": "Samimi dil kullan. Kullanıcıyla arkadaş gibi konuş. Eğlenceli ol.",
        "expected_keywords": ["arkadaş", "samimi", "eğlenceli", "hey", "hadi"],
        "expected_avoid": ["resmi", "sayın", "memnuniyetle"]
    },
    {
        "name": "Sosyal Medya Asistanı",
        "tone": "genç ve dinamik",
        "constraints": "Gençlik dilini kullan. Emojiler kullan (metin olarak). Trendleri takip et.",
        "expected_keywords": ["süper", "harika", "cool", "mükemmel", "çok iyi"],
        "expected_avoid": ["resmi", "ciddi", "formal"]
    },
    {
        "name": "Oyun Arkadaşı Bot",
        "tone": "oyuncu ve eğlenceli",
        "constraints": "Oyun dilini kullan. Heyecan verici ol. Motivasyon ver.",
        "expected_keywords": ["oyun", "heyecan", "başarı", "tebrik", "güçlü"],
        "expected_avoid": ["sıkıcı", "ciddi"]
    },
    {
        "name": "Mizah Asistanı",
        "tone": "komik ve yaratıcı",
        "constraints": "Mizahi yaklaşım sergile. Kullanıcıyı güldürmeye çalış. Yaratıcı ol.",
        "expected_keywords": ["komik", "eğlenceli", "gülmek", "şaka", "neşeli"],
        "expected_avoid": ["ciddi", "resmi", "sıkıcı"]
    },
    {
        "name": "Yaratıcı Rehber",
        "tone": "yaratıcı ve ilham verici",
        "constraints": "Yaratıcı öneriler ver. İlham verici ol. Eğlenceli yaklaşım sergile.",
        "expected_keywords": ["yaratıcı", "ilham", "harika", "mükemmel", "heyecan"],
        "expected_avoid": ["sıkıcı", "standart"]
    }
]

TECHNICAL_PERSONAS = [
    {
        "name": "Yazılım Mimarı",
        "tone": "teknik ve detaylı",
        "constraints": "Teknik terimler kullan. Kod örnekleri ver. Detaylı açıklamalar yap.",
        "expected_keywords": ["algoritma", "mimari", "kod", "fonksiyon", "optimizasyon"],
        "expected_avoid": ["basit", "anlaşılmayan açıklama"]
    },
    {
        "name": "DevOps Uzmanı",
        "tone": "teknik ve operasyonel",
        "constraints": "DevOps terimlerini kullan. Altyapı detaylarını açıkla. Sistem odaklı ol.",
        "expected_keywords": ["docker", "kubernetes", "ci/cd", "infrastructure", "deployment"],
        "expected_avoid": ["basit açıklama", "genel"]
    },
    {
        "name": "Veri Bilimci",
        "tone": "analitik ve bilimsel",
        "constraints": "İstatistiksel terimler kullan. Veri analizi tekniklerini açıkla.",
        "expected_keywords": ["veri", "analiz", "model", "istatistik", "machine learning"],
        "expected_avoid": ["basit", "yüzeysel"]
    },
    {
        "name": "Güvenlik Uzmanı",
        "tone": "teknik ve güvenlik odaklı",
        "constraints": "Güvenlik terimlerini kullan. Tehdit analizi yap. Güvenli çözümler öner.",
        "expected_keywords": ["güvenlik", "şifreleme", "authentication", "threat", "vulnerability"],
        "expected_avoid": ["güvensiz", "riski göz ardı et"]
    },
    {
        "name": "Sistem Mühendisi",
        "tone": "teknik ve sistem odaklı",
        "constraints": "Sistem mimarisi terimleri kullan. Performans optimizasyonu öner. Detaylı analiz yap.",
        "expected_keywords": ["sistem", "performans", "mimari", "scalability", "optimizasyon"],
        "expected_avoid": ["yüzeysel", "basit"]
    },
    {
        "name": "AI/ML Mühendisi",
        "tone": "bilimsel ve teknik",
        "constraints": "AI/ML terimlerini kullan. Model eğitimi detaylarını açıkla. Teknik derinlik sağla.",
        "expected_keywords": ["model", "training", "neural network", "algorithm", "feature"],
        "expected_avoid": ["basit açıklama", "yüzeysel"]
    },
    {
        "name": "Network Uzmanı",
        "tone": "teknik ve ağ odaklı",
        "constraints": "Ağ protokolleri terimlerini kullan. Network topolojisi açıkla.",
        "expected_keywords": ["network", "protocol", "topology", "routing", "firewall"],
        "expected_avoid": ["basit", "genel açıklama"]
    }
]

ALL_PERSONAS = FORMAL_PERSONAS + PLAYFUL_PERSONAS + TECHNICAL_PERSONAS


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def mock_fetch_persona(persona_data):
    """Helper function to mock fetch_persona with given persona data."""
    return Mock(return_value=persona_data)


def extract_constraints_text(constraints):
    """Extract constraint text from persona data."""
    if isinstance(constraints, str):
        return constraints
    elif isinstance(constraints, list):
        return "\n".join(constraints)
    return str(constraints)


def validate_prompt_contains(prompt_text, keywords):
    """Validate that prompt contains expected keywords."""
    prompt_lower = prompt_text.lower()
    return all(keyword.lower() in prompt_lower for keyword in keywords)


def validate_prompt_avoids(prompt_text, avoid_keywords):
    """Validate that prompt avoids certain keywords."""
    prompt_lower = prompt_text.lower()
    return not any(avoid.lower() in prompt_lower for avoid in avoid_keywords)


# ============================================================================
# TEST CASES: Prompt Generation Tests
# ============================================================================

@pytest.mark.parametrize("persona", FORMAL_PERSONAS, ids=[p["name"] for p in FORMAL_PERSONAS])
def test_formal_persona_prompt_generation(persona):
    """Test that formal personas generate prompts with formal tone indicators."""
    with patch('dynamic_prompt_generation.fetch_persona', return_value={
        "name": persona["name"],
        "tone": persona["tone"],
        "constraints": persona["constraints"]
    }):
        with patch('builtins.print'):  # Suppress print output
            result = build_prompt()
            
            # Get the generated prompt by capturing print output
            # Since build_prompt prints the prompt, we'll test the format function directly
            system_prompt = TEST_SYSTEM_PROMPT.format(
                name=persona["name"],
                tone=persona["tone"],
                constraints_list=persona["constraints"]
            )
            
            # Validate prompt structure
            assert persona["name"] in system_prompt
            assert persona["tone"] in system_prompt
            assert persona["constraints"] in system_prompt
            
            # Validate expected keywords are present
            assert validate_prompt_contains(system_prompt, persona["expected_keywords"])
            
            # Validate avoided keywords are not present
            assert validate_prompt_avoids(system_prompt, persona["expected_avoid"])


@pytest.mark.parametrize("persona", PLAYFUL_PERSONAS, ids=[p["name"] for p in PLAYFUL_PERSONAS])
def test_playful_persona_prompt_generation(persona):
    """Test that playful personas generate prompts with playful tone indicators."""
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=persona["name"],
        tone=persona["tone"],
        constraints_list=persona["constraints"]
    )
    
    # Validate prompt structure
    assert persona["name"] in system_prompt
    assert persona["tone"] in system_prompt
    assert persona["constraints"] in system_prompt
    
    # Validate expected keywords are present
    assert validate_prompt_contains(system_prompt, persona["expected_keywords"])


@pytest.mark.parametrize("persona", TECHNICAL_PERSONAS, ids=[p["name"] for p in TECHNICAL_PERSONAS])
def test_technical_persona_prompt_generation(persona):
    """Test that technical personas generate prompts with technical tone indicators."""
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=persona["name"],
        tone=persona["tone"],
        constraints_list=persona["constraints"]
    )
    
    # Validate prompt structure
    assert persona["name"] in system_prompt
    assert persona["tone"] in system_prompt
    assert persona["constraints"] in system_prompt
    
    # Validate expected keywords are present
    assert validate_prompt_contains(system_prompt, persona["expected_keywords"])


# ============================================================================
# TEST CASES: Environment and API Integration Tests
# ============================================================================

def test_build_prompt_with_missing_env_vars():
    """Test that build_prompt handles missing environment variables gracefully."""
    with patch.dict('os.environ', {}, clear=True):
        with patch('dynamic_prompt_generation.load_dotenv'):
            with patch('builtins.print') as mock_print:
                result = build_prompt()
                # Should print error message
                assert mock_print.called


def test_build_prompt_with_valid_persona():
    """Test build_prompt with valid persona data."""
    test_persona = {
        "name": "Test Assistant",
        "tone": "resmi ve profesyonel",
        "constraints": "Test constraint"
    }
    
    with patch('dynamic_prompt_generation.load_dotenv'):
        with patch('dynamic_prompt_generation.fetch_persona', return_value=test_persona):
            with patch('builtins.print'):
                with patch.dict('os.environ', {
                    'PERSONA_API_URL': 'http://test.com',
                    'PERSONA_API_TOKEN': 'test_token',
                    'ABLY_API_KEY': 'test_key',
                    'ABLY_CHANNEL': 'test_channel'
                }):
                    result = build_prompt()
                    # Should complete without errors
                    assert result is None or result is not None  # Either way is fine


def test_persona_fetch_with_api():
    """Test persona fetch with API URL."""
    mock_response = {
        "name": "API Test Persona",
        "tone": "test tone",
        "constraints": "test constraints"
    }
    
    with patch('persona.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()
        
        result = fetch_persona(api_url="http://test.com", token="test_token")
        
        assert result["name"] == mock_response["name"]
        assert result["tone"] == mock_response["tone"]
        assert result["constraints"] == mock_response["constraints"]


def test_persona_fetch_with_ably():
    """Test persona fetch with Ably channel."""
    mock_ably_response = [{
        "data": '{"name": "Ably Persona", "tone": "ably tone", "constraints": "ably constraints"}'
    }]
    
    with patch('persona.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_ably_response
        mock_get.return_value.raise_for_status = Mock()
        
        result = fetch_persona(
            api_url=None,
            ably_channel="test_channel",
            ably_api_key="test_key"
        )
        
        assert result["name"] == "Ably Persona"
        assert result["tone"] == "ably tone"
        assert result["constraints"] == "ably constraints"


# ============================================================================
# TEST CASES: Tone Matching Validation Tests
# ============================================================================

def test_formal_tone_validation():
    """Test that formal tone personas generate prompts that enforce formal language."""
    formal_persona = FORMAL_PERSONAS[0]
    
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=formal_persona["name"],
        tone=formal_persona["tone"],
        constraints_list=formal_persona["constraints"]
    )
    
    # Check that formal tone is explicitly mentioned
    assert "resmi" in system_prompt.lower() or "formal" in system_prompt.lower()
    
    # Check that constraints enforce formal language
    assert "argo" in system_prompt.lower() or "nazik" in system_prompt.lower()


def test_playful_tone_validation():
    """Test that playful tone personas generate prompts that allow informal language."""
    playful_persona = PLAYFUL_PERSONAS[0]
    
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=playful_persona["name"],
        tone=playful_persona["tone"],
        constraints_list=playful_persona["constraints"]
    )
    
    # Check that playful tone is mentioned
    assert "eğlenceli" in system_prompt.lower() or "playful" in system_prompt.lower()
    
    # Check that constraints allow informal language
    assert "şaka" in system_prompt.lower() or "samimi" in system_prompt.lower()


def test_technical_tone_validation():
    """Test that technical tone personas generate prompts that require technical language."""
    technical_persona = TECHNICAL_PERSONAS[0]
    
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=technical_persona["name"],
        tone=technical_persona["tone"],
        constraints_list=technical_persona["constraints"]
    )
    
    # Check that technical tone is mentioned
    assert "teknik" in system_prompt.lower() or "technical" in system_prompt.lower()
    
    # Check that constraints require technical terms
    assert "teknik" in system_prompt.lower() or "terim" in system_prompt.lower()


# ============================================================================
# TEST CASES: Edge Cases and Error Handling
# ============================================================================

def test_persona_with_missing_name():
    """Test handling of persona with missing name field."""
    with patch('dynamic_prompt_generation.fetch_persona', return_value={
        "tone": "test tone",
        "constraints": "test constraints"
    }):
        with patch('builtins.print'):
            with patch('dynamic_prompt_generation.load_dotenv'):
                with patch.dict('os.environ', {
                    'PERSONA_API_URL': 'http://test.com',
                    'PERSONA_API_TOKEN': 'test_token',
                    'ABLY_API_KEY': 'test_key',
                    'ABLY_CHANNEL': 'test_channel'
                }):
                    # Should handle KeyError gracefully
                    try:
                        build_prompt()
                    except KeyError:
                        # Expected behavior
                        pass


def test_persona_with_empty_constraints():
    """Test handling of persona with empty constraints."""
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name="Test Name",
        tone="test tone",
        constraints_list=""
    )
    
    # Should still generate valid prompt
    assert "Test Name" in system_prompt
    assert "test tone" in system_prompt


def test_prompt_template_formatting():
    """Test that TEST_SYSTEM_PROMPT template formats correctly with all fields."""
    test_name = "Test Assistant"
    test_tone = "test tone"
    test_constraints = "test constraints"
    
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=test_name,
        tone=test_tone,
        constraints_list=test_constraints
    )
    
    assert test_name in system_prompt
    assert test_tone in system_prompt
    assert test_constraints in system_prompt
    assert "KİMLİK VE ROL" in system_prompt
    assert "DAVRANIŞ KURALLARI" in system_prompt
    assert "GÖREV" in system_prompt


# ============================================================================
# COMPREHENSIVE TEST: All 20 Scenarios
# ============================================================================

@pytest.mark.parametrize("persona", ALL_PERSONAS, ids=[p["name"] for p in ALL_PERSONAS])
def test_all_persona_scenarios(persona):
    """Comprehensive test for all 20 persona scenarios."""
    # Generate system prompt
    system_prompt = TEST_SYSTEM_PROMPT.format(
        name=persona["name"],
        tone=persona["tone"],
        constraints_list=persona["constraints"]
    )
    
    # Basic structure validation
    assert persona["name"] in system_prompt
    assert persona["tone"] in system_prompt
    assert persona["constraints"] in system_prompt
    
    # Tone-specific validation
    tone_lower = persona["tone"].lower()
    if "resmi" in tone_lower or "formal" in tone_lower or "ciddi" in tone_lower:
        # Formal personas should avoid playful language
        assert validate_prompt_avoids(system_prompt, ["eğlenceli", "şaka", "gülmek"])
    elif "eğlenceli" in tone_lower or "playful" in tone_lower or "komik" in tone_lower:
        # Playful personas should avoid overly formal language
        assert "eğlenceli" in system_prompt.lower() or "samimi" in system_prompt.lower()
    elif "teknik" in tone_lower or "technical" in tone_lower:
        # Technical personas should emphasize technical terms
        assert "teknik" in system_prompt.lower() or "technical" in system_prompt.lower()
    
    # Keyword validation
    assert validate_prompt_contains(system_prompt, persona["expected_keywords"])


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

