---
title: Links to Libraries
module: wiki
origin_type: wiki_page
token_count: 690
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-links-software-libraries.md
last_pipeline_run: '2026-03-12T09:09:53.122488+00:00'
language: text
ai_summary: The 'Links to Libraries' module provides a curated list of lightweight libraries suitable for linking in OpenWrt development. It includes various C standard libraries like uClibc, which is currently used by OpenWrt, and alternatives such as dietlibc and Newlib. Additionally, it offers links to SSL/TLS libraries, including OpenSSL and PolarSSL, along with their licensing information. This resource is essential for developers looking to integrate specific libraries into their OpenWrt projects.
ai_when_to_use: Use this module when selecting libraries for embedded development in OpenWrt, particularly when considering lightweight options for C and SSL/TLS functionalities.
ai_related_topics:
- GNU C Library
- Embedded GLIBC
- uClibc
- dietlibc
- Newlib
- libopenssl
- libpolarssl
- libmatrixssl
- libgnutls
- libgcrypt
---
# Links to Libraries

Here we could place links to light-build libraries you could link against:

## C standard library

- [GNU C Library](https://en.wikipedia.org/wiki/GNU C Library) (LGPL) "working horse", up-to-date, heavily worked on, most commonly used on non-embedded Linux distributions
  - License LGPL:
- [Embedded GLIBC](https://en.wikipedia.org/wiki/Embedded GLIBC) (LGPL) is an abstraction of the glibc, and more configurable and embedded friendly
  - License LGPL:
- [uClibc](https://en.wikipedia.org/wiki/uClibc) (LGPL) At the moment OpenWrt uses µClibc as C standard library. <http://www.uclibc.org/>
  - License LGPL:
- [dietlibc](https://en.wikipedia.org/wiki/dietlibc) (GPLv2) <http://www.fefe.de/dietlibc/> and some [FAQ](http://www.fefe.de/dietlibc/FAQ.txt).
  - License GPLv2:
- [Newlib](https://en.wikipedia.org/wiki/Newlib) (LGPL)
  - License LGPL:

## C++ standard library

## SSL/TLS

[Comparison_of_TLS_Implementations](https://en.wikipedia.org/wiki/Comparison_of_TLS_Implementations)

- `libopenssl` [OpenSSL](https://en.wikipedia.org/wiki/OpenSSL)
  - [Dual license: 4-clause BSD-like and Apache License 1.0](http://www.openssl.org/source/license.html)
    - `umurmur`
- `libpolarssl` [PolarSSL](https://en.wikipedia.org/wiki/PolarSSL)
  - [GPLv2 with FOSS exception or Commercial Licensing](http://polarssl.org/licensing)
    - `umurmur`
- `libmatrixssl` [MatrixSSL](https://en.wikipedia.org/wiki/MatrixSSL)

      *[[http://www.matrixssl.org/]] GPLv2+
        * ''[[docs:guide-user:services:webserver:http.mini-httpd]]''
    * ''libcyassl'' [[wp>CyaSSL]] [[http://www.yassl.com/yaSSL/Home.html]]
      * [[http://www.yassl.com/yaSSL/License.html|GPLv2 with FOSS exception or Commercial Licensing]]
        * ''[[doc:howto:luci|uhttpd-mod-tls]]''
    * ''libgnutls'' [[wp>GnuTLS]] [[http://www.gnu.org/software/gnutls/]]
      * [[http://www.gnu.org/software/gnutls/gnutls.html|LGPLv2.1+]]
    * [[wp>cryptlib]] [[http://www.cs.auckland.ac.nz/~pgut001/cryptlib/]]
      * [[http://www.cs.auckland.ac.nz/~pgut001/cryptlib/download.html|dua license: GPL-like or Commercial Licensing]]
    * ''libgcrypt'' [[wp>Libgcrypt]] [[http://directory.fsf.org/project/libgcrypt/]] LGPL or GPLv3
    * [[http://directory.fsf.org/project/BeeCrypt/|BeeCrypt]] LGPLv2.1+
    * ''libmcrypt'' [[http://mcrypt.sourceforge.net/]]
