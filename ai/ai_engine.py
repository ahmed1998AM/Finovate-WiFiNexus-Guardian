"""
AI Engine - Network intelligence and recommendations using AI
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class AIEngine:
    """AI-powered network analysis and recommendations engine"""
    
    def __init__(self):
        self.model_provider = None
        self.is_initialized = False
        self.recommendations_cache = []
        
    def initialize(self, provider: str = "local") -> bool:
        """Initialize AI engine with specified provider"""
        self.model_provider = provider
        
        # Supported providers: ollama, openai, gemini, claude, deepseek, local
        if provider in ["ollama", "openai", "gemini", "claude", "deepseek", "local"]:
            self.is_initialized = True
            return True
        return False
    
    def analyze_network_health(self, network_data: Dict) -> Dict:
        """Analyze network health and provide insights"""
        health_score = 100
        issues = []
        recommendations = []
        
        # Analyze signal strength
        signal_strength = network_data.get("signal_strength", -50)
        if signal_strength < -80:
            health_score -= 30
            issues.append("Very weak signal detected")
            recommendations.append("Move closer to the access point or consider a WiFi extender")
        elif signal_strength < -70:
            health_score -= 15
            issues.append("Weak signal detected")
            recommendations.append("Consider repositioning your device for better reception")
        elif signal_strength < -60:
            health_score -= 5
            issues.append("Moderate signal strength")
            
        # Analyze channel congestion
        channel_congestion = network_data.get("channel_congestion", "low")
        if channel_congestion == "high":
            health_score -= 20
            issues.append("High channel congestion detected")
            recommendations.append("Switch to a less congested channel (1, 6, or 11 for 2.4GHz)")
        elif channel_congestion == "medium":
            health_score -= 10
            issues.append("Moderate channel congestion")
            recommendations.append("Consider switching to 5GHz band for less interference")
            
        # Analyze interference
        interference_level = network_data.get("interference_level", "low")
        if interference_level == "high":
            health_score -= 25
            issues.append("High interference detected")
            recommendations.append("Identify and remove sources of interference (microwaves, cordless phones, etc.)")
        elif interference_level == "medium":
            health_score -= 10
            issues.append("Moderate interference present")
            
        # Analyze connected devices
        device_count = network_data.get("connected_devices", 0)
        if device_count > 20:
            health_score -= 15
            issues.append(f"High number of connected devices ({device_count})")
            recommendations.append("Consider upgrading to a more powerful router or adding access points")
            
        # Ensure score doesn't go below 0
        health_score = max(0, health_score)
        
        # Determine health status
        if health_score >= 90:
            status = "Excellent"
        elif health_score >= 75:
            status = "Good"
        elif health_score >= 50:
            status = "Fair"
        else:
            status = "Poor"
            
        result = {
            "health_score": health_score,
            "status": status,
            "issues": issues,
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat(),
            "provider": self.model_provider
        }
        
        self.recommendations_cache.append(result)
        return result
    
    def predict_interference(self, historical_data: List[Dict]) -> Dict:
        """Predict potential interference based on historical data"""
        prediction = {
            "risk_level": "low",
            "potential_sources": [],
            "mitigation_suggestions": [],
            "confidence": 0.0
        }
        
        if not historical_data:
            prediction["confidence"] = 0.0
            return prediction
            
        # Simple pattern detection
        interference_patterns = []
        for data_point in historical_data[-10:]:  # Last 10 data points
            if data_point.get("signal_drop", 0) > 20:
                interference_patterns.append("signal_drop")
            if data_point.get("packet_loss", 0) > 5:
                interference_patterns.append("packet_loss")
                
        if len(interference_patterns) > 5:
            prediction["risk_level"] = "high"
            prediction["potential_sources"] = [
                "Other wireless networks",
                "Electronic devices",
                "Physical obstructions"
            ]
            prediction["mitigation_suggestions"] = [
                "Change WiFi channel",
                "Reposition router",
                "Use 5GHz band",
                "Add shielding or barriers"
            ]
            prediction["confidence"] = 0.75
        elif len(interference_patterns) > 2:
            prediction["risk_level"] = "medium"
            prediction["potential_sources"] = ["Nearby wireless devices"]
            prediction["mitigation_suggestions"] = ["Monitor channel usage", "Optimize router placement"]
            prediction["confidence"] = 0.60
        else:
            prediction["risk_level"] = "low"
            prediction["confidence"] = 0.85
            
        return prediction
    
    def generate_optimization_report(self, network_data: Dict) -> str:
        """Generate an AI-powered optimization report"""
        analysis = self.analyze_network_health(network_data)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║         WiFiNexus Guardian - AI Network Analysis Report      ║
╚══════════════════════════════════════════════════════════════╝

Report Generated: {analysis['analyzed_at']}
AI Provider: {analysis['provider']}

┌──────────────────────────────────────────────────────────────┐
│ NETWORK HEALTH SUMMARY                                       │
├──────────────────────────────────────────────────────────────┤
│ Health Score: {analysis['health_score']}/100
│ Status: {analysis['status']}
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ DETECTED ISSUES                                              │
├──────────────────────────────────────────────────────────────┤
"""
        
        for i, issue in enumerate(analysis['issues'], 1):
            report += f"│ {i}. {issue}\n"
            
        if not analysis['issues']:
            report += "│ No significant issues detected\n"
            
        report += """
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ AI RECOMMENDATIONS                                           │
├──────────────────────────────────────────────────────────────┤
"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"│ {i}. {rec}\n"
            
        report += """
└──────────────────────────────────────────────────────────────┘

Thank you for using WiFiNexus Guardian!
© 2025 Ahmed Mostafa Ibrahim - Finovate
"""
        
        return report
    
    def get_ai_recommendation(self, context: str) -> str:
        """Get AI recommendation based on context"""
        # In production, this would call actual AI models
        recommendations = {
            "slow_speed": "Consider upgrading your internet plan or optimizing router settings",
            "connection_drops": "Check for interference sources and update router firmware",
            "security_concern": "Enable WPA3 encryption and change default passwords",
            "range_issues": "Consider mesh networking or WiFi extenders for better coverage"
        }
        
        for key, rec in recommendations.items():
            if key in context.lower():
                return rec
                
        return "For optimal performance, ensure your router firmware is up to date and positioned centrally."
    
    def shutdown(self):
        """Cleanup AI engine resources"""
        self.is_initialized = False
        self.model_provider = None
