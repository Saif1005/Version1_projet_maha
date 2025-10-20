"""
Client pour l'API LinkedIn
Fichier: mcp_servers/linkedin_server/utils/api_client.py
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional
from utils.auth import LinkedInAuth


class LinkedInAPIClient:
    """Client pour interagir avec l'API LinkedIn"""
    
    def __init__(self, auth: LinkedInAuth):
        self.auth = auth
        from config import LinkedInConfig
        self.base_url = LinkedInConfig.API_BASE_URL
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Effectue une requête à l'API LinkedIn"""
        url = f"{self.base_url}/{endpoint}"
        headers = self.auth.get_headers()
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        return response.json()
    
    def get_my_profile(self) -> Dict:
        """Récupère le profil de l'utilisateur authentifié"""
        try:
            profile = self._make_request("GET", "me")
            
            # Enrichir avec l'email si disponible
            try:
                email_data = self._make_request("GET", "emailAddress?q=members&projection=(elements*(handle~))")
                email = email_data.get("elements", [{}])[0].get("handle~", {}).get("emailAddress")
                profile["email"] = email
            except:
                profile["email"] = None
            
            profile["retrieved_at"] = datetime.now().isoformat()
            return profile
            
        except Exception as e:
            raise Exception(f"Erreur récupération profil: {e}")
    
    def search_people(self, keywords: str, limit: int = 10) -> List[Dict]:
        """
        Recherche des personnes sur LinkedIn
        Note: Cette fonctionnalité nécessite un accès LinkedIn Partner
        """
        try:
            params = {
                "q": "people",
                "keywords": keywords,
                "count": limit
            }
            
            results = self._make_request("GET", "search", params=params)
            
            people = []
            for element in results.get("elements", []):
                people.append({
                    "id": element.get("id"),
                    "firstName": element.get("firstName"),
                    "lastName": element.get("lastName"),
                    "headline": element.get("headline"),
                    "retrieved_at": datetime.now().isoformat()
                })
            
            return people
            
        except Exception as e:
            raise Exception(f"Erreur recherche personnes: {e}")
    
    def get_user_posts(self, user_urn: str, limit: int = 50) -> List[Dict]:
        """Récupère les posts d'un utilisateur"""
        try:
            params = {
                "q": "author",
                "author": user_urn,
                "count": limit
            }
            
            results = self._make_request("GET", "ugcPosts", params=params)
            
            posts = []
            for element in results.get("elements", []):
                posts.append({
                    "id": element.get("id"),
                    "author": element.get("author"),
                    "created": element.get("created", {}).get("time"),
                    "text": element.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text"),
                    "likes": element.get("likesSummary", {}).get("totalLikes", 0),
                    "comments": element.get("commentsSummary", {}).get("totalComments", 0),
                    "retrieved_at": datetime.now().isoformat()
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Erreur récupération posts: {e}")
    
    def get_connections(self, start: int = 0, count: int = 100) -> List[Dict]:
        """Récupère les connexions de l'utilisateur"""
        try:
            params = {
                "q": "viewer",
                "start": start,
                "count": count
            }
            
            results = self._make_request("GET", "connections", params=params)
            
            connections = []
            for element in results.get("elements", []):
                connections.append({
                    "id": element.get("id"),
                    "firstName": element.get("firstName"),
                    "lastName": element.get("lastName"),
                    "headline": element.get("headline"),
                    "connectedAt": element.get("connectedAt"),
                    "retrieved_at": datetime.now().isoformat()
                })
            
            return connections
            
        except Exception as e:
            raise Exception(f"Erreur récupération connexions: {e}")
    
    def get_company_info(self, company_id: str) -> Dict:
        """Récupère les informations d'une entreprise"""
        try:
            company = self._make_request("GET", f"organizations/{company_id}")
            
            return {
                "id": company.get("id"),
                "name": company.get("name"),
                "description": company.get("description"),
                "industry": company.get("industries", []),
                "employeeCount": company.get("staffCount"),
                "followers": company.get("followersCount"),
                "website": company.get("website"),
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erreur info entreprise: {e}")
    
    def get_company_posts(self, company_id: str, limit: int = 50) -> List[Dict]:
        """Récupère les posts d'une entreprise"""
        try:
            params = {
                "q": "author",
                "author": f"urn:li:organization:{company_id}",
                "count": limit
            }
            
            results = self._make_request("GET", "ugcPosts", params=params)
            
            posts = []
            for element in results.get("elements", []):
                posts.append({
                    "id": element.get("id"),
                    "author": element.get("author"),
                    "created": element.get("created", {}).get("time"),
                    "text": element.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text"),
                    "likes": element.get("likesSummary", {}).get("totalLikes", 0),
                    "comments": element.get("commentsSummary", {}).get("totalComments", 0),
                    "retrieved_at": datetime.now().isoformat()
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Erreur posts entreprise: {e}")
    
    def share_post(self, text: str, visibility: str = "PUBLIC") -> Dict:
        """Partage un post sur LinkedIn"""
        try:
            payload = {
                "author": f"urn:li:person:{self.get_my_profile().get('id')}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            result = self._make_request("POST", "ugcPosts", json=payload)
            return result
            
        except Exception as e:
            raise Exception(f"Erreur partage post: {e}")