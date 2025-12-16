"""
Persona Veritabanı Modülü

Persona bilgilerini SQLite veritabanında saklar ve yönetir.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


# Veritabanı dosya yolu
DB_PATH = os.path.join(os.path.dirname(__file__), "personas.db")


class PersonaDBError(Exception):
    """Veritabanı hatalarını temsil eder."""
    pass


def init_database() -> None:
    """
    Veritabanını oluşturur ve tabloları hazırlar.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Personas tablosunu oluştur
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tone TEXT NOT NULL,
            constraints TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Veritabanı hazır: {DB_PATH}")


def create_persona(name: str, tone: str, constraints: str) -> int:
    """
    Yeni bir persona oluşturur ve veritabanına kaydeder.
    
    Parametreler:
        name: Persona adı
        tone: Konuşma tonu
        constraints: Kısıtlamalar
        
    Dönüş Değeri:
        int: Oluşturulan persona'nın ID'si
        
    Hatalar:
        PersonaDBError: Kayıt başarısız olursa
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO personas (name, tone, constraints, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, tone, constraints, now, now))
        
        persona_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return persona_id
        
    except sqlite3.Error as e:
        raise PersonaDBError(f"Persona kaydedilemedi: {e}")


def get_persona_by_id(persona_id: int) -> Optional[Dict[str, Any]]:
    """
    ID'ye göre persona getirir.
    
    Parametreler:
        persona_id: Persona ID'si
        
    Dönüş Değeri:
        Optional[Dict]: Persona bilgileri veya None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM personas WHERE id = ?
        """, (persona_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "tone": row["tone"],
                "constraints": row["constraints"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        
        return None
        
    except sqlite3.Error as e:
        raise PersonaDBError(f"Persona getirilemedi: {e}")


def get_all_personas() -> List[Dict[str, Any]]:
    """
    Tüm personaları listeler.
    
    Dönüş Değeri:
        List[Dict]: Persona listesi
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM personas ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        personas = []
        for row in rows:
            personas.append({
                "id": row["id"],
                "name": row["name"],
                "tone": row["tone"],
                "constraints": row["constraints"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        return personas
        
    except sqlite3.Error as e:
        raise PersonaDBError(f"Personalar listelenemedi: {e}")


def update_persona(persona_id: int, name: str, tone: str, constraints: str) -> bool:
    """
    Mevcut bir persona'yı günceller.
    
    Parametreler:
        persona_id: Güncellenecek persona ID'si
        name: Yeni persona adı
        tone: Yeni konuşma tonu
        constraints: Yeni kısıtlamalar
        
    Dönüş Değeri:
        bool: Güncelleme başarılıysa True
        
    Hatalar:
        PersonaDBError: Güncelleme başarısız olursa
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE personas
            SET name = ?, tone = ?, constraints = ?, updated_at = ?
            WHERE id = ?
        """, (name, tone, constraints, now, persona_id))
        
        updated = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return updated
        
    except sqlite3.Error as e:
        raise PersonaDBError(f"Persona güncellenemedi: {e}")


def delete_persona(persona_id: int) -> bool:
    """
    Bir persona'yı siler.
    
    Parametreler:
        persona_id: Silinecek persona ID'si
        
    Dönüş Değeri:
        bool: Silme başarılıysa True
        
    Hatalar:
        PersonaDBError: Silme başarısız olursa
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM personas WHERE id = ?
        """, (persona_id,))
        
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
        
    except sqlite3.Error as e:
        raise PersonaDBError(f"Persona silinemedi: {e}")


def list_personas_simple() -> None:
    """
    Tüm personaları basit formatta ekrana yazdırır.
    """
    personas = get_all_personas()
    
    if not personas:
        print("\n⚠️ Veritabanında persona bulunamadı.")
        return
    
    print("\n" + "="*60)
    print("KAYITLI PERSONALAR")
    print("="*60)
    
    for p in personas:
        print(f"\n[ID: {p['id']}] {p['name']}")
        print(f"  Ton: {p['tone']}")
        print(f"  Kısıtlamalar: {p['constraints'][:50]}...")
        print(f"  Oluşturulma: {p['created_at'][:10]}")


# Test fonksiyonu
def test_database():
    """
    Veritabanı fonksiyonlarını test eder.
    """
    print("🧪 Veritabanı testi başlatılıyor...\n")
    
    # Veritabanını başlat
    init_database()
    
    # Yeni persona oluştur
    print("\n--- Yeni Persona Oluşturuluyor ---")
    persona_id = create_persona(
        name="Test Asistanı",
        tone="Arkadaşça ve yardımcı",
        constraints="Kısa cevaplar ver\nTürkçe konuş\nKaba dil kullanma"
    )
    print(f"✓ Persona oluşturuldu (ID: {persona_id})")
    
    # Persona'yı getir
    print("\n--- Persona Getiriliyor ---")
    persona = get_persona_by_id(persona_id)
    if persona:
        print(f"✓ {persona['name']} bulundu")
        print(f"  Ton: {persona['tone']}")
    
    # Tüm personaları listele
    print("\n--- Tüm Personalar ---")
    list_personas_simple()
    
    print("\n✅ Test tamamlandı!")


if __name__ == "__main__":
    test_database()
