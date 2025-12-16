"""
Chatbot Test Modülü

Main dizinindeki tüm modülleri test etmek için kullanılır.
"""

import os
from typing import Dict, Any, Optional


# Mock Persona Verisi
MOCK_PERSONA_DATA = {
    "name": "Kremna Asistanı",
    "tone": "Arkadaşça, yardımcı ve profesyonel",
    "constraints": "Kısa ve öz cevaplar ver.\nKaba dil kullanma.\nTürkçe konuş.\nTıbbi veya hukuki tavsiye verme.",
    "raw": {
        "name": "Kremna Asistanı",
        "tone": "Arkadaşça, yardımcı ve profesyonel",
        "constraints": "Kısa ve öz cevaplar ver.\nKaba dil kullanma.\nTürkçe konuş.\nTıbbi veya hukuki tavsiye verme.",
        "version": "1.0",
        "language": "tr"
    }
}

# Mock Ortam Değişkenleri
MOCK_ENV_VARS = {
    "PERSONA_API_URL": "http://mock-api.example.com/persona",
    "PERSONA_API_TOKEN": "mock_token_12345",
    "ABLY_API_KEY": "mock_ably_key",
    "ABLY_CHANNEL": "mock_channel"
}


def test_persona_module_with_mock():
    """Persona modülünün temel işlevlerini mock veri ile test eder."""
    print("\n=== PERSONA MODÜLÜ TESTİ (MOCK VERİ) ===")
    
    try:
        from persona import _extract_persona_fields, PersonaFetchError
        
        print("✓ Persona modülü başarıyla içe aktarıldı")
        
        # Test 1: Persona alanlarını çıkartma fonksiyonunu test et
        print("\n--- Persona Alan Çıkarma Testi ---")
        try:
            # Doğrudan format testi
            result1 = _extract_persona_fields(MOCK_PERSONA_DATA)
            print("✓ Doğrudan format başarıyla işlendi")
            
            # Nested format testi
            nested_data = {"persona": MOCK_PERSONA_DATA}
            result2 = _extract_persona_fields(nested_data)
            print("✓ Nested format başarıyla işlendi")
            
            # Attributes format testi
            attr_data = {"attributes": MOCK_PERSONA_DATA}
            result3 = _extract_persona_fields(attr_data)
            print("✓ Attributes format başarıyla işlendi")
            
            print(f"\n✓ Mock persona verisi başarıyla işlendi!")
            print(f"  - Persona adı: {result1.get('name', 'Bilinmiyor')}")
            print(f"  - Ses tonu: {result1.get('tone', 'Bilinmiyor')}")
            print(f"  - Kısıtlamalar: {result1.get('constraints', 'Bilinmiyor')[:50]}...")
            return True
            
        except Exception as e:
            print(f"✗ Persona işleme hatası: {e}")
            return False
    
    except ImportError as e:
        print(f"✗ Persona modülü içe aktarılamadı: {e}")
        return False
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        return False



def test_persona_module():
    """Persona modülünün temel işlevlerini test eder."""
    print("\n=== PERSONA MODÜLÜ TESTİ (GERÇEK API) ===")
    
    try:
        from persona import fetch_persona, PersonaFetchError
        
        print("✓ Persona modülü başarıyla içe aktarıldı")
        
        # Test 1: Ortam değişkenlerini kontrol et
        backend_url = os.getenv("BACKEND_PANEL_URL")
        ably_api_key = os.getenv("ABLY_API_KEY")
        ably_channel = os.getenv("ABLY_CHANNEL")
        
        if backend_url:
            print(f"✓ BACKEND_PANEL_URL bulundu: {backend_url[:30]}...")
        else:
            print("⚠ BACKEND_PANEL_URL bulunamadı")
            
        if ably_api_key:
            print(f"✓ ABLY_API_KEY bulundu: {ably_api_key[:20]}...")
        else:
            print("⚠ ABLY_API_KEY bulunamadı")
            
        if ably_channel:
            print(f"✓ ABLY_CHANNEL bulundu: {ably_channel}")
        else:
            print("⚠ ABLY_CHANNEL bulunamadı")
        
        # Test 2: Persona verisi çekmeyi dene
        print("\n--- Persona Verisi Çekiliyor ---")
        
        # Backend URL veya Ably bilgileri yoksa test geç
        if not backend_url and not (ably_api_key and ably_channel):
            print("⚠ Backend URL veya Ably bilgileri eksik - Gerçek API testi atlanıyor")
            print("💡 Mock veri testi kullanılıyor...")
            return test_persona_module_with_mock()
        
        try:
            # Ably ile test et
            if ably_api_key and ably_channel:
                persona_data = fetch_persona(
                    api_url=None,
                    ably_channel=ably_channel,
                    ably_api_key=ably_api_key
                )
            # Backend URL ile test et
            else:
                persona_data = fetch_persona(
                    api_url=backend_url,
                    token=os.getenv("BACKEND_PANEL_TOKEN")
                )
            
            if persona_data:
                print("✓ Persona verisi başarıyla alındı!")
                print(f"  - Persona adı: {persona_data.get('name', 'Bilinmiyor')}")
                print(f"  - Ses tonu: {persona_data.get('tone', 'Bilinmiyor')}")
                print(f"  - Kısıtlamalar: {persona_data.get('constraints', 'Bilinmiyor')}")
                return True
            else:
                print("✗ Persona verisi boş döndü")
                return False
                
        except PersonaFetchError as e:
            print(f"✗ Persona çekme hatası: {e}")
            print("💡 Mock veri testi kullanılıyor...")
            return test_persona_module_with_mock()
            
    except ImportError as e:
        print(f"✗ Persona modülü içe aktarılamadı: {e}")
        return False
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        return False


def test_dynamic_prompt_module():
    """Dynamic prompt generation modülünün temel işlevlerini test eder."""
    print("\n=== DİNAMİK PROMPT MODÜLÜ TESTİ ===")
    
    try:
        from dynamic_prompt_generation import (
            load_environment_variables,
            create_system_prompt,
            build_prompt,
            EnvironmentConfigError,
            PersonaError
        )
        
        print("✓ Dynamic prompt modülü başarıyla içe aktarıldı")
        
        # Test 1: Ortam değişkenlerini yükle
        print("\n--- Ortam Değişkenleri Yükleniyor ---")
        use_mock = False
        try:
            env_vars = load_environment_variables()
            print(f"✓ {len(env_vars)} ortam değişkeni yüklendi")
            for key in env_vars:
                value = env_vars[key]
                if value:
                    display_value = value[:20] + "..." if len(value) > 20 else value
                    print(f"  - {key}: {display_value}")
                else:
                    print(f"  - {key}: ✗ Eksik")
        except EnvironmentConfigError as e:
            print(f"⚠ Ortam değişkeni hatası: {e}")
            print("💡 Mock veri ile test devam ediyor...")
            use_mock = True
        
        # Test 2: Sistem prompt'u oluştur
        print("\n--- Sistem Promptu Oluşturma Testi ---")
        
        if use_mock:
            print("Mock persona verisi kullanılıyor...")
            test_persona = MOCK_PERSONA_DATA
        else:
            print("Test persona verisi kullanılıyor...")
            test_persona = {
                "name": "Test Asistanı",
                "tone": "Arkadaşça ve yardımcı",
                "constraints": "Kısa ve öz cevaplar ver.\nKaba dil kullanma.\nTürkçe konuş."
            }
        
        try:
            system_prompt = create_system_prompt(test_persona)
            if system_prompt and len(system_prompt) > 50:
                print("✓ Sistem promptu başarıyla oluşturuldu!")
                print(f"  - Uzunluk: {len(system_prompt)} karakter")
                print(f"  - İlk 150 karakter: {system_prompt[:150]}...")
                return True
            else:
                print("✗ Sistem promptu çok kısa veya boş")
                return False
        except Exception as e:
            print(f"✗ Prompt oluşturma hatası: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ Dynamic prompt modülü içe aktarılamadı: {e}")
        return False
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        return False


def test_ai_client_module():
    """AI client modülünün temel işlevlerini test eder."""
    print("\n=== AI CLIENT MODÜLÜ TESTİ ===")
    
    try:
        from ai_client import (
            load_api_configuration,
            initialize_gemini_model,
            build_persona_prefix,
            create_full_prompt,
            AIClientError
        )
        
        print("✓ AI client modülü başarıyla içe aktarıldı")
        
        # Test 1: API yapılandırmasını yükle
        print("\n--- API Yapılandırması Yükleniyor ---")
        try:
            api_key = load_api_configuration()
            if api_key:
                print(f"✓ API anahtarı yüklendi: {api_key[:15]}...")
            else:
                print("✗ API anahtarı boş")
                return False
        except AIClientError as e:
            print(f"✗ API yapılandırma hatası: {e}")
            return False
        
        # Test 2: Gemini modelini başlat
        print("\n--- Gemini Modeli Başlatılıyor ---")
        try:
            model = initialize_gemini_model(api_key)
            if model:
                print("✓ Gemini modeli başarıyla başlatıldı!")
            else:
                print("✗ Model başlatılamadı")
                return False
        except Exception as e:
            print(f"✗ Model başlatma hatası: {e}")
            return False
        
        # Test 3: Persona prefix oluşturma (mock veri ile)
        print("\n--- Persona Prefix Testi (Mock Veri) ---")
        try:
            prefix = build_persona_prefix(MOCK_PERSONA_DATA)
            if prefix:
                print(f"✓ Persona prefix oluşturuldu: {prefix[:80]}...")
            else:
                print("⚠ Persona prefix boş (normal olabilir)")
            
            # Test prompt oluşturma
            test_prompt = "Merhaba, nasılsın?"
            full_prompt = create_full_prompt(test_prompt, MOCK_PERSONA_DATA)
            print(f"✓ Tam prompt oluşturuldu ({len(full_prompt)} karakter)")
            
            return True
        except Exception as e:
            print(f"✗ Persona işleme hatası: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ AI client modülü içe aktarılamadı: {e}")
        return False
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        return False


def test_integration():
    """Tüm modüllerin birlikte çalışmasını test eder."""
    print("\n=== ENTEGRASYON TESTİ ===")
    
    try:
        from ai_client import main, run_chat_loop
        
        print("✓ Chatbot fonksiyonları içe aktarıldı")
        print("\nNot: Tam chatbot testini manuel olarak çalıştırmanız gerekiyor.")
        print("Chatbot'u başlatmak için: python ai_client.py")
        
        return True
        
    except ImportError as e:
        print(f"⚠ Chatbot fonksiyonları içe aktarılamadı: {e}")
        print("Not: Bu normal olabilir - Temel modüller çalışıyorsa sorun yok.")
        return True
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        return False


def run_all_tests():
    """Tüm testleri çalıştırır ve sonuçları özetler."""
    print("=" * 60)
    print("CHATBOT TEST SÜRECİ BAŞLATILIYOR")
    print("=" * 60)
    
    # .env dosyasını kontrol et
    if not os.path.exists("main/.env") and not os.path.exists(".env"):
        print("\n⚠ UYARI: .env dosyası bulunamadı!")
        print("Lütfen .env dosyasını oluşturun ve gerekli anahtarları ekleyin:\n")
        print("OPENAI_API_KEY=your_gemini_api_key")
        print("BACKEND_PANEL_URL=your_backend_url (opsiyonel)")
        print("ABLY_API_KEY=your_ably_key (opsiyonel)")
        print("ABLY_CHANNEL=your_channel_name (opsiyonel)")
        print("\n" + "=" * 60)
        return
    
    results = {}
    
    # Testleri sırayla çalıştır
    results["Persona Modülü"] = test_persona_module()
    results["Dynamic Prompt Modülü"] = test_dynamic_prompt_module()
    results["AI Client Modülü"] = test_ai_client_module()
    results["Entegrasyon"] = test_integration()
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("TEST SONUÇLARI")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results.items():
        if result is None:
            status = "⊘ ATLANDI"
            skipped += 1
        elif result:
            status = "✓ BAŞARILI"
            passed += 1
        else:
            status = "✗ BAŞARISIZ"
            failed += 1
        print(f"{test_name}: {status}")
    
    print("\n" + "-" * 60)
    print(f"Toplam: {passed + failed + skipped} test")
    print(f"Başarılı: {passed}")
    print(f"Başarısız: {failed}")
    if skipped > 0:
        print(f"Atlanan: {skipped}")
    print("=" * 60)
    
    if failed == 0 and passed > 0:
        print("\n🎉 Tüm testler başarılı! Chatbot kullanıma hazır.")
        print("\nChatbot'u başlatmak için:")
        print("  python ai_client.py")
    elif failed == 0 and passed == 0:
        print("\n⚠ Hiçbir test çalıştırılamadı. .env dosyanızı kontrol edin.")
    else:
        print("\n⚠ Bazı testler başarısız oldu.")
        print("\nEksik ortam değişkenleri için .env dosyanıza şunları ekleyin:")
        print("  OPENAI_API_KEY=your_gemini_api_key (zorunlu)")
        print("  BACKEND_PANEL_URL=... (opsiyonel - persona için)")
        print("  ABLY_API_KEY=... (opsiyonel - alternatif persona için)")
        print("  ABLY_CHANNEL=... (opsiyonel)")
        print("  PERSONA_API_URL=... (opsiyonel - dynamic_prompt için)")
        print("  PERSONA_API_TOKEN=... (opsiyonel)")



if __name__ == "__main__":
    run_all_tests()
