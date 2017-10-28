
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['github-gist']
    assert extender.can_handle('github-gist:abc123') == True
    assert extender.can_handle('github-gist:foobar/abc123') == True

    assert extender.can_handle('github:abc123') == False
    assert extender.can_handle('github:foobar/abc123') == False


RESP_BASIC = {
  "url": "https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc",
  "forks_url": "https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc/forks",
  "commits_url": "https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc/commits",
  "id": "5baf85cea2045be585a065650e3ce6dc",
  "git_pull_url": "https://gist.github.com/5baf85cea2045be585a065650e3ce6dc.git",
  "git_push_url": "https://gist.github.com/5baf85cea2045be585a065650e3ce6dc.git",
  "html_url": "https://gist.github.com/5baf85cea2045be585a065650e3ce6dc",
  "files": {
    "tidypy": {
      "filename": "tidypy",
      "type": "text/plain",
      "language": None,
      "raw_url": "https://gist.githubusercontent.com/jayclassless/5baf85cea2045be585a065650e3ce6dc/raw/4a52387ce879edac450beee594404698dea6b282/tidypy",
      "size": 53,
      "truncated": False,
      "content": "[tidypy]\ntest = 'extended'\nextension = 'github gist'\n"
    }
  },
  "public": False,
  "created_at": "2017-10-22T23:39:13Z",
  "updated_at": "2017-10-22T23:39:13Z",
  "description": "TidyPy Extender Test #1",
  "comments": 0,
  "user": None,
  "comments_url": "https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc/comments",
  "owner": {
    "login": "jayclassless",
    "id": 694254,
    "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/jayclassless",
    "html_url": "https://github.com/jayclassless",
    "followers_url": "https://api.github.com/users/jayclassless/followers",
    "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
    "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
    "organizations_url": "https://api.github.com/users/jayclassless/orgs",
    "repos_url": "https://api.github.com/users/jayclassless/repos",
    "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
    "received_events_url": "https://api.github.com/users/jayclassless/received_events",
    "type": "User",
    "site_admin": False
  },
  "forks": [

  ],
  "history": [
    {
      "user": {
        "login": "jayclassless",
        "id": 694254,
        "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/jayclassless",
        "html_url": "https://github.com/jayclassless",
        "followers_url": "https://api.github.com/users/jayclassless/followers",
        "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
        "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
        "organizations_url": "https://api.github.com/users/jayclassless/orgs",
        "repos_url": "https://api.github.com/users/jayclassless/repos",
        "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
        "received_events_url": "https://api.github.com/users/jayclassless/received_events",
        "type": "User",
        "site_admin": False
      },
      "version": "cf67f406eb33b240b5b3ff09dd6f4c11e658418c",
      "committed_at": "2017-10-22T23:39:12Z",
      "change_status": {
        "total": 3,
        "additions": 3,
        "deletions": 0
      },
      "url": "https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc/cf67f406eb33b240b5b3ff09dd6f4c11e658418c"
    }
  ],
  "truncated": False
}

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/gists/5baf85cea2045be585a065650e3ce6dc', json=RESP_BASIC)
        extender = get_extenders()['github-gist']
        cfg = extender.retrieve('github-gist:5baf85cea2045be585a065650e3ce6dc', 'test')

        assert cfg == {
            'extension': 'github gist',
            'test': 'extended',
        }


RESP_PYPROJECT = {
  "url": "https://api.github.com/gists/b23ead805c233488b659229a24c75268",
  "forks_url": "https://api.github.com/gists/b23ead805c233488b659229a24c75268/forks",
  "commits_url": "https://api.github.com/gists/b23ead805c233488b659229a24c75268/commits",
  "id": "b23ead805c233488b659229a24c75268",
  "git_pull_url": "https://gist.github.com/b23ead805c233488b659229a24c75268.git",
  "git_push_url": "https://gist.github.com/b23ead805c233488b659229a24c75268.git",
  "html_url": "https://gist.github.com/b23ead805c233488b659229a24c75268",
  "files": {
    "pyproject.toml": {
      "filename": "pyproject.toml",
      "type": "text/plain",
      "language": "TOML",
      "raw_url": "https://gist.githubusercontent.com/jayclassless/b23ead805c233488b659229a24c75268/raw/57b0a97d4cc3bded7eabc8381f2628d4b86b8cb1/pyproject.toml",
      "size": 67,
      "truncated": False,
      "content": "[tool.tidypy]\ntest = 'extended'\nextension = 'github gist pyproject'"
    }
  },
  "public": False,
  "created_at": "2017-10-23T00:11:17Z",
  "updated_at": "2017-10-23T00:11:17Z",
  "description": "TidyPy Extender Test #2",
  "comments": 0,
  "user": None,
  "comments_url": "https://api.github.com/gists/b23ead805c233488b659229a24c75268/comments",
  "owner": {
    "login": "jayclassless",
    "id": 694254,
    "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/jayclassless",
    "html_url": "https://github.com/jayclassless",
    "followers_url": "https://api.github.com/users/jayclassless/followers",
    "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
    "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
    "organizations_url": "https://api.github.com/users/jayclassless/orgs",
    "repos_url": "https://api.github.com/users/jayclassless/repos",
    "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
    "received_events_url": "https://api.github.com/users/jayclassless/received_events",
    "type": "User",
    "site_admin": False
  },
  "forks": [

  ],
  "history": [
    {
      "user": {
        "login": "jayclassless",
        "id": 694254,
        "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/jayclassless",
        "html_url": "https://github.com/jayclassless",
        "followers_url": "https://api.github.com/users/jayclassless/followers",
        "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
        "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
        "organizations_url": "https://api.github.com/users/jayclassless/orgs",
        "repos_url": "https://api.github.com/users/jayclassless/repos",
        "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
        "received_events_url": "https://api.github.com/users/jayclassless/received_events",
        "type": "User",
        "site_admin": False
      },
      "version": "9e6e932955aa0c939dbce92420500bc5545e0aa8",
      "committed_at": "2017-10-23T00:11:16Z",
      "change_status": {
        "total": 3,
        "additions": 3,
        "deletions": 0
      },
      "url": "https://api.github.com/gists/b23ead805c233488b659229a24c75268/9e6e932955aa0c939dbce92420500bc5545e0aa8"
    }
  ],
  "truncated": False
}

def test_retrieve_pyproject():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/gists/b23ead805c233488b659229a24c75268', json=RESP_PYPROJECT)
        extender = get_extenders()['github-gist']
        cfg = extender.retrieve('github-gist:jayclassless/b23ead805c233488b659229a24c75268', 'test')

        assert cfg == {
            'extension': 'github gist pyproject',
            'test': 'extended',
        }


RESP_NO_GOOD = {
  "url": "https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4",
  "forks_url": "https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4/forks",
  "commits_url": "https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4/commits",
  "id": "f14576eea03b9d3c71018114facec0d4",
  "git_pull_url": "https://gist.github.com/f14576eea03b9d3c71018114facec0d4.git",
  "git_push_url": "https://gist.github.com/f14576eea03b9d3c71018114facec0d4.git",
  "html_url": "https://gist.github.com/f14576eea03b9d3c71018114facec0d4",
  "files": {
    "something.conf": {
      "filename": "something.conf",
      "type": "text/plain",
      "language": None,
      "raw_url": "https://gist.githubusercontent.com/jayclassless/f14576eea03b9d3c71018114facec0d4/raw/1c59fede9543117f283a52fdd9f3ff9bb0b6f25e/something.conf",
      "size": 60,
      "truncated": False,
      "content": "[tidypy]\ntest = 'extended'\nextension = 'github gist badname'"
    }
  },
  "public": False,
  "created_at": "2017-10-23T00:16:34Z",
  "updated_at": "2017-10-23T00:16:35Z",
  "description": "TidyPy Extender Test #3",
  "comments": 0,
  "user": None,
  "comments_url": "https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4/comments",
  "owner": {
    "login": "jayclassless",
    "id": 694254,
    "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/jayclassless",
    "html_url": "https://github.com/jayclassless",
    "followers_url": "https://api.github.com/users/jayclassless/followers",
    "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
    "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
    "organizations_url": "https://api.github.com/users/jayclassless/orgs",
    "repos_url": "https://api.github.com/users/jayclassless/repos",
    "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
    "received_events_url": "https://api.github.com/users/jayclassless/received_events",
    "type": "User",
    "site_admin": False
  },
  "forks": [

  ],
  "history": [
    {
      "user": {
        "login": "jayclassless",
        "id": 694254,
        "avatar_url": "https://avatars3.githubusercontent.com/u/694254?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/jayclassless",
        "html_url": "https://github.com/jayclassless",
        "followers_url": "https://api.github.com/users/jayclassless/followers",
        "following_url": "https://api.github.com/users/jayclassless/following{/other_user}",
        "gists_url": "https://api.github.com/users/jayclassless/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/jayclassless/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/jayclassless/subscriptions",
        "organizations_url": "https://api.github.com/users/jayclassless/orgs",
        "repos_url": "https://api.github.com/users/jayclassless/repos",
        "events_url": "https://api.github.com/users/jayclassless/events{/privacy}",
        "received_events_url": "https://api.github.com/users/jayclassless/received_events",
        "type": "User",
        "site_admin": False
      },
      "version": "e59c5667d224082c7505b2df5ee63e9fd49a0f17",
      "committed_at": "2017-10-23T00:16:34Z",
      "change_status": {
        "total": 3,
        "additions": 3,
        "deletions": 0
      },
      "url": "https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4/e59c5667d224082c7505b2df5ee63e9fd49a0f17"
    }
  ],
  "truncated": False
}

def test_retrieve_no_good_files():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/gists/f14576eea03b9d3c71018114facec0d4', json=RESP_NO_GOOD)
        extender = get_extenders()['github-gist']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('github-gist:jayclassless/f14576eea03b9d3c71018114facec0d4', 'test')


RESP_MISSING = {
  "message": "Not Found",
  "documentation_url": "https://developer.github.com/v3/gists/#get-a-single-gist"
}

def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/gists/doesntexist', json=RESP_MISSING, status_code=404)
        extender = get_extenders()['github-gist']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('github-gist:jayclassless/doesntexist', 'test')

