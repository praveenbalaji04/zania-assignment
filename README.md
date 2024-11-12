Zania Interview Assignment
------

Files:
 - core/views.py - DRF API
 - core/open_ai_wrapper.py - Function to fetch response from OpenAI
 - helpers.py - File type handlers

APIs:
 - `<HOST>/v1/health` - Health check API
 - `<HOST>/v1/open-ai/` - Request payload and response structure mentioned in views.py

ENV:
 - OPEN_AI_API_KEY

To Run:
 1. pip install -r requirements.txt
 2. python manage.py runserver