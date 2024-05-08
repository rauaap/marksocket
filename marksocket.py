#!/usr/bin/env python3
from collections import namedtuple
import socket
import fcntl
import os
import signal
import json
import argparse
import tomllib
import mimetypes
import importlib.util
import markdown

DEFAULT_PORT = 44444

def cli():
    arg_parser = argparse.ArgumentParser(
        prog = 'marksocket',
        description = 'Serve markdown documents to the browser with live reload.'
    )

    arg_parser.add_argument('markdown_file', help = 'The markdown file to serve.')
    arg_parser.add_argument('-c', '--config', help = 'Configuration file.')

    arg_parser.add_argument(
        '-p',
        '--port',
        help = f'The port to serve at. Defaults to {DEFAULT_PORT}.',
        type = int,
    )

    arg_parser.add_argument(
        '-x',
        '--extension',
        help = 'Python-Markdown extension to load',
        action = 'append',
        default = []
    )

    arg_parser.add_argument(
        '-s',
        '--stylesheet',
        help = 'Stylesheet to apply to the HTML parsed from the markdown.',
        action = 'append',
        default = []
    )

    arg_parser.add_argument(
        '-j',
        '--javascript',
        help = 'JavaScript file to add to the HTML parsed from the markdown.',
        action = 'append',
        default = []
    )

    return arg_parser.parse_args()


def get_configuration():
    args = cli()
    config_file = args.config
    config_path = os.path.expanduser('~/.config/marksocket/config.toml')

    if config_file is None and os.path.isfile(config_path):
        config_file = config_path

    if config_file:
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)
    else:
        config = {}

    watch_dir = os.path.dirname(markdown_file := args.markdown_file) or '.'
    port = args.port or config.get('port') or DEFAULT_PORT

    extensions = []
    css = []
    js = []

    for x in [*config.get('extension', []), *args.extension]:
        extensions.append(x)

    for s in [*config.get('stylesheet', []), *args.stylesheet]:
        with open(os.path.expanduser(s)) as f:
            css.append(f.read())

    for j in [*config.get('javascript', []), *args.javascript]:
        with open(os.path.expanduser(j)) as f:
            js.append(f.read())

    Configuration = namedtuple('Configuration', [
        'markdown_file',
        'watch_dir',
        'port',
        'extensions',
        'js',
        'css'
    ])

    return Configuration(markdown_file, watch_dir, port, extensions, js, css)


def update_content(markdown_file, extensions):
    with open(markdown_file) as f:
        content = f.read()

    return markdown.markdown(content, extensions = extensions)


def handle(client, subscribers, configuration):
    request = client.recv(1024)

    if len(request) == 0:
        client.close()
        return

    path = request.decode().split('\n')[0].split(' ')[1]

    if path == '/events':
        subscribers.append(client)

        client.sendall((
            'HTTP/1.1 200 OK\n'
            'Cache-Control: no-store\n'
            'Content-Type: text/event-stream\n\n'
        ).encode())
    elif path == '/':
        content = update_content(
            configuration.markdown_file,
            configuration.extensions
        )

        client.sendall((
            'HTTP/1.1 200 OK\n'
            'Content-Type: text/html\n\n'
            '<head>'
                '<meta charset="utf-8">'
                f'<script>{"; ".join(configuration.js)}</script>'
                f'<style>{" ".join(configuration.css)}</style>'
            '</head>'
            f'<body>{content}<body>'
            '<script>'
                'const eventSource = new EventSource("/events");'
                'eventSource.onmessage = (msg) => {'
                    'document.body.innerHTML = JSON.parse(msg.data);'
                '}'
            '</script>'
        ).encode())

        client.close()
    else:
        file = os.path.join( configuration.watch_dir, path.lstrip('/') )
        mimetype, _ = mimetypes.guess_type(file)

        if not os.path.isfile(file):
            client.sendall(b'HTTP/1.1 404 Not Found\n\n')
            client.close()
            return;

        with open(file, 'rb') as f:
            client.sendall(
                b'HTTP/1.1 200 OK\n' +
                f'Content-Type: {mimetype}\n\n'.encode() +
                f.read()
            )

        client.close()


def serve(configuration, subscribers):
    with socket.socket() as s:
        # Allow reusing the same socket
        # if the previous one is still in TIME_WAIT state
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', configuration.port))
        s.listen()

        print(
            'Marksocket listening at:\n'
            f'http://localhost:{configuration.port}\n'
            'Stop with ctrl+c'
        )

        while True:
            try:
                client, _ = s.accept()
                handle(client, subscribers, configuration)
            except KeyboardInterrupt:
                break


def main():
    configuration = get_configuration()
    subscribers = []

    def notify_subscribers(signum = None, frame = None):
        html = update_content(
            configuration.markdown_file,
            configuration.extensions
        )

        for client in subscribers:
            try:
                client.send(f'data: {json.dumps(html)}\n\n'.encode())
            except BrokenPipeError:
                subscribers.remove(client)

    # Get the file descriptor for fcntl
    fd = os.open(configuration.watch_dir,  os.O_RDONLY)

    # Send SIGIO on modify
    fcntl.fcntl(
        fd,
        fcntl.F_NOTIFY,
        fcntl.DN_MODIFY | fcntl.DN_MULTISHOT
    )

    # Connect to the signal
    signal.signal(signal.SIGIO, notify_subscribers)

    try:
        serve(configuration, subscribers)
    finally:
        os.close(fd)

if __name__ == "__main__":
    main()
