import re
import os
from urllib.parse import urljoin, urlparse

import requests
import click


__version__ = '0.1-dev'

session = requests.Session()
saved = set()


def find_links(content, from_url):
    '''Returns content with local links and set of local links.
       Strips all query parameters or anchors.'''

    url_re = re.compile('(href=|src=|url\()"(.*?)"')
    links = (x[1] for x in url_re.findall(content))

    local = urlparse(from_url).netloc
    local_links = set()
    for orig in links:
        _, netloc, path, _, _, fragment = urlparse(orig)
        if netloc not in (local, ''):
            continue

        link = urljoin(from_url, path, fragment)
        short = urljoin(path, fragment) or '/'

        result = (orig, link, short)
        local_links.add(result)

    for orig, link, short in local_links:
        orig = '"{}"'.format(orig)
        short = '"{}"'.format(short)
        content = content.replace(orig, short)

    local_links = {x[1] for x in local_links}
    return content, local_links


def file_path(link):
    '''Generates file path from url.'''

    path = urlparse(link).path
    if path == '' or path.endswith('/'):
        path = path + 'index.html'

    path = os.path.join('static', *path.split('/'))
    return path


def save_content(content, path):
    '''Saves str or bytes to a given path.'''

    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    if isinstance(content, str):
        content = content.encode('utf-8')

    with open(path, 'wb') as f:
        f.write(content)


def ghost(link, local):
    '''Recursively generates static site from Ghost blog.'''

    path = file_path(link)
    if path in saved:
        return link

    saved.add(path)
    yield path

    r = session.get(link)

    content_type = r.headers['content-type']
    if content_type.startswith('text'):
        content, links = find_links(r.text, link)
    else:
        content, links = r.content, []

    save_content(content, path)

    for i in links:
        yield from ghost(i, local)


@click.command()
@click.option('-s', '--source',
              default='http://localhost:2368',
              help='URL of Ghost blog to dump.')
def cli(source):
    click.echo('\n    ghostbuster {}'.format(__version__))
    click.echo('\n    {}\n'.format(source))

    buster = ghost(source, source)

    for i, item in enumerate(buster, 1):
        click.echo('{:5} {}'.format(i, item))


if __name__ == '__main__':
    cli()
