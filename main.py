import json
import re

import requests

# The public org where new repos will be created.
PUBLIC_ORG = 'asgharlabs'

# The repo where folks will request new repos for the public org in the form of a comment
GHE_REQUEST_REPO = 'https://api.github.com/repos/asgharlabs/team-request'


def _get_info_from_body(body):

    m = re.search(r'\* name:(.*)(\r\n|$)', body)
    team_name = m.group(1).strip() if m else None
    team_name = team_name.strip() if team_name else None

    m = re.search(r'\* users:(.*)(\r\n|$)', body)
    users = m.group(1).strip() if m else []
    users = [x.strip() for x in users.split(',')] if users else []

    m = re.search(r'\* description:(.*)(\r\n|$)', body)
    description = m.group(1).strip() if m else ''

    m = re.search(r'\* privacy:(.*)(\r\n|$)', body)
    privacy = m.group(1).strip() if m else 'closed'
    privacy = privacy.strip() if privacy else 'closed'

    return {'team_name': team_name, 'users': users,
            'description': description, 'privacy': privacy}

def _post_a_comment(issue_number, message, ghe_token):
    # post comment on issue -- https://developer.github.com/v3/issues/comments/#create-a-comment
    headers = {'Authorization': 'token %s' % ghe_token}
    url = GHE_REQUEST_REPO + '/issues/' + str(issue_number) + '/comments'
    payload = {"body": message}
    r = requests.post(url, headers=headers, json=payload)


def main(params):

    # set up commonmly used variables
    issue_number = params['issue']['number']
    gh_token = params['TOKEN']
    ghe_token = gh_token
    headers = {'Authorization': 'token %s' % gh_token}

    # case 1: issue is created or edited, perform some checking
    if 'action' in params and params['action'] == 'opened' or params['action'] == 'edited':

        failed_checks = 0

        # comment if the structure is incorrect
        body = params['issue']['body']
        info = _get_info_from_body(body)
        message = "parsed the following properties:\n\n`" + str(info) + "`\n\nif not correct, modify the original issue body."
        print(message)
        _post_a_comment(issue_number, message, ghe_token)

        # check 1: comment if repo name is None
        if info['team_name'] is None:
            message = "Unable to parse a team name. We think it's: " + str(info['team_name'])
            _post_a_comment(issue_number, message, ghe_token)
            failed_checks = failed_checks + 1

        # check 2: does team exist?
        if info['team_name']:
            url = 'https://api.github.com/orgs/' + PUBLIC_ORG + '/teams/' + info['team_name']
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                message = "Team name `" + info['team_name'] + "` already exists at [github.com/" + PUBLIC_ORG + "](github.com/" + PUBLIC_ORG + "), choose another name"
                details = message

                _post_a_comment(issue_number, message, ghe_token)
                failed_checks = failed_checks + 1

        # check 3: does user exist?
        for user in info['users']:
            url = 'https://api.github.com/users/' + user
            r = requests.get(url)
            if r.status_code != 200:
                message = "User `" + user + "` does not exist on [github.com](github.com), ensure username is correct"
                details = message
                _post_a_comment(issue_number, message, ghe_token)
                failed_checks = failed_checks + 1

        # check 4: is user in the org?
        for user in info['users']:
            url = 'https://api.github.com/orgs/' + PUBLIC_ORG + '/members/' + user
            r = requests.get(url, headers=headers)
            if r.status_code != 204:
                message = "User `" + user + "` is not in the [github.com/" + PUBLIC_ORG +"](github.com/" + PUBLIC_ORG + ") organization please invite them to join the org."
                details = message
                _post_a_comment(issue_number, message, ghe_token)
                failed_checks = failed_checks + 1

        # check 5: comment if repo name is None
        if info['privacy'] is None:
            message = "You haven't set a privacy level, please choose from `secret` or `closed`"
            _post_a_comment(issue_number, message, ghe_token)
            failed_checks = failed_checks + 1

        # got to the end of the checks
        if failed_checks == 0:
            message = 'Detected ' + str(failed_checks) + ' issues with this request, it will be approved and automatically closed.'
            _post_a_comment(issue_number, message, ghe_token)
            _post_a_comment(issue_number, "/approve", ghe_token)
            # close the issue -- https://developer.github.com/v3/issues/#edit-an-issue
            headers = {'Authorization': 'token %s' % ghe_token}
            url = GHE_REQUEST_REPO + '/issues/' + str(issue_number)
            payload = {'state': "closed"}
            requests.patch(url, headers=headers, data=json.dumps(payload))
        else:
            message = 'Detected ' + str(failed_checks) + ' issues with this request, see comments'
            _post_a_comment(issue_number, message, ghe_token)
        return {
            'message': message
        }

    # case 2: /approve was left, so actually create the team
    elif 'action' in params and params['action'] == 'created' and params['comment']['body'].strip() == '/approve':

        body = params['issue']['body']
        info = _get_info_from_body(body)

        sender = params['sender']['login']
        if sender == 'jjasghar' :
            print("approved by: " + sender)
        else:
            message = 'approve comment made by unauthorized user, please wait for an authorized user to approve'
            _post_a_comment(issue_number, message, ghe_token)
            return {'message': message}

        # create the team -- https://developer.github.com/v3/teams/#create-team
        url = 'https://api.github.com/orgs/' + PUBLIC_ORG + '/teams'
        payload = {
            'name': info['team_name'],
            'description': info['description'],
            'maintainers': info['users'],
            'privacy': info['privacy'],
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print("Tried to post to the API to create the team")
        if r.status_code != 201:
            message = "could not create team: " + r.text
            _post_a_comment(issue_number, message, ghe_token)
            return {'message': message}
        else:
            message = "created team: " + info['team_name'] + ". now adding users and teams"
            _post_a_comment(issue_number, message, ghe_token)

        message = "created team https://github.com/orgs/" + PUBLIC_ORG +"/teams/" + info['team_name'] + " with admins: " + str(info['users'])
        _post_a_comment(issue_number, message, ghe_token)
        return {'message': message}

    else:
        message = "unable to process, ping @jjasghar"
        return {'message': message}
