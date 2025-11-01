import os
from dotenv import load_dotenv
from persona import fetch_persona

TEST_SYSTEM_PROMPT = """
SEN BİR YARDIMCI ASİSTANSIN.

### KİMLİK VE ROL ###
Senin adın: {name}
Kullanıcılarla konuşurken kullanman gereken ses tonu: {tone}

### DAVRANIŞ KURALLARI VE KISITLAMALAR ###
Aşağıdaki kurallara MUTLAKA uymalısın:
{constraints_list}

### GÖREV ###
Bu kimlik ve kurallara bağlı kalarak kullanıcının sorularını yanıtla.
"""

def build_prompt():
    load_dotenv()

    API_URL = os.getenv("PERSONA_API_URL")
    API_TOKEN = os.getenv("PERSONA_API_TOKEN")
    ABLY_KEY = os.getenv("ABLY_API_KEY")
    ABLY_CHANNEL_NAME = os.getenv("ABLY_CHANNEL")

    if not API_URL or not API_TOKEN or not ABLY_KEY or not ABLY_CHANNEL_NAME:
        print("Hata: Lütfen .env dosyanıza PERSONA_API_URL, PERSONA_API_TOKEN, ABLY_KEY, ABLY_CHANNEL_NAME değerlerini ekleyin.")
        return
    
    print("Persona verisi çekiliyor...")
    
    persona_config = fetch_persona(
        api_url=API_URL,
        token=API_TOKEN,
        ably_api_key=ABLY_KEY,
        ably_channel=ABLY_CHANNEL_NAME
    )

    if persona_config:
        print("\n=== BAŞARILI: Persona Yüklendi ===")
        try:
            name = persona_config["name"]
            tone = persona_config["tone"]
            constraints_list = persona_config["constraints"]

            formatted_constraints = "\n".join([f"- {rule}" for rule in constraints_list])

            system_prompt = TEST_SYSTEM_PROMPT.format(
                name=name,
                tone=tone,
                constraints_list=formatted_constraints
            )

            print("\n\n--- OLUŞTURULAN SYSTEM PROMPT ---")
            print(system_prompt)
            print("-----------------------------------")
        
        except KeyError as e:
            print(f"Hata: Persona verisi prompt'a dönüştürülürken bir anahtar bulunamadı: {e}")
            
    else:
        print("Persona verisi alınamadı, system prompt oluşturulamadı.")

if __name__ == "__main__":
    build_prompt()
