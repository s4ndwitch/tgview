from sqlite3 import connect
from requests import get
from bs4 import BeautifulSoup
from sys import argv

connection = connect(argv[2])
cursor = connection.cursor()

def init():
	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS 'channel' (
			id TEXT PRIMARY KEY,
			title TEXT,
			description TEXT NULLABLE
		)
		"""
		)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS 'post' (
			id INTEGER,
			channel TEXT REFERENCES channel(id),
			text TEXT
		)
		"""
		)

def parse_info(id: str):
	bs = BeautifulSoup(get("https://t.me/%s" % (id)).content, 'html.parser')

	title = list(filter(lambda x: x.has_attr('class') and "tgme_page_title" \
		in x['class'], bs.find_all('div')))[0].get_text().strip()

	description = list(filter(lambda x: x.has_attr('class') \
		and "tgme_page_description" in x['class'], \
		bs.find_all('div')))

	if len(description) != 0:
		description = description[0].get_text().strip()  # Here is a bs4's '\n' oddity.
	else:
		description = 'NULL'
	if cursor.execute("""
		SELECT EXISTS(SELECT * FROM channel WHERE id='%s' LIMIT 1)
		""" % (id,)).fetchone()[0]:
		pass
	else:
		cursor.execute("INSERT INTO channel VALUES (\'%s\', \'%s\', \'%s\')"
			% (id, title, description))
		connection.commit()


def parse_post(id: str, post: int):
	bs = BeautifulSoup(get("https://t.me/%s/%i" % (id, post)).content,
		'html.parser')

	if 'View context' not in bs.get_text():
		text = list(filter(lambda x: x.has_attr('name') \
			and x['name'] == 'twitter:description', bs.find_all('meta')))[0]['content']
		cursor.execute("INSERT INTO post VALUES (%i, \'%s\', \'%s\')"
			% (post, id, text))


def parse_posts(id: str, first_post=1, last_post=0, progress=False):
	bs = BeautifulSoup(get("https://t.me/s/%s" % (id)).content, 'html.parser')

	if last_post == 0:
		last_post = int(list(filter(lambda x: x.has_attr('class') \
			and "tgme_widget_message_wrap" in x['class'],
			bs.find_all('div')))[-1].div['data-post'].split('/')[1])

	for i in range(first_post, last_post + 1):
		print(f"\rProgress: {int(i / last_post * 100)}% [{i} / {last_post}]",
			end="")
		parse_post(id, i)
	connection.commit()


if __name__ == "__main__":
	init()
	parse_info(argv[1])
	parse_posts(argv[1], progress=True)
