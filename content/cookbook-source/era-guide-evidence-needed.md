# Era Guide Evidence Needed

This file tracks claims in `openwrt-era-guide.md` that require human-verified external sources before the page can be considered fully verified.

## Pending Claims

| Claim | Required evidence | Status |
|-------|-------------------|--------|
| Legacy era ends ~12.09 | Forum post, release notes, or commit showing procd introduction date | Pending |
| Transitional era boundary 12.09–17.01 | Upstream release history or procd stabilization commit | Pending |
| Current era stable by 21.02 | OpenWrt 21.02 release announcement or changelog | Pending |

## Instructions for Human Reviewer

For each pending claim:
1. Search OpenWrt forums (https://forum.openwrt.org), GitHub (https://github.com/openwrt/), and official release notes
2. Record the exact URL, commit SHA, or forum thread ID
3. Update `openwrt-era-guide.md` Era Reference Table with the verified date range
4. Remove the row from this table once evidence is recorded in the era guide
5. Update `last_reviewed` in the era guide frontmatter
