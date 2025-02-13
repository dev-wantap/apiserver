from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Cookie
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel
import ftplib
import os
import shutil
from pathlib import Path

from database import engine, get_db
import models

app = FastAPI()

# CORS 처리
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 앱 시작 시 DB에 테이블 생성
models.Base.metadata.create_all(bind=engine)

# GET, 메인 화면, "/"
class UserRequest(BaseModel):
    username: str

@app.post("/")
async def mainpage(user_request: UserRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_request.username).first()
    if not user:
        return JSONResponse(
            status_code=401,  # Unauthorized
            content={"detail": "로그인이 필요합니다"}
        )
    return {"username": user.username, "nickname": user.nickname}


#POST, 회원가입, "/signup"
class UserSignup(BaseModel):
    username: str
    password: str
    nickname: str

@app.post("/signup")
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    # 사용자명과 닉네임 중복 체크
    username_exists = db.query(models.User).filter(models.User.username == user.username).first()
    
    nickname_exists = db.query(models.User).filter(models.User.nickname == user.nickname).first()
    
    if username_exists:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다")
    
    if nickname_exists:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다")
    
    # 새 사용자 생성
    new_user = models.User(
        username=user.username,
        password=user.password,
        nickname=user.nickname
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입 성공", "nickname": new_user.nickname}

#POST, 로그인, "/login"
class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username,
        models.User.password == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="로그인 실패"
        )
    
    response = JSONResponse({
        "message": "로그인 성공",
        "success": 1,
        "username": db_user.username,
        "nickname": db_user.nickname
    })

    response.set_cookie(key="username", value=db_user.username)
    response.set_cookie(key="nickname", value=db_user.nickname)
    
    return response


# POST, 파일 업로드, "/file"
# FTP 서버 접속 정보
FTP_HOST = "localhost"  # 또는 "127.0.0.1" 사용 가능
FTP_PORT = 21
FTP_USER = "ftpuser"
FTP_PASS = "ftppassword"

def upload_to_ftp(local_file_path, remote_filename):
    try:
        # FTP 연결
        ftp = ftplib.FTP()
        ftp.connect(host=FTP_HOST, port=FTP_PORT)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        ftp.encoding = "utf-8"
        
        # 파일 업로드
        with open(local_file_path, "rb") as file:
            ftp.storbinary(f"STOR {remote_filename}", file)
            print(f"파일 업로드 성공: {remote_filename}")
        
        # 연결 종료
        ftp.quit()
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")

@app.post("/file/")
async def upload_file(
    username: str = Cookie(None),  # 쿠키에서 username 가져오기
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # file_name = file_name.strip()
    if not username:
        raise HTTPException(
            status_code=401,
            detail="로그인이 필요합니다"
        )
    # 로컬 저장 디렉토리 정보
    folder_path = os.path.join("temp")
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    file_path = os.path.join(folder_path, file.filename)

    # 파일 저장(현재는 로컬에 저장)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 현재 파일명 임시 변수에 저장
    file_name = file.filename

    # FTP로 파일 업로드
    upload_to_ftp(f"temp/{file_name}", file_name) # 로컬파일경로, 원격저장이름

    # 서버에 저장된 url 및 파일 원본 이름 db에 저장
    download_url = f"http://127.0.0.1/{file_name}"

    # username으로 user 조회
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # File 테이블에 저장
    new_file = models.File(
        user_id=user.id,
        name=file_name,
        file_url=download_url
    )
    
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {"message": "File uploaded successfully", "file_path": file_path, "file_name": file_name}

