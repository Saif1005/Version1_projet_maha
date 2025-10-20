"""
Client pour l'API Reddit via PRAW
Fichier: mcp_servers/reddit_server/utils/api_client.py
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import praw


class RedditAPIClient:
    """Client pour interagir avec l'API Reddit"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialise le client Reddit avec PRAW"""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def _extract_post_data(self, post, include_extra: bool = False) -> Dict:
        """Extrait les données d'un post Reddit"""
        base_data = {
            "id": post.id,
            "title": post.title,
            "selftext": post.selftext,
            "author": str(post.author) if post.author else "[deleted]",
            "subreddit": post.subreddit.display_name,
            "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
            "score": post.score,
            "upvote_ratio": post.upvote_ratio,
            "num_comments": post.num_comments,
            "permalink": post.permalink,
            "url": post.url,
            "is_self": post.is_self,
            "link_flair_text": post.link_flair_text,
            "retrieved_at": datetime.now().isoformat()
        }
        
        if include_extra:
            base_data.update({
                "is_video": post.is_video,
                "over_18": post.over_18
            })
        
        return base_data
    
    def search_posts(self, query: str, subreddit: Optional[str] = None, 
                    sort: str = "relevance", limit: int = 10) -> List[Dict]:
        """Recherche des posts sur Reddit"""
        try:
            if subreddit:
                sub = self.reddit.subreddit(subreddit)
                posts = sub.search(query, sort=sort, limit=limit)
            else:
                posts = self.reddit.subreddit("all").search(query, sort=sort, limit=limit)
            
            return [self._extract_post_data(post) for post in posts]
            
        except Exception as e:
            raise Exception(f"Erreur recherche posts: {e}")
    
    def get_subreddit_posts(self, subreddit: str, sort: str = "hot", 
                           limit: int = 25, time_filter: str = "day") -> List[Dict]:
        """Récupère les posts d'un subreddit"""
        try:
            sub = self.reddit.subreddit(subreddit)
            
            if sort == "hot":
                posts = sub.hot(limit=limit)
            elif sort == "new":
                posts = sub.new(limit=limit)
            elif sort == "top":
                posts = sub.top(time_filter=time_filter, limit=limit)
            else:
                posts = sub.rising(limit=limit)
            
            return [self._extract_post_data(post, include_extra=True) for post in posts]
            
        except Exception as e:
            raise Exception(f"Erreur collecte subreddit: {e}")
    
    def get_post_with_comments(self, post_id: str, limit: int = 100) -> Tuple[Dict, List[Dict]]:
        """Récupère un post avec ses commentaires"""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            post_data = self._extract_post_data(submission)
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    comments.append({
                        "id": comment.id,
                        "post_id": post_id,
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                        "parent_id": comment.parent_id,
                        "retrieved_at": datetime.now().isoformat()
                    })
            
            return post_data, comments
            
        except Exception as e:
            raise Exception(f"Erreur collecte commentaires: {e}")
    
    def get_user_data(self, username: str, include_posts: bool = True, 
                     include_comments: bool = True, limit: int = 100) -> Dict:
        """Récupère les données d'un utilisateur"""
        try:
            user = self.reddit.redditor(username)
            
            user_data = {
                "username": username,
                "comment_karma": user.comment_karma,
                "link_karma": user.link_karma,
                "created_utc": datetime.fromtimestamp(user.created_utc).isoformat(),
                "is_gold": user.is_gold,
                "retrieved_at": datetime.now().isoformat(),
                "posts": [],
                "comments": []
            }
            
            if include_posts:
                for submission in user.submissions.new(limit=limit):
                    user_data["posts"].append({
                        "id": submission.id,
                        "title": submission.title,
                        "selftext": submission.selftext,
                        "subreddit": submission.subreddit.display_name,
                        "score": submission.score,
                        "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat()
                    })
            
            if include_comments:
                for comment in user.comments.new(limit=limit):
                    if hasattr(comment, 'body'):
                        user_data["comments"].append({
                            "id": comment.id,
                            "body": comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
                            "subreddit": comment.subreddit.display_name,
                            "score": comment.score,
                            "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat()
                        })
            
            return user_data
            
        except Exception as e:
            raise Exception(f"Erreur données utilisateur: {e}")
    
    def get_subreddit_info(self, subreddit: str) -> Dict:
        """Récupère les informations d'un subreddit"""
        try:
            sub = self.reddit.subreddit(subreddit)
            
            return {
                "name": sub.display_name,
                "title": sub.title,
                "description": sub.public_description,
                "subscribers": sub.subscribers,
                "created_utc": datetime.fromtimestamp(sub.created_utc).isoformat(),
                "over18": sub.over18,
                "subreddit_type": sub.subreddit_type,
                "url": sub.url,
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erreur info subreddit: {e}")