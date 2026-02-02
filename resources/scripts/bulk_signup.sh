#!/bin/bash
set -euo pipefail

python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model

User = get_user_model()

PASSWORD = "string135!"
NAME = "테스트"
BIRTHDAY = "2006-02-04"
GENDER = "M"

def create_user(email, phone, *, is_staff=False, is_superuser=False):
    if User.objects.filter(email=email).exists():
        print(f"⏭️  이미 존재: {email}")
        return False

    if User.objects.filter(phone=phone).exists():
      print(f"⏭️  휴대폰 중복: {phone}")
      return False

    nickname = email.split("@")[0]

    user = User.objects.create_user(
        email=email,
        password=PASSWORD,
        name=NAME,
        nickname=nickname,
        birthday=BIRTHDAY,
        gender=GENDER,
        phone=phone,
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
if create_user("user@example.com", "01000000000"):
    created += 1

for i in range(1, 10):
    if create_user(
        f"user{i}@example.com",
        f"010100000{i:02d}",
    ):
        created += 1

# 2️⃣ 스태프
for i in range(1, 10):
    if create_user(
        f"staff{i}@example.com",
        f"010200000{i:02d}",
        is_staff=True,
    ):
        created += 1

# 3️⃣ 관리자
for i in range(1, 10):
    if create_user(
        f"admin{i}@example.com",
        f"010300000{i:02d}",
        is_staff=True,
        is_superuser=True,
    ):
        created += 1

print()
print(f"🎉 계정 생성 완료: 총 {created}개")
EOF