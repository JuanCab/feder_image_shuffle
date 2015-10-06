from __future__ import print_function, absolute_import, unicode_literals

import os
from glob import glob
from time import sleep

from github3 import login


def main(night, path=None, sleep_time=0.1):
    """
    Create a github issue for a night that has been staged.

    Parameters
    ----------

    night : str
        Date of the observation, in the form YYYY-MM-DD

    path : str
        Full path the the directory containing the staged images.

    sleep_time : float
        Amount of time to sleep after the github class to avoid hitting API
        rate limits.
    """
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        raise RuntimeError('Set GITHUB_TOKEN to a github token before running.')

    gh = login(token=token)
    repo = gh.repository('feder-observatory', 'processed_images')

    # Check that whether there is already an issue for this night.
    issue_title = 'Examine staged data for {}'.format(night)
    for i in repo.issues():
        if i.title == issue_title:
            raise RuntimeError('Issue already exists: {}'.format(issue_title))

    # Add a skeleton README for this night
    with open('github_staging_readme_template.md', 'r') as f:
        template = f.read()

    readme = template.format(night=night)
    readme_path = 'nights/{}-README.md'.format(night)
    commit_message = 'Add skeleton README for {}'.format(night)
    repo.create_file(readme_path, commit_message, readme)

    readme_edit_url = '/'.join([repo.html_url, 'edit', 'master', readme_path])

    if path is not None:
        needs_stuff = glob(os.path.join(path, 'NEEDS*.txt'))
        # Do not write full path to github.
        needs_stuff = [os.path.basename(need) for need in needs_stuff]

    if needs_stuff:
        needs_text = ('\n\nThis directory seems to need '
                      'these things:\n+ {}').format('\n+ '.join(needs_stuff))
    else:
        needs_text = ''
    issue_text = ('Click [here]({}) to edit README '
                  'for this night'.format(readme_edit_url)) + needs_text

    repo.create_issue(issue_title, issue_text)

    # Take a brief nap to avoid getting blocked by GitHub...
    sleep(sleep_time)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('night', help='Night of observation as YYYY-MM-DD')
    parser.add_argument('-p', '--path',
                        help='Full path to directory containing observations',
                        nargs=1, default=None)
    args = parser.parse_args()
    path = args.path
    if path:
        path = path[0]

    main(args.night, path=path)
