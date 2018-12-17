#!/usr/bin/env python3

import time

import requests
import terminaltables

members = [
    ["Ivan Mikushin", "imikushin"],
    ["Sabari Murugesan", "neosab"],
    ["Berndt Jung", "berndtj"],
    ["Karol Stepniewski", "kars7e"],
    ["Nick Tenczar", "tenczar"],
    ["Zimeng Yang", "zimengyang"],
    ["Zhiming Peng", "pzmrzy"],
]

apis = {
    "issues": ["https://api.github.com/search/issues", "application/vnd.github.symmetra-preview+json", "bb74c7f01a52591fa03809897150ec43ab7b8c00"],
    "comments": ["https://api.github.com/search/comments", "application/vnd.github.cloak-preview", "bb74c7f01a52591fa03809897150ec43ab7b8c00"],
}

metrics = {
    "issues submitted": ["issues", "%s?q=is:issue+archived:false+user:knative+author:\"%s\"", "total_count"],
    "issues resolved (with contributor PR)": None,
    "issues commented on": ["issues", "%s?&q=is:issue+archived:false+user:knative+commenter:\"%s\"", "total_count"],
    "PRs submitted": ["issues", "%s?&q=is:pr+archived:false+user:knative+author:\"%s\"", "total_count"],
    "PRs accepted (merged)": ["issues", "%s?&q=is:pr+archived:false+user:knative+author:\"%s\"", "total_count"],
    "documentation": ["issues", "%s?&q=is:pr+archived:false+repo:knative/docs+is:merged+author:\"%s\"", "total_count"],
    "bug fixes": ["issues", "%s?&q=is:pr+archived:false+user:knative+-repo:knative/docs+is:merged+author:\"%s\"+", "total_count"],
    "PRs reviewed": ["issues", "%s?&q=is:pr+archived:false+user:knative+commenter:\"%s\"", "total_count"],
}

def report():
    table = []
    header = ["",]
    for member in members:
        member_name, _ = member
        header.append(member_name)
    table.append(header)
    for name, metric in metrics.items():
        if metric is None:
            table.append([name,])
            continue
        mtype, query, path = metric
        url, content_type, token = apis[mtype]
        row = [name,]
        for member in members:
            _, github_id = member
            resp = requests.get(query % (url, github_id), headers={"authorization": "token %s" % token, "accept": content_type})
            if resp.ok:
                payload = resp.json()
                row.append(payload[path])
            else:
                print("error getting %s: %s" % (name, resp.json()))
                resp = requests.get("https://api.github.com/rate_limit", headers={"authorization": "token %s" % token})
                search = resp.json()["resources"]["search"]
                print(search)
                print("limit resets in %s" % (time.time() - search["reset"]))
            # respect the rate limit!
            time.sleep(3)
        table.append(row)
    ttable = terminaltables.AsciiTable(table)
    print(ttable.table)

if __name__ == "__main__":
    report()