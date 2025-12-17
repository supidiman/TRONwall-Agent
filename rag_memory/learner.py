import json
import os
import re

class AutoLearner:
    def __init__(self):
        # Dosya yolunu dinamik olarak bul
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, 'data', 'attack_signatures.json')

    def load_db(self):
        """Mevcut veritabanını yükler."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_db(self, data):
        """Veritabanını güncelleyip kaydeder."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Hafıza güncellendi: Yeni saldırı veritabanına yazıldı.")
            return True
        except Exception as e:
            print(f"Kayıt Hatası: {e}")
            return False

    def learn_new_attack(self, attack_type, log_pattern, risk_level="HIGH"):
        """
        AI'ın tespit ettiği yeni saldırıyı JSON'a ekler.
        """
        data = self.load_db()

        # 1. Regex'e Çevir (Güvenlik İçin)
        safe_pattern = re.escape(log_pattern)

        # 2. Mükerrer Kontrolü (Aynı desen zaten var mı?)
        for entry in data:
            if safe_pattern in entry.get('regex_patterns', []):
                print(f"Bilgi: Bu saldırı deseni zaten {entry['id']} altında kayıtlı.")
                return entry

        # 3. Yeni ID Üretme (A006, A007...)
        existing_ids = [int(item['id'][1:]) for item in data if item['id'].startswith('A')]
        new_id_num = max(existing_ids) + 1 if existing_ids else 1
        new_id = f"A{new_id_num:03d}"

        # 4. Yeni Kayıt Oluşturma
        new_entry = {
            "id": new_id,
            "name": attack_type,
            "description": f"AI tarafından otomatik öğrenilen {attack_type} saldırısı.",
            "risk_level": risk_level,
            "regex_patterns": [safe_pattern],
            "rule_template": {
                "action": "block_ip",
                "reason": f"Auto-learned threat: {attack_type}"
            }
        }

        # 5. Listeye Ekle ve Kaydet
        data.append(new_entry)
        self.save_db(data)
        
        print(f"ÖĞRENİLDİ: {attack_type} (ID: {new_id}) hafızaya kazındı!")
        return new_entry