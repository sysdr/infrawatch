import os
import ast
import re
from typing import List, Dict
from pathlib import Path

class CodeAnalyzer:
    def __init__(self):
        self.security_patterns = self._load_security_patterns()
    
    def analyze_code(self, directory_path: str) -> List[Dict]:
        """Perform static code analysis"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    results.extend(self._analyze_python_file(filepath))
        
        return results
    
    def _analyze_python_file(self, filepath: str) -> List[Dict]:
        """Analyze Python file for security issues"""
        findings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                tree = ast.parse(content)
                
                # Check for dangerous functions
                findings.extend(self._check_dangerous_functions(tree, filepath))
                
                # Check for weak authentication
                findings.extend(self._check_authentication_issues(content, filepath))
                
                # Check for insecure configurations
                findings.extend(self._check_configurations(content, filepath))
                
        except Exception as e:
            pass
        
        return findings
    
    def _check_dangerous_functions(self, tree: ast.AST, filepath: str) -> List[Dict]:
        """Check for dangerous function calls"""
        findings = []
        dangerous_calls = ['eval', 'exec', 'compile', '__import__', 'pickle.loads']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = f"{node.func.attr}"
                
                if any(dangerous in func_name for dangerous in dangerous_calls):
                    findings.append({
                        "scan_type": "code_analysis",
                        "severity": "HIGH",
                        "title": f"Dangerous function: {func_name}",
                        "description": f"Use of dangerous function '{func_name}' detected. This can lead to code injection vulnerabilities.",
                        "file_path": filepath,
                        "line_number": node.lineno if hasattr(node, 'lineno') else 0,
                        "cvss_score": 7.5,
                        "metadata": {"function": func_name, "type": "dangerous_call"}
                    })
        
        return findings
    
    def _check_authentication_issues(self, content: str, filepath: str) -> List[Dict]:
        """Check for authentication and authorization issues"""
        findings = []
        
        # Check for weak password comparison
        if re.search(r'password\s*==\s*|password\s*!=\s*', content):
            findings.append({
                "scan_type": "code_analysis",
                "severity": "HIGH",
                "title": "Timing Attack Vulnerability",
                "description": "Password comparison using == operator is vulnerable to timing attacks. Use constant-time comparison.",
                "file_path": filepath,
                "line_number": 0,
                "cvss_score": 7.0,
                "metadata": {"issue": "timing_attack"}
            })
        
        # Check for missing authentication decorators
        if re.search(r'@app\.route|@router\.(get|post|put|delete)', content):
            if not re.search(r'@require_auth|@login_required|@jwt_required', content):
                findings.append({
                    "scan_type": "code_analysis",
                    "severity": "MEDIUM",
                    "title": "Missing Authentication Check",
                    "description": "Route detected without authentication decorator. Ensure proper authentication is enforced.",
                    "file_path": filepath,
                    "line_number": 0,
                    "cvss_score": 6.0,
                    "metadata": {"issue": "missing_auth"}
                })
        
        return findings
    
    def _check_configurations(self, content: str, filepath: str) -> List[Dict]:
        """Check for insecure configurations"""
        findings = []
        
        # Check for debug mode in production
        if re.search(r'debug\s*=\s*True|DEBUG\s*=\s*True', content):
            findings.append({
                "scan_type": "code_analysis",
                "severity": "HIGH",
                "title": "Debug Mode Enabled",
                "description": "Debug mode detected. This exposes sensitive information and should be disabled in production.",
                "file_path": filepath,
                "line_number": 0,
                "cvss_score": 7.0,
                "metadata": {"issue": "debug_enabled"}
            })
        
        # Check for disabled SSL verification
        if re.search(r'verify\s*=\s*False', content):
            findings.append({
                "scan_type": "code_analysis",
                "severity": "HIGH",
                "title": "SSL Verification Disabled",
                "description": "SSL certificate verification is disabled. This makes the application vulnerable to man-in-the-middle attacks.",
                "file_path": filepath,
                "line_number": 0,
                "cvss_score": 8.0,
                "metadata": {"issue": "ssl_disabled"}
            })
        
        return findings
    
    def _load_security_patterns(self) -> Dict:
        """Load security analysis patterns"""
        return {
            "sql_injection": r'execute\([^)]*%|cursor\.execute\([^)]*\+',
            "xss": r'innerHTML\s*=|document\.write\(',
            "csrf": r'@app\.route.*methods=\["POST"\](?!.*@csrf\.exempt)',
            "command_injection": r'os\.system|subprocess\.call.*shell=True'
        }
