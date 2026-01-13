import subprocess
import json
from typing import List, Dict
import os

class DependencyAuditor:
    def __init__(self):
        self.vulnerability_db = self._load_vulnerability_db()
    
    def audit_dependencies(self, project_path: str) -> List[Dict]:
        """Audit project dependencies for known vulnerabilities"""
        results = []
        
        # Check Python dependencies
        requirements_file = os.path.join(project_path, "requirements.txt")
        if os.path.exists(requirements_file):
            results.extend(self._audit_python_deps(requirements_file))
        
        # Check npm dependencies
        package_json = os.path.join(project_path, "package.json")
        if os.path.exists(package_json):
            results.extend(self._audit_npm_deps(package_json))
        
        return results
    
    def _audit_python_deps(self, requirements_file: str) -> List[Dict]:
        """Audit Python dependencies using Safety"""
        findings = []
        
        try:
            cmd = ["safety", "check", "--json", "--file", requirements_file]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if process.stdout:
                try:
                    safety_results = json.loads(process.stdout)
                    for vuln in safety_results:
                        findings.append({
                            "scan_type": "dependency",
                            "severity": self._get_severity_from_cvss(vuln.get("cvssv3", {}).get("base_score", 0)),
                            "title": f"Vulnerable dependency: {vuln.get('package', 'Unknown')}",
                            "description": vuln.get('advisory', 'Known security vulnerability'),
                            "file_path": requirements_file,
                            "cve_id": vuln.get('cve', None),
                            "cvss_score": vuln.get("cvssv3", {}).get("base_score", 0),
                            "metadata": {
                                "package": vuln.get("package"),
                                "installed_version": vuln.get("installed_version"),
                                "vulnerable_spec": vuln.get("vulnerable_spec"),
                                "more_info_url": vuln.get("more_info_url")
                            }
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Python dependency audit error: {str(e)}")
        
        # Add manual checks for known vulnerable packages
        findings.extend(self._manual_dependency_checks(requirements_file))
        
        return findings
    
    def _audit_npm_deps(self, package_json: str) -> List[Dict]:
        """Audit npm dependencies"""
        findings = []
        
        try:
            # Run npm audit if package.json exists
            project_dir = os.path.dirname(package_json)
            cmd = ["npm", "audit", "--json"]
            process = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=60)
            
            if process.stdout:
                try:
                    audit_results = json.loads(process.stdout)
                    vulnerabilities = audit_results.get("vulnerabilities", {})
                    
                    for pkg_name, vuln_data in vulnerabilities.items():
                        findings.append({
                            "scan_type": "dependency",
                            "severity": vuln_data.get("severity", "MEDIUM").upper(),
                            "title": f"Vulnerable npm package: {pkg_name}",
                            "description": vuln_data.get("via", [{}])[0].get("title", "Known security vulnerability"),
                            "file_path": package_json,
                            "cve_id": vuln_data.get("via", [{}])[0].get("cve", None),
                            "cvss_score": vuln_data.get("via", [{}])[0].get("cvss", {}).get("score", 0),
                            "metadata": {
                                "package": pkg_name,
                                "range": vuln_data.get("range", ""),
                                "fix_available": vuln_data.get("fixAvailable", False)
                            }
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"NPM dependency audit error: {str(e)}")
        
        return findings
    
    def _manual_dependency_checks(self, requirements_file: str) -> List[Dict]:
        """Manual checks for known vulnerable packages"""
        findings = []
        vulnerable_packages = {
            "django<3.2": {"cve": "CVE-2021-33203", "severity": "HIGH", "description": "Potential directory traversal"},
            "flask<2.0": {"cve": "CVE-2021-31618", "severity": "MEDIUM", "description": "Open redirect vulnerability"},
            "pillow<9.0": {"cve": "CVE-2022-22817", "severity": "CRITICAL", "description": "Buffer overflow"},
            "requests<2.28": {"cve": "CVE-2022-23491", "severity": "MEDIUM", "description": "Proxy-Authorization header leak"}
        }
        
        try:
            with open(requirements_file, 'r') as f:
                content = f.read()
                for pkg_spec, vuln_info in vulnerable_packages.items():
                    pkg_name = pkg_spec.split('<')[0]
                    if pkg_name in content:
                        findings.append({
                            "scan_type": "dependency",
                            "severity": vuln_info["severity"],
                            "title": f"Potentially vulnerable: {pkg_name}",
                            "description": vuln_info["description"],
                            "file_path": requirements_file,
                            "cve_id": vuln_info["cve"],
                            "cvss_score": self._severity_to_cvss(vuln_info["severity"]),
                            "metadata": {"package": pkg_name, "recommendation": f"Update to {pkg_spec}"}
                        })
        except Exception as e:
            pass
        
        return findings
    
    def _get_severity_from_cvss(self, cvss_score: float) -> str:
        """Convert CVSS score to severity level"""
        if cvss_score >= 9.0:
            return "CRITICAL"
        elif cvss_score >= 7.0:
            return "HIGH"
        elif cvss_score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _severity_to_cvss(self, severity: str) -> float:
        """Convert severity to CVSS score"""
        mapping = {
            "CRITICAL": 9.5,
            "HIGH": 7.5,
            "MEDIUM": 5.0,
            "LOW": 2.5
        }
        return mapping.get(severity, 0.0)
    
    def _load_vulnerability_db(self) -> Dict:
        """Load vulnerability database (simplified version)"""
        return {
            "known_vulns": [],
            "last_updated": "2025-05-01"
        }
