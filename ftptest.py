import ftplib

# FTP 서버 접속 정보
FTP_HOST = "localhost"  # 또는 "127.0.0.1" 사용 가능
FTP_PORT = 21
FTP_USER = "ftpuser"
FTP_PASS = "ftppassword"

def upload_file(local_file_path, remote_filename):
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

# 사용 예시
upload_file("test", "file2")
