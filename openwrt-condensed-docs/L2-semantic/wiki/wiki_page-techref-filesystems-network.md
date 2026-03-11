---
title: Network Filesystems
module: wiki
origin_type: wiki_page
token_count: 330
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-filesystems-network.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
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
