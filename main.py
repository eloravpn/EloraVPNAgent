# This is a sample Python script.
import csv
import getopt
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from urllib.parse import unquote

import requests as requests

import config

abspath = sys.path[0]


def get_valid_ip():
    ip = "192.168.1.1"
    try:
        ip = requests.get("https://api.ipify.org").content.decode("utf8")
        print("My public IP address is: {}".format(ip))
    except Exception:
        print(f"Error in get public ip address!")

    return ip


def get_auth_token():
    r = requests.post(
        config.ELORA_BASE_API_URL + config.ELORA_TOKEN_PATH,
        data={"username": config.ELORA_USER_NAME, "password": config.ELORA_PASSWORD},
    ).json()

    return r


def send_test_result(
        access_token_: str,
        url: str,
        client_name: str,
        client_ip: str,
        test_url: str,
        remark_: str,
        port_: int,
        domain_: str,
        sni: str,
        delay: int,
        ping: int,
        develop: bool = False,
        success: bool = True,
):
    payload = json.dumps(
        {
            "client_name": client_name,
            "client_ip": client_ip,
            "test_url": test_url,
            "remark": remark_,
            "port": port_,
            "domain": domain_,
            "sni": sni,
            "delay": delay,
            "ping": ping,
            "develop": develop,
            "success": success,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token_,
    }

    response = requests.request("POST", url, headers=headers, data=payload)


def cli(args):
    """Send results of test via command line"""

    usage = "usage: python main.py " + "[-V|--version] [-h|--help] [-u|--url] "

    test_url = "https://www.google.com/generate_204"

    try:
        opts, args = getopt.getopt(args, "Vhu:", ["version", "help", "url="])
    except getopt.GetoptError:
        sys.exit(usage)

    for opt, arg in opts:
        if opt in ("-V", "--version"):
            sys.exit("Cloudflare library version: %s" % 0.1)
        if opt in ("-h", "--help"):
            sys.exit(usage)
        if opt in ("-u", "--url"):
            test_url = arg

    run_xray_knife()

    # send_csv_records(test_url=test_url)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    cli(args)


def run_xray_knife():
    subprocess.run(abspath + "/tools/xray-knife --version", shell=True)


def send_csv_records(test_url: str):
    file = open(config.CSV_FILE_PATH)
    csvreader = csv.reader(file)
    api_url = config.ELORA_BASE_API_URL + "/api/monitoring-results/"
    public_ip = get_valid_ip()
    token = get_auth_token()
    access_token = token["access_token"]
    next(csvreader)
    for row in csvreader:
        url = row[0]

        status = row[1]
        delay = row[4]
        url_decode = unquote(url)

        result = re.search("@(.*)\?", url_decode)
        group = result.group(1)

        port = group.split(":")[1]
        domain = group.split(":")[0]

        remark = url_decode.split("#")[1]

        success = status == "passed"

        send_test_result(
            access_token_=access_token,
            url=api_url,
            client_name=config.CLIENT_NAME,
            client_ip=public_ip,
            test_url=test_url,
            remark_=remark,
            port_=int(port),
            domain_=domain,
            sni="",
            delay=int(delay),
            ping=0,
            success=success,
        )


if __name__ == "__main__":
    main()
