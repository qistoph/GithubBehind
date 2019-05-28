#!/usr/bin/python -u

import json
import urllib2

import config

def github_request(uri):
    url = 'https://api.github.com/%s?client_id=%s&client_secret=%s' % (uri, config.client_id, config.client_secret)
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
    return json.load(response)

try:
    print "Retrieving repos..."
    repos = github_request('users/%s/repos' % (config.userid))
    #print repos
    #print json.dumps(repos, indent = True)
    print "%d repos found" % (len(repos))

    for repo in repos:
        repo_printed = False

        if repo['fork']:
            repo_full_name = repo['full_name']
            repo_owner = repo['owner']['login']
            #print json.dumps(repo, indent = True)

            repo_details = github_request('repos/%s' % repo_full_name)
            #print json.dumps(repo_details, indent = True)
            parent_full_name = repo_details['parent']['full_name']
            parent_owner = repo_details['parent']['owner']['login']

            local_branches = github_request('repos/%s/branches' % repo_full_name)
            parent_branches = github_request('repos/%s/branches' % parent_full_name)

            #for branch in [filter(lambda x: x in parent_branches, sublist) for sublist in

            for branch in list(set([x['name'] for x in local_branches]) & set([x['name'] for x in parent_branches])):
                branch_status = github_request('repos/%s/compare/%s:%s...%s:%s' % (parent_full_name, parent_owner, branch, repo_owner, branch))
                #print json.dumps(branch_status, indent = True)

                behind = branch_status['behind_by']
                ahead = branch_status['ahead_by']

                if behind > 0 or ahead > 0:
                    if not repo_printed:
                        print 'Repo: %s (%s)' % (repo_full_name, repo_owner)
                        print 'Parent: %s (%s)' % (parent_full_name, parent_owner)
                        repo_printed = True
                    print '- %s behind: %d, ahead: %d' % (branch, behind, ahead)

            #print json.dumps(refs, indent = True)

        if repo_printed:
            print ''


except Exception as e:
    print e
