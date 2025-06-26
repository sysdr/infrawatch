import re
import math
import zxcvbn
from typing import Dict, List, Tuple

class PasswordStrengthValidator:
    def __init__(self):
        self.common_patterns = [
            r'123456',
            r'password',
            r'qwerty',
            r'abc123',
            r'admin'
        ]
        self.keyboard_patterns = [
            r'qwertyuiop',
            r'asdfghjkl',
            r'zxcvbnm'
        ]

    def calculate_entropy(self, password: str) -> float:
        """Calculate password entropy using character set diversity"""
        charset_size = 0
        
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'[0-9]', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
            
        if charset_size == 0:
            return 0
            
        return len(password) * math.log2(charset_size)

    def check_common_patterns(self, password: str) -> List[str]:
        """Check for common weak patterns"""
        violations = []
        
        for pattern in self.common_patterns:
            if re.search(pattern, password.lower()):
                violations.append(f"Contains common pattern: {pattern}")
                
        return violations

    def check_keyboard_patterns(self, password: str) -> List[str]:
        """Check for keyboard walking patterns"""
        violations = []
        password_lower = password.lower()
        
        for pattern in self.keyboard_patterns:
            for i in range(len(pattern) - 2):
                substring = pattern[i:i+3]
                if substring in password_lower:
                    violations.append(f"Contains keyboard pattern: {substring}")
                    
        return violations

    def validate_strength(self, password: str) -> Dict:
        """Comprehensive password strength validation"""
        
        # Basic requirements
        requirements = {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'numbers': bool(re.search(r'[0-9]', password)),
            'special_chars': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        # Calculate entropy
        entropy = self.calculate_entropy(password)
        
        # Use zxcvbn for advanced analysis
        zxcvbn_result = zxcvbn.zxcvbn(password)
        
        # Check patterns
        pattern_violations = []
        pattern_violations.extend(self.check_common_patterns(password))
        pattern_violations.extend(self.check_keyboard_patterns(password))
        
        # Determine overall strength
        basic_score = sum(requirements.values())
        entropy_score = min(entropy / 50, 4)  # Normalize to 0-4
        zxcvbn_score = zxcvbn_result['score']
        pattern_penalty = len(pattern_violations)
        
        final_score = max(0, (basic_score + entropy_score + zxcvbn_score - pattern_penalty) / 3)
        
        strength_levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
        strength = strength_levels[min(int(final_score), 4)]
        
        return {
            'valid': final_score >= 2.5 and len(pattern_violations) == 0,
            'strength': strength,
            'score': round(final_score, 2),
            'entropy': round(entropy, 2),
            'requirements': requirements,
            'violations': pattern_violations,
            'suggestions': zxcvbn_result.get('feedback', {}).get('suggestions', []),
            'crack_time': zxcvbn_result.get('crack_times_display', {})
        }
