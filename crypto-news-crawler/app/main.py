from .db import engine
from .models import Base

def init_db():
    # Nếu bảng chưa tạo, có thể dùng dòng này để SQLAlchemy tạo giúp
    Base.metadata.create_all(bind=engine)
    print("DB initialized")

if __name__ == "__main__":
    init_db()