#!/usr/bin/env python3
"""Main jesql application to be run by the user
"""
import jesql_client

with jesql_client.Interface() as db:
    db.accept_user_input()
