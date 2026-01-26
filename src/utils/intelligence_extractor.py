import re
from typing import List, Set
from src.models.schemas import ExtractedIntelligence, Message


class IntelligenceExtractor:
    """Extracts structured intelligence from conversations"""
    
    # Regex patterns for extraction
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'
    UPI_PATTERN = r'\b[\w\.-]+@[\w\.-]+\b'
    PHONE_PATTERN = r'\+?\d{10,15}'
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    # Common scam keywords
    SCAM_KEYWORDS = [
        'urgent', 'verify', 'suspend', 'block', 'immediate', 'account',
        'security', 'update', 'confirm', 'click', 'link', 'prize',
        'winner', 'congratulations', 'claim', 'expires', 'limited',
        'act now', 'verify now', 'update now', 'confirm now', 'kyc',
        'otp', 'password', 'pin', 'cvv', 'card number', 'expiry'
    ]
    
    def __init__(self):
        self.extracted_data = ExtractedIntelligence()
    
    def extract_from_message(self, message: str) -> ExtractedIntelligence:
        """Extract intelligence from a single message"""
        intel = ExtractedIntelligence()
        
        # Extract bank accounts
        bank_accounts = re.findall(self.BANK_ACCOUNT_PATTERN, message)
        intel.bankAccounts = list(set(bank_accounts))
        
        # Extract UPI IDs
        upi_ids = re.findall(self.UPI_PATTERN, message)
        # Filter out email-like patterns that aren't UPI
        upi_ids = [uid for uid in upi_ids if any(provider in uid.lower() for provider in 
                   ['paytm', 'phonepe', 'gpay', 'okaxis', 'ybl', 'axl', 'ibl', 'okhdfcbank', 'oksbi'])]
        intel.upiIds = list(set(upi_ids))
        
        # Extract phone numbers
        phone_numbers = re.findall(self.PHONE_PATTERN, message)
        intel.phoneNumbers = list(set(phone_numbers))
        
        # Extract URLs (potential phishing links)
        urls = re.findall(self.URL_PATTERN, message)
        intel.phishingLinks = list(set(urls))
        
        # Extract suspicious keywords
        message_lower = message.lower()
        found_keywords = [kw for kw in self.SCAM_KEYWORDS if kw in message_lower]
        intel.suspiciousKeywords = list(set(found_keywords))
        
        return intel
    
    def extract_from_conversation(self, messages: List[Message]) -> ExtractedIntelligence:
        """Extract intelligence from entire conversation"""
        all_intel = ExtractedIntelligence()
        
        for msg in messages:
            if msg.sender == "scammer":
                intel = self.extract_from_message(msg.text)
                
                # Merge all extracted data
                all_intel.bankAccounts.extend(intel.bankAccounts)
                all_intel.upiIds.extend(intel.upiIds)
                all_intel.phoneNumbers.extend(intel.phoneNumbers)
                all_intel.phishingLinks.extend(intel.phishingLinks)
                all_intel.suspiciousKeywords.extend(intel.suspiciousKeywords)
        
        # Remove duplicates
        all_intel.bankAccounts = list(set(all_intel.bankAccounts))
        all_intel.upiIds = list(set(all_intel.upiIds))
        all_intel.phoneNumbers = list(set(all_intel.phoneNumbers))
        all_intel.phishingLinks = list(set(all_intel.phishingLinks))
        all_intel.suspiciousKeywords = list(set(all_intel.suspiciousKeywords))
        
        return all_intel
    
    def merge_intelligence(self, existing: ExtractedIntelligence, new: ExtractedIntelligence) -> ExtractedIntelligence:
        """Merge two intelligence objects"""
        merged = ExtractedIntelligence()
        
        merged.bankAccounts = list(set(existing.bankAccounts + new.bankAccounts))
        merged.upiIds = list(set(existing.upiIds + new.upiIds))
        merged.phoneNumbers = list(set(existing.phoneNumbers + new.phoneNumbers))
        merged.phishingLinks = list(set(existing.phishingLinks + new.phishingLinks))
        merged.suspiciousKeywords = list(set(existing.suspiciousKeywords + new.suspiciousKeywords))
        
        return merged
