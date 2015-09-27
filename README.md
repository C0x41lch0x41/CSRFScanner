# CSRFScanner v1.0
Python CSRF vulnerability scanner

# Description
CSRFScanner is a tool to scan a website for CSRF vulnerabilities.
It is a basic tool, not very user friendly that I first develop for academic purpose.
More explications can be found in the PDF CSRFScanner_Explications.pdf (written in french). 

# Requirement
Python >= 2.6

# Usage 
python main.py [-R] URL Cookie
 - -R is an optional argument uses to follow internals links in order to scan a whole website.
 - URL is the webpage to scan
 - Cookie is the cookie to send to be authenticated. It can be seen with a tool like Wireshark, a web proxy like Burp or Webscarab, a web browser extension like TamperData ...
