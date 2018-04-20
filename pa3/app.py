#!/usr/bin/env python3.6
"""Main jesql application to be run by the user
"""
import argparse
import jesql_client


def main():
    parser = argparse.ArgumentParser(description='Runs an interactive database management system')
    parser.add_argument('-s', '--silent', action='store_true', help='omits jesql> prompt')
    args = parser.parse_args()

    with jesql_client.Interface(args) as db:
        db.accept_user_input()

if __name__ == '__main__':
    main()
