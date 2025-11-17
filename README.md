서버가 이미 가동 중인 상태(예: `docker compose up -d` 실행 완료)에서,  

Windows PowerShell을 열고 다음 명령으로 Django 관리자 계정을 생성합니다.



powershell

docker compose exec web python manage.py createsuperuser

