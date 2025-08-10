import os
import re
import time
import argparse
import requests
from datetime import datetime

# --- Argument Parsing ---
parser = argparse.ArgumentParser(
    description="RoboBack: A tool that helps you travel back in time to find archived robots.txt files of a target."
)

parser.add_argument("-d", required=True, type=str,
                    help="Target domain (e.g., example.com)")
parser.add_argument("-o", type=str,
                    help="Path to save the results")
parser.add_argument("-tf", type=str,
                    help="Filter results by year (e.g., 2021 or 2020,2021)")

args = parser.parse_args()
domain = args.d

if args.tf:
    years_filter = [year for year in args.tf.split(",")]

if args.o:
    if not os.path.exists(args.o):
        os.system(f"touch {args.o}")

# --- Colors ---
red     = "\033[31m"
blue    = "\033[34m"
green   = "\033[32m"
name_bg = "\033[48;5;235m"
gray_bg = "\033[48;5;237m"
reset   = "\033[0m"


# --- Functions ---
def extractRobots(snapshots: list) -> list:
    robots = []

    for snap in snapshots:
        if re.search(r"/robots\.txt$", snap[1]):
            robots.append(snap)

    if args.tf:
        filtered_robots = []
        for robot in robots:
            timestamp = robot[0]
            year = timestamp[:4]
            if year in years_filter:
                filtered_robots.append(robot)

        robots.clear()
        return filtered_robots
    else:
        return robots


def getRobotsContent(robots: list) -> None:
    notFounds = 0
    success = 0

    for snap in robots:
        timestamp = snap[0]
        date = datetime.strptime(timestamp, "%Y%m%d%H%M%S").date()
        url = snap[1]
        archive_url = f"https://web.archive.org/web/{timestamp}if_/{url}"

        response = requests.get(archive_url)
        if response.status_code == 200:
            content = f"<--------------- {timestamp} ({date}) --------------->\n{response.text}\n{red}url:{reset} {url}"
            print(content)

            if args.o:
                with open(args.o, "a") as f:
                    f.write(content + "\n")

            success += 1

        elif response.status_code == 404:
            notFounds += 1

    print(f"{blue}[INFO]{reset} {green}{success}{reset} robots.txt files {green}successfully{reset} read")
    print(f"{blue}[INFO]{reset} {red}{notFounds}{reset} robots.txt files {red}failed{reset} to read (404 Not Found)")


def banner():
    me = f"created by: " + name_bg + red + "NakuTenshi" + reset + reset
    print(fr"""
{blue}+---------------------------------------------------------------------------+{reset}
{blue}|{reset}  _____       _           ____             _                               {blue}|{reset}
{blue}|{reset} |  __ \     | |         |  _ \           | |                              {blue}|{reset}
{blue}|{reset} | |__) |___ | |__   ___ | |_) | __ _  ___| | __                           {blue}|{reset}
{blue}|{reset} |  _  // _ \|  _ \ / _ \|  _ < / _` |/ __| |/ /                           {blue}|{reset}
{blue}|{reset} | | \ \ (_) | |_) | (_) | |_) | (_| | (__|   <  {me}    {blue}|{reset}
{blue}|{reset} |_|  \_\___/|____/ \___/|____/ \__,_|\___|_|\_\ fuck this people          {blue}|{reset}
{blue}|{reset}                                                                           {blue}|{reset}
{blue}+---------------------------------------------------------------------------+{reset}
""")


def main():
    os.system("clear")
    banner()

    print(f"<------------------ {green}Status{reset} ------------------>")
    print(f"{blue}[INFO]{reset} Target: {red}{domain}{reset}")
    
    if args.tf:
        print(f"{blue}[INFO]{reset} Filtering by year(s): {blue}{','.join(years_filter)}{reset}")
    if args.o:
        print(f"{blue}[INFO]{reset} Saving results to: {green}{args.o}{reset}")

    print(f"{blue}[INFO]{reset} Sending request to {green}archive.org{reset}")
    print(f"\n<------------------- {green}Logs{reset} ------------------->")

    response = requests.get("https://web.archive.org/cdx/search/cdx", params={
        "url": domain,
        "matchType": "domain",
        "fl": "timestamp,original",
        "collapse": "digest",
        "output": "json"
    })

    if response.status_code == 200:
        snapshots = response.json()[1:]
        robots = extractRobots(snapshots=snapshots)

        print(f"{blue}[INFO]{reset} {red}{len(robots)}{reset} robots.txt snapshot(s) found.")
        print(f"{blue}[INFO]{reset} Reading each file...\n")
        time.sleep(0.5)
        getRobotsContent(robots)
    else:
        print(f"{red}[FAIL]{reset} Request failed.")
        print(f"{blue}[INFO]{reset} Status code: {response.status_code}")


# --- Entry Point ---
if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"{red}[ERROR]{reset} your internet is ass, fix your internet first of anything")
    except KeyboardInterrupt:
        print("\nbye :)")
        exit()
    except Exception as e:
        print(f"[{red}ERROR]{reset} there is an error: {e}")
