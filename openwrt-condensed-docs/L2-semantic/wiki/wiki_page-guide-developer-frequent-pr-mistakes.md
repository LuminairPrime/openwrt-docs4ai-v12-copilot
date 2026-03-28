---
title: Frequent PR mistakes or "How to prevent my PR from getting delayed for sure"
module: wiki
origin_type: wiki_page
token_count: 951
source_file: L1-raw/wiki/wiki_page-guide-developer-frequent-pr-mistakes.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_url: https://openwrt.org/docs/guide-developer/frequent-pr-mistakes
language: text
ai_summary: This document outlines common mistakes that developers make when submitting Pull Requests (PRs) to OpenWrt, aiming to help them avoid delays in the review process. Key points include the necessity of a commit message, the importance of using a real name and email in the Signed-off-by line, and the distinction between a PR and its commits. Developers are also advised to respond to reviewer questions, avoid multi-posting PRs, and use the checkpatch.pl script for code quality checks.
ai_when_to_use: Refer to this guide when preparing a PR for OpenWrt to ensure a smooth review process and to avoid common pitfalls that can lead to delays.
ai_related_topics:
- Submitting patches
- Device Support Policies
- Reopen closed PR
- checkpatch.pl
---
# Frequent PR mistakes or "How to prevent my PR from getting delayed for sure"

A lot of PR initial reviews include the very same basic review comments each and every time again.

In order to not have to write the very same things more than a few hundred times, this page is meant to serve as a collection of very frequent "mistakes", or things that you should avoid in order to get a quick(er) review.

If you are pointed here and/or find yourself in the list below, you should probably read [Submitting patches](/submitting-patches) (again).

For device support, [Device Support Policies](/docs/guide-developer/device-support-policies) might help as well.

Those references up there are the real thing. In contrast, this page here is not exhaustive.

**So, in order to improve for your next try, or give a good first impression, please:**

## 1. Add a commit message

Commit message is mandatory. And if you think your particular PR maybe does not need a commit message, remember: Commit message is mandatory. Is. Mandatory.

## 2. Add a Signed-off-by with your real name

Use your real name. And a real e-mail address. Really.

    Signed-off-by: Firstname Lastname <myreal@emailadre.ss>

## 3. Do not multi-post or re-post PRs

If you have opened one PR, stick to it. If you have issues with Git, ask and try to get help.

If you accidentally closed the PR, reopen it as described here: [Reopen closed PR](/docs/guide-developer/working-with-github-pr#reopen_closed_pr)

Simply posting another, new PR will invalidate all the previous discussion - your work so far - and annoy the reviewers, because they will have to do extra work.

Just don't do it. Please.

## 4. Know the difference between the PR (Pull Request) and the commit

PR and commit are not same the same. *PR* is for preparation only, but the *commit(s) inside* the PR are the real thing. They will stay in the Git history. So, they are the important aspect.

So, while keeping the PR up-to-date is not a bad thing, remember: If you are asked to change the *commit*, change the commit; not the PR's initial post or title.

## 5. Answer questions

If I ask questions in OpenWrt GitHub PRs, in about 90 % of the cases I do not get an answer. I don't fully understand why this is the case, but probably people think my question only implies the necessity to change something. Since without answering the initial question there has been no discussion, these changes might help - or they make it worse.

So, please, if you are asked a question, just answer it. Maybe the answer is enough, and you don't have to change anything at all. Maybe there is a need to change - but now the reviewers will probably be able to help you with what has to be done, since they have been given information.

Thus, if you are asked "Have you tested this?", please answer. "Yes" or "no", and some explanation. If someone wanted you to change anything already, they would simply have said so.

## 6. Do not resolve comment that are not resolved

"Resolved" means the issue/question is dealt with completely and there is no doubt about the correct response.

If you are not sure - keep it open.

If there are multiple opinions, of which you chose one for your changes - keep it open.

If you have done nothing at all - keep it open.

If it might be helpful for review - keep it open.

Having all comments closed won't make the review process faster. Actually, if you have more than a few and they all are resolved it's quite suspicious. Ask yourself: If reviewers find that you closed something that is not resolved, will they trust you more - or less ...

## 7. Use checkpatch.pl

The OpenWrt core repository includes a script that is able to check most of the formal issues automatically. You just have run it. Please do.

<https://github.com/openwrt/openwrt/blob/master/scripts/checkpatch.pl>

## 8. Address all issues

Occasionally, people do 90 % of the requested changes and simply ignore the rest.

Don't do that. It will waste the reviewer's life-time (since they have to come back for another round) and will have you waiting longer for a chance to be merged (since they have to come back for another round).
