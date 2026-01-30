#!/bin/bash
set -euo pipefail

python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model

User = get_user_model()

PASSWORD = "string"
NAME = "테스트"
BIRTHDAY = "2006-02-04"
GENDER = "M"
PHONE = "01012345678"

def create_user(email, *, is_staff=False, is_superuser=False):
    if User.objects.filter(email=email).exists():
        print(f"⏭️  이미 존재: {email}")
        return False

    nickname = email.split("@")[0]

    user = User.objects.create_user(
        email=email,
        password=PASSWORD,
        name=NAME,
        nickname=nickname,
        birthday=BIRTHDAY,
        gender=GENDER,
        phone=PHONE,
        is_active=True,
    )

    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save(update_fields=["is_staff", "is_superuser"])

    role = (
        "ADMIN" if is_superuser else
        "STAFF" if is_staff else
        "USER"
    )

    print(f"✅ 생성 완료 [{role}] {email}")
    return True


created = 0

# 1️⃣ 일반 유저
emails = ["user@example.com"] + [f"user{i}@example.com" for i in range(1, 10)]
for email in emails:
    if create_user(email):
        created += 1

# 2️⃣ 스태프
for i in range(1, 10):
    if create_user(f"staff{i}@example.com", is_staff=True):
        created += 1

# 3️⃣ 관리자
for i in range(1, 10):
    if create_user(
        f"admin{i}@example.com",
        is_staff=True,
        is_superuser=True,
    ):
        created += 1

print()
print(f"🎉 계정 생성 완료: 총 {created}개")
EOF