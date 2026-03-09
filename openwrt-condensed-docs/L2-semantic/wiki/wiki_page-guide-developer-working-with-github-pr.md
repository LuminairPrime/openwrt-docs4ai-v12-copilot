---
title: Working with GitHub
module: wiki
origin_type: wiki_page
token_count: 1397
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-working-with-github-pr.md
last_pipeline_run: '2026-03-09T17:28:41.757217+00:00'
language: text
---
# Working with GitHub

There are GitHub mirrors of the source repository [here](https://github.com/openwrt/openwrt).

Fork the project to a public repo using GitHub web interface, clone the repo to your computer, create a branch for your changes, push these back to GitHub and submit a pull request.

In case you don't know how to do that, keep reading.

Create a GitHub account, this will host your public fork of OpenWrt source, and will be used for all interaction on GitHub.

Install git in your PC, and make sure that your local git settings have the right name and email:

``` bash
git config --global user.name "my name"
git config --global user.email "my@email.address"
```

You might also want to set the default text editor to your favorite editor. If you have a Linux system with a GUI, some choices are **geany**, **kwrite**, **pluma** and **gedit**. If you are using command line, **nano** is a good one.

``` bash
git config --global core.editor "editor-name-here"
```

Then follow GitHub's excellent documentation to [Fork A Repo](https://help.github.com/articles/fork-a-repo/) and [Create a local clone of your fork](https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork).

After you have set it up as described, write

``` bash
git checkout -b my-new-branch-name
```

to create a branch for your PR ("my-new-branch-name" is just an example name, use a more descriptive name in yours).

All commits you do after this command will be grouped in this branch. This allows to have multiple branches, one for each PR. To switch between branches you already created, use

``` bash
git checkout my-branch-name
```

After you made your changes, write

``` bash
git add -i
```

and use its interface to add untracked (new) files and update existing ones.

Then write

``` bash
git commit --signoff
```

This will open the git default editor and you can write the commit message.

The first line is the commit subject, then leave an empty line, then you write the commit description. This command will automatically add the Signed-off-by line with your name and email as set above. For example, a complete commit message might look like this:

``` bash
<area>: the best code update.

This is the best piece of code I have ever submitted.

Signed-off-by: John Doe <John.Doe@test.com>
```

To send your local changes over to your GitHub repo, write

``` bash
git push --all
```

You will be asked your GitHub user and password in the process.

After the code has been uploaded to your GitHub repo, you can submit pull request using GitHub web interface, see again GitHub's documentation about [Creating a pull request](https://help.github.com/articles/creating-a-pull-request/).

## Squashing commits

Commits in a PR or sent by email should be about full changes you want to merge, not about fixing all issues the reviewers found in your original PR.

So, there will come a time when you will need to either rewrite or squash your commits; so you end with a normal amount of true and sane commits.

Work with git commandline. Change to your development folder. Look at the branches you have with:

``` bash
git branch -a
```

get something like:

``` bash
  best_code_update
* master
```

Switch to the your development branch for this PR with:

``` bash
git checkout best_code_update
```

Look at the git log, so you can count the number of commits you want to squash ( the "X" below ) with:

``` bash
git log
```

Delete commits with:

``` bash
git reset HEAD~X
```

(where X is the number of commits you want to delete, counted from the last commit), this will not change modified files, it will only delete the commits.

Add the files to git tracking again with:

``` bash
git add -i
```

and commit again with:

``` bash
git commit --signoff
```

Send the updated branch over to GitHub with:

``` bash
git push -f
```

and the commits in the PR will be updated automatically.

### Alternative squashing advice

You can use **interactive rebase** to combine, reorder and edit your commits and their commit messages, with:

``` bash
git rebase -i HEAD~X
```

Where X is a number of commits to edit.

## Reopen closed PR

GitHub will grey out "Reopen" and will not let you reopen a PR if you force-pushed anything to the relevant branch after the PR has been closed, or deleted the branch.

However, reopening is still possible if you just set back the GitHub branch to the exact commit ID/hash it was at when you closed it. This even works when the branch or even the whole repository was deleted on GitHub. It just has to be recreated with the same name (for repo and branch) and the same commit hash at the branches HEAD.

A possible way to do that would be (there might be others, even shorter ones):

*We assume that the git remote referring to GitHub is called "origin", the branch of interest is called "testbranch", and the local and remote branch names are the same.*

``` bash
# Get the hash yyyyyyyyyyyyyyy of the current state of "testbranch" (we will move the branch head later)
git log -1 testbranch
# Checkout the latest state of the PR (commit hash xxxxxxxxxxx)
git checkout xxxxxxxxxx
# Delete old testbranch
git branch -D testbranch
# Label current state as testbranch
git checkout -b testbranch
# Push old state to GitHub
git push -f origin testbranch
```

Now you got GitHub at the state it was at when closing the PR. It should now be possible to "reopen" the PR. Note that this will only be possible if *you* closed it. If it was closed by an admin, you will have to ask an admin to reopen it (though they will also only be able to do that when the branch is at the proper hash). If the PR is reopened, you can update as usual, e.g.

``` bash
# Checkout the desired hash yyyyyyyyy (or branch)
git checkout yyyyyyyyy
# Delete intermediate testbranch
git branch -D testbranch
# Label current state as testbranch
git checkout -b testbranch
# Push new state to GitHub
git push -f origin testbranch
```