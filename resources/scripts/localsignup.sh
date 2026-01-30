#!/bin/bash
set -euo pipefail

read -p "이메일을 입력하세요: " EMAIL
read -p "닉네임을 입력하세요(중복불가): " NICKNAME
read -s -p "비밀번호를 입력하세요: " PASSWORD
echo ""

NAME="테스트"
BIRTHDAY="2006-02-04"
GENDER="M"
PHONE_NUMBER="01012345678"

python manage.py shell -c "
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

email='''$EMAIL'''.strip().lower()
pw='''$PASSWORD'''
name='''$NAME'''
nickname='''$NICKNAME'''
birthday='''$BIRTHDAY'''
gender='''$GENDER'''
phone='''$PHONE_NUMBER'''

if User.objects.filter(email=email).exists():
    print('이미 존재하는 이메일입니다:', email)
else:
    user = User.objects.create_user(
        email=email,
        password=pw,
        name=name,
        nickname=nickname,
        birthday=birthday,
        gender=gender,
        phone=phone,
        is_active=True,
    )

    refresh = RefreshToken.for_user(user)

    print('생성 완료:', user.id, user.email)
    print()
    print('---ACCESS TOKEN---')
    print(refresh.access_token)
    print()
    print('---REFRESH TOKEN---')
    print(refresh)
"