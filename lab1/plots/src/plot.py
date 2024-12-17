import matplotlib.pylab as plt
import pandas as pd
import pika

try:
  # Создаём подключение по адресу rabbitmq:
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  # Объявляем очередь "error"
  channel.queue_declare(queue='error')

  file_path = 'logs/metric_log.csv'

  # Создаём функцию callback для обработки данных из очереди
  def callback(ch, method, properties, body):
    print()
    df = pd.read_csv(file_path, sep=',')
    data = df['absolute_error']

    plt.hist(data, bins=10, edgecolor='black')
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