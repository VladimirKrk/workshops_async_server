from rest_framework.views import APIView
from rest_framework.response import Response
import time # Используем time.sleep вместо asyncio.sleep
import random
import requests
import os
import threading # <-- Импортируем threading

def calculate_historical_output(found_defects: int) -> str:
    defective_rate = 0.3
    found_rate = 0.06
    if defective_rate == 0 or found_rate == 0:
        return "0 шт."
    calculated_output = int(found_defects / (defective_rate * found_rate))
    return f"{calculated_output} шт."

# Наша долгая задача теперь - это обычная синхронная функция
def perform_analysis_in_background(data: dict):
    # 1. Имитируем задержку с помощью time.sleep
    time.sleep(random.uniform(5, 10))
    
    # 2. Выполняем расчет
    predicted_output = calculate_historical_output(data.get("found_defects", 0))

    # 3. Готовим и отправляем результат обратно в Go-сервис
    callback_url = os.environ.get("CALLBACK_URL")
    api_key = os.environ.get("INTERNAL_API_KEY")
    
    payload = {
        "application_id": data.get("application_id"),
        "workshop_id": data.get("workshop_id"),
        "predicted_output": predicted_output,
        "api_key": api_key,  # Передаем API-ключ
    }
    
    headers = {
        "Content-Type": "application/json",
    }

    print(f"Sending result for AppID {payload['application_id']}, WorkshopID {payload['workshop_id']}: {predicted_output}")

    try:
        requests.post(callback_url, json=payload, headers=headers)
        print("Result sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to send callback to Go service: {e}")

class AnalyzeProductionView(APIView):
    def post(self, request, *args, **kwargs):
        # Создаем и запускаем новый поток, передавая ему нашу функцию и данные
        thread = threading.Thread(target=perform_analysis_in_background, args=(request.data,))
        thread.start()
        
        # Сразу же отвечаем Go-сервису, что задача принята
        return Response({"status": "analysis_started"}, status=202)
