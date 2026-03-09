---
title: Sending patches by git send-email
module: wiki
origin_type: wiki_page
token_count: 174
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-working-with-git-email.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
language: text
---
# Sending patches by git send-email

Send an email to the [development mailing list](https://lists.openwrt.org/mailman/listinfo/openwrt-devel). All patches need to be sent in the same format as those that are listed on [patchwork](https://patchwork.ozlabs.org/project/openwrt/list/). If the patch does not get listed in patchwork then it won't get processed.

Using [git send-email](https://git-scm.com/docs/git-send-email) is warmly recommended, as email clients tend to add spaces and screw up the formatting or add non-printable characters.

    git send-email --from=youremail@example.com --to="openwrt-devel@lists.openwrt.org" 001-description.patch

[git send-email documentation](http://git-scm.com/docs/git-send-email)