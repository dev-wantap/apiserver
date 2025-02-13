from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import Base

# 사용자 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer ,primary_key=True, index=True)  # PK
    username = Column(String, nullable=False) # 아이디
    password = Column(String, nullable=False)  # 비밀번호
    nickname = Column(String, nullable=False)  # 닉네임
    files = relationship("File", back_populates="user")  # 사용자와 폴더의 관계


# 파일 모델
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)  # 파일의 PK
    user_id = Column(Integer, ForeignKey("users.id"))  # 사용자 ID (FK)
    name = Column(String, nullable=False)  # 파일명
    file_url = Column(String, nullable=False)  # 파일 경로(URL)
    user = relationship("User", back_populates="files")  # 파일과 사용자 관계

