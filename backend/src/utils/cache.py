"""Cache utility for centralized cache key management and invalidation"""
from functools import wraps

class CacheKeys:
    """Centralized cache key definitions"""
    
    @staticmethod
    def chat_movies(member_id):
        return f"chat_movies:{member_id}"
    
    @staticmethod
    def recommendations(member_id, trigger):
        return f"rec:{member_id}:{trigger}"


class CacheManager:
    """Handles cache operations across the application"""
    
    def __init__(self, cache):
        self.cache = cache
    
    def clear_chat_context(self, member_id):
        """Clear chat-related caches when conversation ends"""
        if self.cache:
            self.cache.delete(CacheKeys.chat_movies(member_id))
    
    def clear_all_member_caches(self, member_id):
        """Clear all caches for a member (nuclear option)"""
        if self.cache:
            # Clear chat movies
            self.cache.delete(CacheKeys.chat_movies(member_id))
            
            # Clear all recommendation caches
            from services import RecommendationTrigger
            for trigger in RecommendationTrigger:
                if trigger != RecommendationTrigger.CHATBOT_MESSAGE:
                    self.cache.delete(CacheKeys.recommendations(member_id, trigger.value))

def cache_recommendations(func):
    """Decorator to cache recommendation results"""
    def wrapper(self, trigger, params=None):
        # Skip caching for chatbot (conversational)
        from services import RecommendationTrigger
        if trigger == RecommendationTrigger.CHATBOT_MESSAGE:
            return func(self, trigger, params)
        
        # Build cache key
        cache_key = CacheKeys.recommendations(self.member_id, trigger.value)
        
        # Try cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Execute function
        result = func(self, trigger, params)
        
        # Store in cache
        if self.cache:
            self.cache.set(cache_key, result, timeout=60*60) # one hour
        
        return result
    
    return wrapper

def cache_available_movies(func):
    """Decorator to cache available movies for chat continuity"""
    def wrapper(self, message):
        # Build cache key
        cache_key = CacheKeys.chat_movies(self.member_id)
        
        # Try cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Execute function
        result = func(self, message)
        
        # Store in cache with chat expiry TTL
        if self.cache:
            from config import Config
            ttl = Config.CHAT_EXPIRY_MINUTES * 60  # Convert to seconds
            self.cache.set(cache_key, result, timeout=ttl)
        
        return result
    
    return wrapper