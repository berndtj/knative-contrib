#! /usr/bin/env python3

import argparse
import datetime
import json
import requests
import re
import yaml

token = "bb74c7f01a52591fa03809897150ec43ab7b8c00"

def guess_org(users, email):
    for org, values in users.items():
        pattern = values.get("pattern")
        if pattern is not None:
            if re.match(pattern, email):
                return org
        if email in values.get("users", []):
            return org
    return "Unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="github repo (serving|build|eventing|docs)")
    parser.add_argument("--org", "-o", dest="org", default="knative", help="github org")
    parser.add_argument("--since", "-s", dest="since", type=int, default=30, help="number of days for search")
    parser.add_argument("--db", "-d", dest="db", default="github-users.yaml", help="github users db file (yaml)")
    ns = parser.parse_args()

    start_date = datetime.datetime.now() - datetime.timedelta(days=ns.since)

    with open(ns.db) as fh:
        users = yaml.load(fh)

    url = "https://api.github.com/repos/knative/%s/commits?since=%s" % (ns.repo, start_date.isoformat())

    resp = requests.get(url, headers={"authorization": "token %s" % token})

    commits = {}

    while resp.ok:
        for c in resp.json():
            key = c["commit"]["author"]["name"]
            email = c["commit"]["author"]["email"]
            org = guess_org(users, email)
            commits.setdefault(key, {"email": email, "org": org, "num": 0})
            commits[key]["num"] += 1
        if not "Link" in resp.headers:
            break
        links = resp.headers["Link"].split(",")
        for l in links:
            m = re.search(r"<([^>]+)>; rel=\"next\"", l)
            if m:
                n = m.groups()[0]
                resp = requests.get(n, headers={"authorization": "token %s" % token})
                break
        else:
            break

    commit_list = [(k, v["email"], v["org"], v["num"]) for (k, v) in commits.items()]

    commit_list.sort(key=lambda x: x[3], reverse=True)

    print("\nIndividual Contributors Ranking (%d total)\n" % len(commit_list))

    orgs = {}
    rank = 1
    last_num = 0
    for i, c in enumerate(commit_list):
        name, email, org, num = c
        orgs.setdefault(org, 0)
        orgs[org] += num
        if num != last_num:
            last_num = num
            rank = i + 1
        print("%d - %s <%s> %d commits - %s" % (rank, name, email, num, org))

    org_list = [(k, v) for (k, v) in orgs.items()]
    org_list.sort(key=lambda x: x[1], reverse=True)

    print("\nOrganization Summary\n")

    for t in org_list:
        print("%s - %d" % (t[0], t[1]))



if __name__ == "__main__":
    main()

