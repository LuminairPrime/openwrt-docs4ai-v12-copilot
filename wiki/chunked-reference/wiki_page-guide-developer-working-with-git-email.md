---
title: Sending patches by git send-email
module: wiki
origin_type: wiki_page
token_count: 174
source_file: L1-raw/wiki/wiki_page-guide-developer-working-with-git-email.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_url: https://openwrt.org/docs/guide-developer/working-with-git-email
language: text
ai_summary: The 'Sending patches by git send-email' module provides guidance on how to properly send patches to the OpenWrt development mailing list using the 'git send-email' command. It emphasizes the importance of adhering to the format specified on the patchwork site to ensure that patches are processed correctly. Additionally, it warns against using standard email clients due to potential formatting issues that could arise. The recommended command for sending a patch includes specifying the sender's email and the recipient mailing list.
ai_when_to_use: Use this module when you need to submit patches to the OpenWrt development mailing list to ensure they are correctly formatted and processed.
ai_related_topics:
- git send-email
- openwrt-devel
- patchwork
---

> **Source:** [https://openwrt.org/docs/guide-developer/working-with-git-email](https://openwrt.org/docs/guide-developer/working-with-git-email)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

# Sending patches by git send-email

Send an email to the [development mailing list](https://lists.openwrt.org/mailman/listinfo/openwrt-devel). All patches need to be sent in the same format as those that are listed on [patchwork](https://patchwork.ozlabs.org/project/openwrt/list/). If the patch does not get listed in patchwork then it won't get processed.

Using [git send-email](https://git-scm.com/docs/git-send-email) is warmly recommended, as email clients tend to add spaces and screw up the formatting or add non-printable characters.

    git send-email --from=youremail@example.com --to="openwrt-devel@lists.openwrt.org" 001-description.patch

[git send-email documentation](http://git-scm.com/docs/git-send-email)
