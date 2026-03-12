---
title: Network Filesystems
module: wiki
origin_type: wiki_page
token_count: 330
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-filesystems-network.md
last_pipeline_run: '2026-03-12T18:07:24.356646+00:00'
language: text
ai_summary: The Network Filesystems module in OpenWrt allows the system to mount various filesystems over an IP network, functioning as both a client and a server. Supported filesystems include ftp, sshfs, sftp, nfs, cifs, iscsi, remotefs, tftp, and webdav, each with specific configurations and capabilities. This module facilitates file sharing and storage solutions across networked devices. Security features vary by filesystem, with some supporting tcp-wrappers and authentication mechanisms.
ai_when_to_use: Use this module when you need to access or share files over a network in OpenWrt, such as setting up a NAS or connecting to remote storage solutions.
ai_related_topics:
- ftp
- sshfs
- sftp
- nfs
- cifs
- iscsi
- remotefs
- tftp
- webdav
---
# Network Filesystems

OpenWrt can mount several filesystem that are attached to an IP Network. OpenWrt acts as a client.

OpenWrt can provide filesystems over network links; it acts as a server.

Files can be provided by other means: see [filesharing](/doc/howto/filesharing)

## Supported Network Filesystems

- ftp (via curlftpfs) [ftp.overview](/docs/guide-user/services/nas/ftp.overview)
- sshfs [sshfs.client](/docs/guide-user/services/ssh/sshfs.client) ,
- sftp [sshfs.server](/docs/guide-user/services/ssh/sshfs.server) , [sftp.server](/docs/guide-user/services/nas/sftp.server)
- nfs [nfs.client](/docs/guide-user/services/nas/nfs.client) , [nfs.server](/docs/guide-user/services/nas/nfs.server)
- cifs [cifs.server](/docs/guide-user/services/nas/cifs.server) , [samba](/docs/guide-user/services/nas/samba)
- iscsi : tgt package
- remotefs
- tftp [tftp.overview](/doc/howto/tftp.overview)
- webdav via davfs2

## Embedded FS

:FIXME:

- owfs ?
- gadgetfs ?

## Security

:FIXME:

The Filesystems mentioned, support varying security. Accessible via TCP often means support for tcp-wrappers (libwrap). Blacklists/Whitelists are sometimes possible. Authentication via ldap ....
