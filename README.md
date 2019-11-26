# requests-a-team-bot

Hi! :wave: You found the way to create a team for [github.com/asgharlabs/team-request](https://github.com/asgharlabs/team-request)! Read the instructions below on how to get started.

## How to use this repo?

1. [Create an issue](https://github.ibm.com/Open-source/request-a-team-bot/issues/new?assignees=&labels=&template=request-a-repository.md&title=%5BIBM+GH+REPO+REQUEST%5D). Here's an example of a request

   ```ini
   * name: my_awesome_team
   * users: markstur, rhagarty
   * description: a short description on why this team exists
   * privacy: closed
   ```

   * Please only request one team a time.
   * Use [PUBLIC github](https://github.com/) user names. Try to log into [https://github.com](https://github.com) if you don't know your user name.

1. Each issue will be validated for the following:

  * Is the proposed team name available?
  * Are all the initial users listed in the asgharlabs org?
  * Do all users on github.com?
  * Privacy can be either `closed` or `secret`, default is `closed`.
    * secret - only visible to organization owners and members of this team.
    * closed - visible to all members of this organization.

Once there are no issues with the validation, the team will be automatically created, and the users assigned. If there are issues with the validation, then address the issues and edit the issue.

> **NOTE**: Closing and re-opening the issue will re-trigger the validation.

## How's it work?

The code in [main.py](main.py) is run as a serverless action when a comment is made in this repo. In addition to the REST calls to create the team and assign permissions, there are a checks done beforehand to ensure the users exist, and that the team name is not yet taken.


```text
Copyright:: 2019- IBM, Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
