import json
import os
import re  # Regex kütüphanesini ekledik

class KnowledgeBase:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(current_dir, 'data', 'attack_signatures.json')
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                print("Hafıza veritabanı yüklendi.")
                return json.load(f)
        except FileNotFoundError:
            print("HATA: attack_signatures.json bulunamadı!")
            return []
        except json.JSONDecodeError:
            print("HATA: JSON formatı bozuk!")
            return []

    def search_knowledge(self, log_line):
        """
        Log satırını Regex desenleriyle tarar.
        Advanced Mod: Sadece kelime değil, kalıp eşleştirir.
        """
        found_matches = []
        
        for attack in self.data:
            # JSON'daki 'regex_patterns' listesini geziyoruz
            for pattern in attack.get('regex_patterns', []):
                try:
                    # re.search ile regex taraması yapıyoruz
                    # re.IGNORECASE bayrağı büyük/küçük harfi önemsemez
                    if re.search(pattern, log_line, re.IGNORECASE):
                        
                        found_matches.append({
                            "attack_name": attack['name'],
                            "risk_level": attack['risk_level'],
                            "matched_pattern": pattern, # Hangi kalıba yakalandı?
                            "suggested_rule": attack['rule_template']
                        })
                        # Bir saldırı türünden 1 tane yakalamak yeterli, diğer desenlere bakma
                        break 
                except re.error:
                    print(f"Hatalı Regex Deseni: {pattern}")
                    continue
        
        return found_matches

# --- GELİŞMİŞ TEST ALANI ---
if __name__ == "__main__":
    kb = KnowledgeBase()
    
    # 3 Farklı Zorlu Senaryo Testi
    
    print("\n--- TEST 1: Gizlenmiş SQL Injection ---")
    # Hacker 'SELECT' yerine 'SeLeCt' yazmış ve boşlukları karıştırmış
    log1 = 'GET /users.php?id=1 UNION   SeLeCt * FROM users'
    res1 = kb.search_knowledge(log1)
    if res1: print(f"Yakalandı: {res1[0]['attack_name']}")
    else: print("Kaçırıldı!")

    print("\n--- TEST 2: Path Traversal ---")
    log2 = 'GET /download.php?file=../../../../etc/passwd'
    res2 = kb.search_knowledge(log2)
    if res2: print(f"Yakalandı: {res2[0]['attack_name']}")
    else: print("Kaçırıldı!")

    print("\n--- TEST 3: Masum Trafik ---")
    log3 = 'GET /images/logo.png HTTP/1.1'
    res3 = kb.search_knowledge(log3)
    if res3: print(f"Yanlış Alarm: {res3[0]['attack_name']}")
    else: print("Temiz Trafik (Doğru Tepki)")