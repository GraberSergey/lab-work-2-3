import sqlite3
import xml.etree.ElementTree as ET
from pymorphy3 import MorphAnalyzer
import string


def create_database(connection: sqlite3.Connection) -> None:
	"""
	Создание таблиц базы данных

	:param connection: Объект соединения с БД

	:return: None
	"""

	cursor = connection.cursor()

	(
		cursor.execute("""
	        CREATE TABLE IF NOT EXISTS `requests`(
	        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	        `phrase` TEXT NOT NULL,
	        `answer` TEXT NOT NULL
	        );
        """)
		.execute("""
			CREATE TABLE IF NOT EXISTS `service-words`(
			`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			`word` TEXT NOT NULL
			);
		""")
	)


def clear_database(connection: sqlite3.Connection) -> None:
	"""
	Удаление информации из базы данных

	:param connection: Объект подключения к БД

	:return: None
	"""

	cursor = connection.cursor()

	(
		cursor.execute("""
			DROP TABLE IF EXISTS `requests`;
		""")
		.execute("""
			DROP TABLE IF EXISTS `service-words`;
		""")
	)


def insert_data(connection: sqlite3.Connection) -> None:
	"""
	Помещение информации в базу данных

	:param connection: Объект подключения к БД

	:return: None
	"""

	cursor = connection.cursor()

	(
		cursor.execute("""
			INSERT INTO `service-words`
			(`word`)
			VALUES('в');
		""")
		.execute("""
			INSERT INTO `service-words`
			(`word`)
			VALUES('на');
		""")
		.execute("""
			INSERT INTO `service-words`
			(`word`)
			VALUES('и');
		""")
		.execute("""
			INSERT INTO `requests`
			(`phrase`, `answer`)
			VALUES
			('кофе', 'Заварной кофе можно приготовить при помощи заливания кипятком растворимого кофейного порошка'),
			('паста карбонара', 'Паста карбонара - это классическое итальянское блюдо'),
			('суши', 'Суши - японское блюдо'),
			('хлеб', 'Домашний хлеб можно приготовить');
		""")
	)

	connection.commit()


def get_data_from_xml(path: str) -> list[dict]:
	"""
	Получение информации из файла .xml

	:param path: Путь к файлу .xml

	:return: Список объектов в файле .xml
	"""

	result = []

	tree = ET.parse(path)
	root = tree.getroot()

	for item in root.findall('Item'):
		result.append({
			'name': item.get('name'),
			'lemma': item.get('lemma')
		})

	return result


def normalize_request(request: str) -> str:
	"""
	Функция нормализации запроса

	:param request: Запрос

	:return: Нормализованный запрос
	"""

	request = (
		request.strip()
		.translate(str.maketrans('', '', string.punctuation))
		.split()
	)
	request = ' '.join(MorphAnalyzer().parse(word.lower())[0].normal_form for word in request)

	return request


def get_lemma(request: str, pairs: list[dict]) -> str:
	"""
	Функция получения леммы запроса

	:param request: Запрос
	:param pairs: Пары запрос-лемма

	:return: Лемма, соответствующая запросу
	"""

	for item in pairs:
		if item['name'] in request:
			return item['lemma']
	return ''


def get_answer(connection: sqlite3.Connection, request: str) -> str:
	"""
	Функция получения ответа на запрос

	:param connection: Объект подключения к базе данных
	:param request: Запрос

	:return: Ответ на запрос
	"""

	cursor = connection.cursor()
	cursor.execute("""
		SELECT `answer` FROM `requests`
		WHERE `phrase` = ?
	""", (request,))

	result = cursor.fetchone()
	if result is None:
		return 'Ответ не получен'
	else:
		return result[0]


def main():
	# Создание подключения к базе данных db\database.db
	connection = sqlite3.connect('db\\database.db')

	# Выполнение цикла очистки, создания, заполнения базы данных
	clear_database(connection)
	create_database(connection)
	insert_data(connection)

	# Получение информации из файла xml\senses.xml
	xml_data: list[dict] = get_data_from_xml('xml\\senses.xml')

	# Список запросов пользователя
	requests = [
		'рецепт пасты карбонара',
		'сделать домашний хлеб'
	]

	# Получение ответов на запросы
	for request in requests:
		lemma = get_lemma(request, xml_data)
		print('\n'.join([
			f'Запрос: {request}',
			f'Ответ: {get_answer(connection, lemma)}'
		]), end = '\n\n')

	# Завершение соединения к базе данных
	connection.close()


if __name__ == "__main__":
	main()
