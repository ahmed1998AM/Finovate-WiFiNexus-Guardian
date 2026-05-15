WiFiNexus Guardian Documentation
================================

.. image:: ../logo.png
   :alt: WiFiNexus Guardian Logo
   :align: center

**أداة احترافية لاختبار اختراق الشبكات اللاسلكية والمراجعة الأمنية**

الإصدار: v2.1.0

.. contents:: محتويات الدليل
   :depth: 3
   :local:
   :backlinks: none

نظرة عامة
----------

WiFiNexus Guardian هي أداة شاملة لاختبار الأمان اللاسلكي، توفر:

- مسح شامل للشبكات اللاسلكية
- هجمات PMKID و Handshake Capture
- نظام دفاع ومراقبة WIDS
- تكامل مع WiGLE.net و Hashcat
- واجهات متعددة (CLI, GUI, TUI, Web)
- تقارير احترافية (PDF, HTML, DOCX)

وحدات البرمجية
--------------

الوحدات الأساسية
~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   modules/core
   modules/network
   modules/attacks
   modules/defense
   modules/ai
   modules/reports
   modules/integrations

دليل الوحدات التفصيلي
---------------------

Core Modules
~~~~~~~~~~~~

.. automodule:: core.security_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: core.process_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: core.profile_manager
   :members:
   :undoc-members:
   :show-inheritance:

Network Modules
~~~~~~~~~~~~~~~

.. automodule:: network.wifi_scanner
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: network.handshake_capturer
   :members:
   :undoc-members:
   :show-inheritance:

Attack Modules
~~~~~~~~~~~~~~

.. automodule:: attacks.pmkid_attacker
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: attacks.evil_twin_engine
   :members:
   :undoc-members:
   :show-inheritance:

Defense Modules
~~~~~~~~~~~~~~~

.. automodule:: defense.wids_monitor
   :members:
   :undoc-members:
   :show-inheritance:

Integration Modules
~~~~~~~~~~~~~~~~~~~

.. automodule:: integrations.wigle_api
   :members:
   :undoc-members:
   :show-inheritance:

Report Modules
~~~~~~~~~~~~~~

.. automodule:: reports.report_generator_pro
   :members:
   :undoc-members:
   :show-inheritance:

أدلة الاستخدام
--------------

.. toctree::
   :maxdepth: 2

   guides/getting_started
   guides/advanced_usage
   guides/docker_guide
   guides/api_reference

أمثلة سريعة
-----------

مسح الشبكات
~~~~~~~~~~~

.. code-block:: python

   from network.wifi_scanner import WiFiScanner
   
   scanner = WiFiScanner()
   networks = scanner.scan_networks()
   
   for network in networks:
       print(f"SSID: {network['ssid']}, Signal: {network['signal']}")

هجوم PMKID
~~~~~~~~~~

.. code-block:: python

   from attacks.pmkid_attacker import PMKIDAttacker
   
   attacker = PMKIDAttacker(interface='wlan0')
   await attacker.attack(target_bssid='AA:BB:CC:DD:EE:FF')

التكامل مع WiGLE
~~~~~~~~~~~~~~~~

.. code-block:: python

   from integrations.wigle_api import WiGLEIntegration
   
   wigle = WiGLEIntegration(api_key='YOUR_API_KEY')
   results = wigle.search_networks(ssid='TargetNetwork')

الفهرس والجداول
---------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

روابط مفيدة
-----------

- `المستودع الرسمي على GitHub <https://github.com/wifinexus/guardian>`_
- `دليل Docker <guides/docker_guide.html>`_
- `تقارير الاختبار <https://github.com/wifinexus/guardian/actions>`_

.. note::

   هذه الوثائق قيد التطوير المستمر. للمزيد من المعلومات، يرجى زيارة 
   `الوثائق الكاملة <https://wifinexus.github.io/docs>`_.

حقوق النشر
----------

© 2024 WiFiNexus Security Team. جميع الحقوق محفوظة.
