import json
import pika

try:
  # Создаём подключение по адресу "rabbitmq":
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  # Объявляем очередь "features" и "y_pred" и "error"
  channel.queue_declare(queue='y_true')
  channel.queue_declare(queue='y_pred')
  channel.queue_declare(queue='error')

  # Создаем словарь для хранения данных об истинном и предсказанном значениях
  data = {}

  # Задаем путь к файлу с логами
  file_path = 'logs/metric_log.csv'

  # Создаём функцию callback для обработки данных из очереди
  def callback(ch, method, properties, body):
    msg = json.loads(body)

    msg_id = msg.get('id')
    msg_body = msg.get('body')

    if not msg_id in data:
      data[msg_id] = {}

    if method.routing_key == 'y_true':
      print(f'Сообщение с идентификатором {msg_id} с правильным ответом {msg_body} получено из очереди "y_true"')
      data[msg_id].update({ 'y_true': msg_body })

    if method.routing_key == 'y_pred':
      print(f'Сообщение с идентификатором {msg_id} с предсказанием {msg_body} получено из очереди "y_pred"')
      data[msg_id].update({ 'y_pred': msg_body })

    if 'y_true' in data[msg_id] and 'y_pred' in data[msg_id]:
      error = abs(data[msg_id].get('y_true') - data[msg_id].get('y_pred'))
      line = f'{msg_id},{data[msg_id].get("y_true")},{data[msg_id].get("y_pred")},{error}'

      with open(file_path, 'a') as file:
        file.write(line + '\n')

      # Отправляем сообщение с вычисленной ошибкой в очередь "error"
      # По сути, значение имеет не сама ошибка а факт появления новых данных для
      # построения новой диаграммы сервисом plots
      msg_error = { 'id': msg_id, 'body': error }
      channel.basic_publish(exchange='', routing_key='error', body=json.dumps(msg_error))
      print(f'Сообщение с идентификатором {msg_id} с абсолютной ошибкой {error} отправлено в очередь "error"')

      del data[msg_id]

  # Извлекаем сообщение из очереди "y_true"
  channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)

  # Извлекаем сообщение из очереди "y_pred"
  channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

  # Запускаем режим ожидания прихода сообщений
  print('...Ожидание сообщений, для выхода нажмите CTRL+C')
  channel.start_consuming()
except Exception as e:
  print('Не удалось подключиться к очереди', e)