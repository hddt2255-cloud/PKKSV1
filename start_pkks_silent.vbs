Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""C:\Users\Administrator\.gemini\antigravity\scratch\PKKS 2026"" && python server.py 8085", 0, False
