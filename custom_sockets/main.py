import socket
import ssl
import json


class SimpleHTTPClient:
    def __init__(self, timeout=10):
        self.timeout = timeout

    def _create_connection(self, host, port):
        sock = socket.create_connection((host, port), timeout=self.timeout)
        return sock

    def _send_request(self, host, request):
        with self._create_connection(host, 443) as sock:
            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=host) as secure_sock:
                secure_sock.sendall(request.encode('utf-8'))
                response = self._receive_response(secure_sock)
        return response

    def _receive_response(self, sock):
        response_parts = []
        while True:
            part = sock.recv(4096)
            if not part:
                break
            response_parts.append(part)
        return b''.join(response_parts)

    def get(self, url):
        """Отправляет GET-запрос."""
        if url.startswith('https://'):
            host = url[8:url.find('/', 8)]
            path = url[url.find('/', 8):] or '/'
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            response = self._send_request(host, request)
            return self._parse_response(response)
        else:
            raise ValueError("URL должен начинаться с 'https://'")

    def post(self, url, data=None):
        """Отправляет POST-запрос."""
        if url.startswith('https://'):
            host = url[8:url.find('/', 8)]
            path = url[url.find('/', 8):] or '/'
            if data is not None:
                body = json.dumps(data)
                content_length = len(body)
                request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/json\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{body}"
            else:
                request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            response = self._send_request(host, request)
            return self._parse_response(response)
        else:
            raise ValueError("URL должен начинаться с 'https://'")

    def _parse_response(self, response):
        headers, body = response.split(b'\r\n\r\n', 1)
        status_line = headers.split(b'\r\n')[0]
        headers_dict = {k: v for k, v in (line.split(b': ', 1) for line in headers.split(b'\r\n')[1:])}
        return {
            'status_line': status_line.decode('utf-8'),
            'headers': headers_dict,
            'body': json.loads(body) if b'Content-Type: application/json' in headers else body.decode('utf-8'),
        }


client = SimpleHTTPClient()

# Пример GET-запроса
response = client.get('https://jsonplaceholder.typicode.com/posts/1')
print("GET ответ:", response)

# Пример POST-запроса
data = {
    'title': 'foo',
    'body': 'bar',
    'userId': 1
}
response = client.post('https://jsonplaceholder.typicode.com/posts', data=data)
print("POST ответ:", response)
