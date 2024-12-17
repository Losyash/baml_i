from datetime import datetime
from sklearn.datasets import load_diabetes
import json
import numpy as np
import pika
import time

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
  try:
    # Создаём подключение по адресу "rabbitmq":
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Объявляем очередь "features" и "y_pred"
    channel.queue_declare(queue='features')
    channel.queue_declare(queue='y_true')

    # Формируем случайный индекс строки
    random_row = np.random.randint(0, X.shape[0]-1)

    # Формируем идентификаторы сообщений
    msg_id = datetime.timestamp(datetime.now())

    # Формируем сообщения
    msg_y_true = { 'id': msg_id, 'body': y[random_row] }
    msg_features = { 'id': msg_id, 'body': list(X[random_row]) }

    # Публикуем сообщение в очередь "y_true"
    channel.basic_publish(exchange='', routing_key='y_true', body=json.dumps(msg_y_true))
    print(f'Сообщение с идентификатором {msg_id} с правильным ответом отправлено в очередь "y_true"')

    # Публикуем сообщение в очередь "features"
    channel.basic_publish(exchange='', routing_key='features', body=json.dumps(msg_features))
    print(f'Сообщение с идентификатором {msg_id} с вектором признаков отправлено в очередь "features"')

    # Закрываем подключение и ожидаем 10 секунд перед отправкой следующего сообщения
    connection.close()
    time.sleep(10)
  except Exception as e:
    print('Не удалось подключиться к очереди', e)