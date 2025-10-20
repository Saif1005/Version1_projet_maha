#!/usr/bin/env python3
"""
Script pour obtenir un Access Token LinkedIn
"""
import os
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

# Charger depuis .env
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = ["r_liteprofile", "r_emailaddress", "w_member_social"]

authorization_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>Succès!</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #0077B5;">✅ Autorisation réussie!</h1>
                <p>Vous pouvez fermer cette fenêtre.</p>
                <p>Retournez à votre terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    print("="*70)
    print("🔐 OBTENIR UN ACCESS TOKEN LINKEDIN")
    print("="*70)
    
    # Construire l'URL d'autorisation
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random123",
        "scope": " ".join(SCOPES)
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    
    print("\n📌 Étape 1: Autorisation")
    print("\nOuverture du navigateur dans 3 secondes...")
    print(f"\nSi rien ne s'ouvre, visitez manuellement:\n{auth_url}\n")
    
    import time
    time.sleep(3)
    webbrowser.open(auth_url)
    
    print("📌 Étape 2: En attente de la redirection...")
    print(f"Serveur local démarré sur {REDIRECT_URI}\n")
    
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    
    while authorization_code is None:
        server.handle_request()
    
    print("✅ Code d'autorisation reçu!")
    
    print("\n📌 Étape 3: Échange du code contre un token...")
    
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", "N/A")
        
        print("\n" + "="*70)
        print("🎉 SUCCÈS!")
        print("="*70)
        print(f"\n📝 Votre Access Token:")
        print(f"\n{access_token}")
        print(f"\n⏱️  Expire dans: {expires_in} secondes (~60 jours)")
        
        # Mettre à jour le .env
        print("\n💾 Mise à jour de .env...")
        
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Remplacer la ligne ACCESS_TOKEN
        if 'LINKEDIN_ACCESS_TOKEN=' in env_content:
            lines = env_content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                    new_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')
                else:
                    new_lines.append(line)
            env_content = '\n'.join(new_lines)
        else:
            env_content += f'\nLINKEDIN_ACCESS_TOKEN={access_token}\n'
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Fichier .env mis à jour automatiquement!")
        print("\n" + "="*70)
        print("🚀 PRÊT À LANCER LE SERVEUR!")
        print("="*70)
        print("\nExécutez maintenant:")
        print("  python server.py")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        if hasattr(e, 'response'):
            print(f"Détails: {e.response.text}")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Erreur: CLIENT_ID et CLIENT_SECRET doivent être configurés dans .env")
    else:
        main()