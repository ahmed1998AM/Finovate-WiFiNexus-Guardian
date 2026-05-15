"""
واجهة ويب تجريبية لـ WiFiNexus Guardian
تستخدم Flask لتقديم لوحة تحكم بسيطة
"""
import os
import sys
import json
from flask import Flask, render_template_string, jsonify, request
from typing import Dict, List, Optional

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# بيانات مؤقتة للتجربة
network_data = []
system_status = {
    'running': True,
    'mode': 'monitor',
    'interface': 'wlan0',
    'captured_handshakes': 0,
    'active_attacks': 0
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WiFiNexus Guardian - لوحة التحكم</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; text-align: center; }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .status-card h3 { color: #764ba2; margin-bottom: 10px; }
        .status-card .value { font-size: 2em; font-weight: bold; color: #667eea; }
        .networks-table {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: #667eea; color: white; }
        tr:hover { background: #f5f5f5; }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover { background: #5568d3; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .controls { margin-top: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ WiFiNexus Guardian v2.1.0</h1>
            <p style="text-align: center; color: #666;">لوحة التحكم الويب</p>
        </header>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>الحالة</h3>
                <div class="value" id="status">{{ 'نشط' if status.running else 'متوقف' }}</div>
            </div>
            <div class="status-card">
                <h3>الواجهة</h3>
                <div class="value" id="interface">{{ status.interface }}</div>
            </div>
            <div class="status-card">
                <h3>Handshakes</h3>
                <div class="value" id="handshakes">{{ status.captured_handshakes }}</div>
            </div>
            <div class="status-card">
                <h3>الهجمات النشطة</h3>
                <div class="value" id="attacks">{{ status.active_attacks }}</div>
            </div>
        </div>
        
        <div class="networks-table">
            <h2>الشبكات المكتشفة</h2>
            <table>
                <thead>
                    <tr>
                        <th>SSID</th>
                        <th>BSSID</th>
                        <th>القناة</th>
                        <th>الإشارة</th>
                        <th>الأمان</th>
                    </tr>
                </thead>
                <tbody id="networks-body">
                    {% for network in networks %}
                    <tr>
                        <td>{{ network.ssid or '<مخفي>' }}</td>
                        <td>{{ network.bssid }}</td>
                        <td>{{ network.channel }}</td>
                        <td>{{ network.signal }} dBm</td>
                        <td>{{ network.security }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if not networks %}
            <p style="text-align: center; color: #999; padding: 20px;">لا توجد شبكات مكتشفة</p>
            {% endif %}
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">🔄 تحديث</button>
            <button class="btn" onclick="startScan()">📡 بدء المسح</button>
            <button class="btn btn-danger" onclick="stopAll()">⏹️ إيقاف الكل</button>
        </div>
    </div>
    
    <script>
        function refreshData() {
            location.reload();
        }
        
        async function startScan() {
            const response = await fetch('/api/scan', { method: 'POST' });
            const result = await response.json();
            alert(result.message);
            refreshData();
        }
        
        async function stopAll() {
            if (confirm('هل أنت متأكد من إيقاف جميع العمليات؟')) {
                const response = await fetch('/api/stop', { method: 'POST' });
                const result = await response.json();
                alert(result.message);
                refreshData();
            }
        }
        
        // تحديث تلقائي كل 30 ثانية
        setTimeout(refreshData, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """الصفحة الرئيسية للوحة التحكم"""
    return render_template_string(
        HTML_TEMPLATE,
        networks=network_data,
        status=system_status
    )

@app.route('/api/status')
def get_status():
    """الحصول على حالة النظام"""
    return jsonify(system_status)

@app.route('/api/networks')
def get_networks():
    """الحصول على قائمة الشبكات"""
    return jsonify(network_data)

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """بدء مسح الشبكات"""
    # محاكاة بدء المسح
    global network_data
    network_data = [
        {'ssid': 'HomeWiFi', 'bssid': 'AA:BB:CC:DD:EE:FF', 'channel': 6, 'signal': -45, 'security': 'WPA2'},
        {'ssid': 'OfficeNet', 'bssid': '11:22:33:44:55:66', 'channel': 11, 'signal': -60, 'security': 'WPA3'},
    ]
    return jsonify({'message': 'تم بدء المسح بنجاح', 'success': True})

@app.route('/api/stop', methods=['POST'])
def stop_all():
    """إيقاف جميع العمليات"""
    global system_status, network_data
    system_status['running'] = False
    system_status['active_attacks'] = 0
    network_data = []
    return jsonify({'message': 'تم إيقاف جميع العمليات', 'success': True})

@app.route('/api/add_network', methods=['POST'])
def add_network():
    """إضافة شبكة يدوياً (للاختبار)"""
    data = request.json
    if data:
        network_data.append(data)
        return jsonify({'message': 'تمت الإضافة', 'success': True})
    return jsonify({'message': 'بيانات غير صالحة', 'success': False})

def run_server(host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
    """تشغيل خادم الويب"""
    print(f"🌐 تشغيل واجهة الويب على http://{host}:{port}")
    print("اضغط Ctrl+C للإيقاف")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='واجهة ويب WiFiNexus Guardian')
    parser.add_argument('--host', default='127.0.0.1', help='عنوان الخادم')
    parser.add_argument('--port', type=int, default=8080, help='رقم المنفذ')
    parser.add_argument('--debug', action='store_true', help='وضع التصحيح')
    
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)
