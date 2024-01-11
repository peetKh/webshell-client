
# Webshell client #

This is a client to provide extended capabilities in a webshell or while exploiting a Remote Command Execution in a web application.

Features:
- Command completion based on history
- Upload file macro for Linux and Windows
- Download file macro for Linux and Windows
- Proxying request, for instance through Burp for keeping traces of performed actions


The typical use case for this is when during a penetration test you obtain a Remote Command Execution vulnerability, or can drop a webshell, on a web application, but the target server is behind a well configured firewall and no other flow that the HTTP(S) can go though (so no file transfer, no SHH/RDP, no reverse shell... nothing).

This script provides an environment to prepare HTTP requests and parse their result, provide command completion based on history, and some "macros" to upload and download files for Linux and Windows. These latter macros are based on a sequence of native shell commands (e.g. head/tail/base64 in bash) to upload/download a file chunk by chunk through several requests.

This script should rather be seen as a template, so that the `execCmd()` function can be customized for specific situations, for instance if the command has to be formatted in a specific way (e.g. XMLRPC).

## Demo ##
![vid-linux](https://github.com/peetKh/webshell-client/assets/64159410/22b2b8b0-5e92-4c30-8239-84300ad78108)

