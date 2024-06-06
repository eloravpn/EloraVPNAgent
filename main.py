# This is a sample Python script.
import csv
import getopt
import json
import re
import subprocess
import sys
import time
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
    if response and response.status_code == 200:
        print(f"Success send test result for {remark_}")


def get_configs(base_sub_url: str, override_domain: str, q: str, plain: bool = True):
    full_url = f"{base_sub_url}?address={override_domain}&q={q}&plain={plain}"
    print(f"Try to get configs by {full_url}")
    response = requests.request("GET", full_url, timeout=15)
    return response.text


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

    run_test()


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    cli(args)


def get_relative_file_path(file_path: str):
    if file_path.startswith("./"):
        return file_path.replace("./", f"/{abspath}")
    else:
        return file_path


def run_test():
    file = open(get_relative_file_path(config.SUBS_CSV_FILE_PATH))
    csvreader = csv.reader(file)
    q = config.CONFIGS_Q

    # next(csvreader)
    for idx, row in enumerate(csvreader):
        print(f"There are {len(row)} columns in row#{idx}")
        base_sub_url = row[1]

        for i in range(2, len(row)):
            now = time.time()
            domain = row[i]
            print(f"Run text for {row[i]} by {base_sub_url}")
            configs = get_configs(base_sub_url, domain, q)

            configs_file_name = get_relative_file_path(
                f"{config.CONFIGS_DIR}/config-{domain}-{now}.txt"
            )

            print(f"Configs file: {configs_file_name}")

            test_output_file_name = get_relative_file_path(
                f"{config.RESULTS_DIR}/test-results-{domain}-{now}.txt"
            )

            print(f"Test results file: {test_output_file_name}")

            file = open(configs_file_name, "w")
            file.write(configs)
            file.close()

            run_xray_knife(
                configs_file=configs_file_name,
                result_file=test_output_file_name,
                test_url=config.TEST_URL,
            )

            send_csv_records(
                test_url=config.TEST_URL, test_result_file=test_output_file_name
            )


def run_xray_knife(configs_file: str, result_file: str, test_url: str):
    subprocess.run(
        abspath
        + f"/tools/xray-knife net http -f {configs_file} -x csv -s -u {test_url} -o  {result_file}",
        shell=True,
    )


def send_csv_records(test_url: str, test_result_file: str):
    file = open(test_result_file)
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
