#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_jwt_extended import create_access_token
from app.extensions.jwt.uitls import add_token_to_database
from app.utils.secure import encrypt_str


class TestAuth:
    def test_auth(self, flask_app, flask_app_client, regular_user):
        user_hash = encrypt_str(regular_user.email)
        query_string = "user_id=" + user_hash
        access_token = create_access_token(identity=regular_user.email)
        flask_app_client.connect("/auth", query_string=query_string)
        assert flask_app_client.is_connected("/auth")

        flask_app_client.emit(
            "authenticate", {"token": access_token}, namespace="/auth"
        )
        assert flask_app_client.is_connected("/auth") is False
        add_token_to_database(access_token, flask_app.config["JWT_IDENTITY_CLAIM"])

        flask_app_client.connect("/auth", query_string=query_string)
        flask_app_client.emit(
            "authenticate", {"token": access_token}, namespace="/auth"
        )
        assert flask_app_client.is_connected("/auth")

        flask_app_client.emit("test", namespace="/auth")
        data = flask_app_client.get_received("/auth")
        assert data[0]["name"]["data"] == "Hello, World"
        flask_app_client.disconnect("/auth")
        flask_app_client.connect("/auth", query_string=query_string)
        flask_app_client.emit("test", namespace="/auth")
        assert flask_app_client.is_connected("/auth") is False

        flask_app_client.connect("/auth", query_string="121212")
        flask_app_client.emit("test", namespace="/auth")
        assert flask_app_client.is_connected("/auth") is False
