import os

class Settings:
    # MoMo Configuration
    MOMO_PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE", "MOMOBKUN20180529")
    MOMO_ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY", "klm05TvNBzhg7h7j")
    MOMO_SECRET_KEY = os.getenv("MOMO_SECRET_KEY", "at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa")
    MOMO_TEST_ENDPOINT = os.getenv("MOMO_TEST_ENDPOINT", "https://test-payment.momo.vn/v2/gateway/api/create")
    
    # URLs - these will be routed through Kong Gateway
    MOMO_RETURN_URL = os.getenv("MOMO_RETURN_URL", "http://localhost:8000/api/payment/momo/result")
    MOMO_NOTIFY_URL = os.getenv("MOMO_NOTIFY_URL", "http://localhost:8000/api/payment/momo/ipn")
    
    # Business Service URL for creating orders
    BUSINESS_SERVICE_URL = os.getenv("BUSINESS_SERVICE_URL", "http://business_service:8000")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_service.db")

settings = Settings()
