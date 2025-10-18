"""Utility for calculating discussion power metrics"""
from config import Config

def get_discussion_power(member):
    """
    Calculate discussion power metrics for a member
    
    Args:
        member: Member model instance
        
    Returns:
        dict: Discussion power metrics
    """
    used = float(member.agent_usage)
    limit = Config.AGENT_USAGE_LIMIT
    remaining = limit - used
    percentage = (used / limit) * 100
    
    return {
        'used': used,
        'limit': limit,
        'remaining': remaining,
        'percentage': min(percentage, 100)
    }