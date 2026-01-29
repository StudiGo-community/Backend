#!/bin/bash

python manage.py shell << 'EOF'
from apps.daily.models.questions import Question

# 이번 달 문제 예시 데이터
QUESTIONS = [
    {
        "title": "Saludos",
        "description": "Completa la oración.",
        "prompt": "Buenos _____, ¿cómo estás?",
        "answer_text": "dias",
        "explanation": "Buenos días, ¿cómo estás?",
    },
    {
        "title": "Presentación",
        "description": "Completa la oración.",
        "prompt": "Mi nombre _____ Carlos.",
        "answer_text": "es",
        "explanation": "Mi nombre es Carlos.",
    },
    {
        "title": "Cortesía",
        "description": "Completa la oración.",
        "prompt": "_____ por tu ayuda.",
        "answer_text": "gracias",
        "explanation": "Gracias por tu ayuda.",
    },
    {
        "title": "Preguntas básicas",
        "description": "Completa la oración.",
        "prompt": "¿_____ años tienes?",
        "answer_text": "cuantos",
        "explanation": "¿Cuántos años tienes?",
    },
    {
        "title": "Ubicación",
        "description": "Completa la oración.",
        "prompt": "Vivo _____ Madrid.",
        "answer_text": "en",
        "explanation": "Vivo en Madrid.",
    },
    {
        "title": "Tiempo",
        "description": "Completa la oración.",
        "prompt": "Hoy _____ mucho frío.",
        "answer_text": "hace",
        "explanation": "Hoy hace mucho frío.",
    },
    {
        "title": "Preferencias",
        "description": "Completa la oración.",
        "prompt": "Me _____ el café.",
        "answer_text": "gusta",
        "explanation": "Me gusta el café.",
    },
    {
        "title": "Rutina diaria",
        "description": "Completa la oración.",
        "prompt": "Todos los días me _____ temprano.",
        "answer_text": "despierto",
        "explanation": "Todos los días me despierto temprano.",
    },
    {
        "title": "Compras",
        "description": "Completa la oración.",
        "prompt": "Quiero _____ pan y leche.",
        "answer_text": "comprar",
        "explanation": "Quiero comprar pan y leche.",
    },
    {
        "title": "Despedida",
        "description": "Completa la oración.",
        "prompt": "_____ luego, nos vemos mañana.",
        "answer_text": "hasta",
        "explanation": "Hasta luego, nos vemos mañana.",
    },
]

created = 0
skipped = 0

for q in QUESTIONS:
    obj, is_created = Question.objects.get_or_create(
        title=q["title"],
        defaults={
            "description": q["description"],
            "prompt": q["prompt"],
            "answer_text": q["answer_text"],
            "explanation": q["explanation"],
            "is_active": True,
        },
    )

    if is_created:
        created += 1
    else:
        skipped += 1

print(f"✅ 생성된 문제: {created}개")
print(f"⏭️  이미 존재하여 건너뜀: {skipped}개")
EOF