서버 가동 중인 상태에서 원도우 Powershell 에서 관리자 계정 등록 필요합니다.
docker compose exec web python manage.py createsuperuser << 명령어
비밀번호는 8자리 숫자+영문으로 powershell 에서 비밀번호를 입력해도 안보이는 경우가 있는데, 보이지만 않을 뿐 입력되고 있습니다.
로또 회차 설정은 http://localhost:8000/admin/ 를 들어간뒤 Draws를 +add 하시면 됩니다.
