import json
import matplotlib.pylab as plt
import pandas as pd
import pika

try:
  # Создаём подключение по адресу rabbitmq:
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  # Объявляем очередь "error"
  channel.queue_declare(queue='error')

  # Задаем путь к файлу с логами
  file_path = 'logs/metric_log.csv'

  # Создаём функцию callback для обработки данных из очереди
  def callback(ch, method, properties, body):
    msg = json.loads(body)

    msg_id = msg.get('id')
    msg_body = msg.get('body')

    print(f'Сообщение с идентификатором {msg_id} с правильным ответом {msg_body} получено из очереди "error"')

    df = pd.read_csv(file_path, sep=',')
    data = df['absolute_error']

    plt.hist(data, bins=10, edgecolor='black')
    plt.xlabel('Абсолютная ошибка')
    plt.ylabel('Количество')
    plt.savefig('logs/error_distribution.png', bbox_inches='tight')

  # Извлекаем сообщение из очереди features
  # on_message_callback показывает, какую функцию вызвать при получении сообщения
  channel.basic_consume(queue='error', on_message_callback=callback, auto_ack=True)

  # Запускаем режим ожидания прихода сообщений
  print('...Ожидание сообщений, для выхода нажмите CTRL+C')
  channel.start_consuming()
except Exception as e:
  print(e)
  print('Не удалось подключиться к очереди', e)