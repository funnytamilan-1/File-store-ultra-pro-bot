import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")

from urllib.parse import parse_qs
from unittest.mock import patch
from utils.link_generator import generate_secure_link, verify_secure_link


def split_link(value):
    path, query = value.split("?", 1)
    return path, parse_qs(query)


def test_signed_link_is_valid():
    token = generate_secure_link("telegram-file-id", 120)
    file_id, query = split_link(token)
    assert verify_secure_link(file_id, int(query["exp"][0]), query["sig"][0])


def test_signed_link_rejects_tampered_signature():
    token = generate_secure_link("telegram-file-id", 120)
    file_id, query = split_link(token)
    assert not verify_secure_link(file_id, int(query["exp"][0]), "0" * 64)


def test_signed_link_rejects_expired_token():
    with patch("utils.link_generator.time.time", return_value=1000):
        token = generate_secure_link("telegram-file-id", 1)
    file_id, query = split_link(token)
    with patch("utils.link_generator.time.time", return_value=1002):
        assert not verify_secure_link(file_id, int(query["exp"][0]), query["sig"][0])
