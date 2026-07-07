class ToneTransformer:
    """Handles tone transformation for copywriting"""
    
    def __init__(self):
        self.tone_mappings = {
            'professional': {
                'style': 'formal, business-like, corporate',
                'keywords': ['professional', 'expertise', 'solution', 'value']
            },
            'casual': {
                'style': 'friendly, conversational, relaxed',
                'keywords': ['hey', 'awesome', 'cool', 'great']
            },
            'persuasive': {
                'style': 'convincing, compelling, urgent',
                'keywords': ['discover', 'transform', 'achieve', 'unlock']
            },
            'informative': {
                'style': 'educational, factual, clear',
                'keywords': ['learn', 'understand', 'know', 'insight']
            },
            'emotional': {
                'style': 'heartfelt, touching, inspiring',
                'keywords': ['feel', 'believe', 'together', 'dream']
            },
            'humorous': {
                'style': 'funny, witty, entertaining',
                'keywords': ['hilarious', 'fun', 'laugh', 'joke']
            }
        }
    
    def transform_tone(self, text, target_tone):
        """
        Transform text to target tone
        For now returns text as-is since Gemini handles transformation
        """
        if target_tone in self.tone_mappings:
            # Add tone-specific keywords or adjustments
            tone_info = self.tone_mappings[target_tone]
            # This is a placeholder for additional transformations
            return text
        return text
    
    def get_available_tones(self):
        """Return list of available tones"""
        return list(self.tone_mappings.keys())
    
    def get_tone_description(self, tone):
        """Get description of a specific tone"""
        return self.tone_mappings.get(tone, {}).get('style', 'No description available')