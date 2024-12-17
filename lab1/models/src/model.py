from datetime import datetime
import json
import numpy as np
import pickle
import pika

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
  regressor = pickle.load(pkl_file)

try:
  # Создаём подключение по адресу rabbitmq:
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  # Объявляем очередь "features" и "y_pred"
  channel.queue_declare(queue='features')
  channel.queue_declare(queue='y_pred')

  # Создаём функцию callback для обработки данных из очереди
  def callback(ch, method, properties, body):
    msg = json.loads(body)

    msg_id = msg.get('id')
    msg_body = msg.get('body')

    print(f'Сообщение с идентификатором {msg_id} c вектором признаков {msg_body} получено из очереди "features"')

    y_pred = regressor.predict(np.array(msg_body).reshape(1, -1))
    msg_y_pred = { 'id': msg_id, 'body': y_pred[0] }

    channel.basic_publish(exchange='', routing_key='y_pred', body=json.dumps(msg_y_pred))
    print(f'Сообщение с идентификатором {msg_id} с предсказанием {y_pred[0]} отправлено в очередь "y_pred"')

  # Извлекаем сообщение из очереди "features"
  # on_message_callback показывает, какую функцию вызвать при получении сообщения
  channel.basic_consume(queue='features', on_message_callback=callback, auto_ack=True)

  # Запускаем режим ожидания прихода сообщений
  print('...Ожидание сообщений, для выхода нажмите CTRL+C')
  channel.start_consuming()
except Exception as e:
  print('Не удалось подключиться к очереди', e)