"""
Script hướng dẫn setup ban đầu.

Các bước:
1. python -m app.main                          # Tạo tables
2. python insert_sample_sources.py             # Insert Coindesk + CryptoNews
3. python -m app.crawler_runner                # Test 1 lần
4. python -m app.core.scheduler                # Chạy 1 phút/lần
5. uvicorn app.api.main_api:app --reload      # API server
"""

print(__doc__)
