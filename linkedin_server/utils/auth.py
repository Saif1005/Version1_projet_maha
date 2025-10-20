"""
Gestion de l'authentification LinkedIn OAuth2
Fichier: mcp_servers/linkedin_server/utils/auth.py
"""

import requests
from urllib.parse import urlencode
from typing import Dict


class LinkedInAuth:
    """Gestionnaire d'authentification LinkedIn OAuth2"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        
        from config import LinkedInConfig
        self.auth_url = LinkedInConfig.AUTH_URL
        self.token_url = LinkedInConfig.TOKEN_URL
        self.scopes = LinkedInConfig.SCOPES
    
    def get_authorization_url(self, state: str = "random_state") -> str:
        """
        Génère l'URL d'autorisation OAuth2
        
        Args:
            state: Chaîne aléatoire pour la sécurité CSRF
            
        Returns:
            URL d'autorisation complète
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.scopes)
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """
        Échange le code d'autorisation contre un access token
        
        Args:
            authorization_code: Code d'autorisation OAuth2
            
        Returns:
            Dictionnaire contenant l'access token et les métadonnées
        """
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        
        return token_data
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Rafraîchit l'access token
        
        Args:
            refresh_token: Token de rafraîchissement
            
        Returns:
            Nouveau token data
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        
        return token_data
    
    def set_access_token(self, token: str):
        """Définit manuellement l'access token"""
        self.access_token = token
    
    def get_headers(self) -> Dict:
        """Retourne les headers pour les requêtes API"""
        if not self.access_token:
            raise ValueError("Access token non configuré. Authentifiez-vous d'abord.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }