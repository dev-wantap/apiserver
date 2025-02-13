from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # SQLite 데이터베이스 사용 (PostgreSQL 등으로 변경 가능)

# 데이터베이스 엔진 생성
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
    )

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 이 클래스를 상속)
Base = declarative_base()


# get_db
# 각 요청마다 새로운 세션, 요청 처리 종료 시 자동 종료
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
