import asyncio
import httpx
import time

# Количество запросов для тестирования
NUM_REQUESTS = 200
# URL-адрес вашего API
URL = "http://localhost:8080/login"


async def send_request(client):
    start_time = time.monotonic()  # Начинаем измерение времени
    response = await client.post(URL, json={
        "email": "legen2a208@gmail.com",
        "password": "legen2a777"
    })
    response_time = time.monotonic() - start_time  # Измеряем время ответа
    return response_time if response.status_code == 200 else None  # Возвращаем только успешные ответы


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client) for _ in range(NUM_REQUESTS)]

        # Выполняем запросы и собираем результаты
        response_times = await asyncio.gather(*tasks)
        # Убираем None из результатов
        response_times = [time for time in response_times if time is not None]

        # Если есть успешные результаты, вычисляем среднее время ответа
        if response_times:
            average_response_time = sum(response_times) / len(response_times)
            print(f"Среднее время ответа: {average_response_time:.4f} секунд")
        else:
            print("Не удалось получить успешные ответы.")


# Запуск асинхронного теста
asyncio.run(main())
