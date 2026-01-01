import json
import os

# Dosya yollarını ayarla
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WHITELIST_PATH = os.path.join(CURRENT_DIR, 'data', 'whitelist.json')

class WhitelistManager:
    def __init__(self):
        self.file_path = WHITELIST_PATH
        self._load_whitelist()

    def _load_whitelist(self):
        """JSON dosyasını yükler, yoksa oluşturur."""
        if not os.path.exists(self.file_path):
            self.data = {"allowed_ips": [], "allowed_paths": []}
            self._save_whitelist()
        else:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def _save_whitelist(self):
        """Verileri dosyaya kaydeder."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
        print("Whitelist güncellendi.")

    def add_ip(self, ip_address):
        """Güvenli bir IP ekler."""
        if ip_address not in self.data["allowed_ips"]:
            self.data["allowed_ips"].append(ip_address)
            self._save_whitelist()
            print(f" IP Eklendi: {ip_address}")
        else:
            print(f"Bu IP zaten listede: {ip_address}")

    def add_path(self, path):
        """Güvenli bir URL yolu ekler."""
        if path not in self.data["allowed_paths"]:
            self.data["allowed_paths"].append(path)
            self._save_whitelist()
            print(f"Yol Eklendi: {path}")

    def is_whitelisted(self, log_entry):
        """
        Log içinde güvenli bir IP veya yol geçiyor mu diye bakar.
        Basit bir string araması yapar.
        """
        # IP Kontrolü
        for ip in self.data["allowed_ips"]:
            if ip in log_entry:
                return True, f"Güvenli IP tespiti: {ip}"
        
        # Yol Kontrolü
        for path in self.data["allowed_paths"]:
            if path in log_entry:
                return True, f"Güvenli Yol tespiti: {path}"
                
        return False, None

# Test için (Doğrudan çalıştırılırsa)
if __name__ == "__main__":
    wm = WhitelistManager()
    print("--- Whitelist Yönetici Paneli ---")
    secim = input("1- IP Ekle\n2- Yol Ekle\nSeçiminiz: ")
    
    if secim == "1":
        ip = input("IP Adresi girin: ")
        wm.add_ip(ip)
    elif secim == "2":
        yol = input("Yol (Path) girin: ")
        wm.add_path(yol)