# Camlio web client

Web client that connects to Bluejeans

## FAQs

1. How do I avoid CORS issue?

Bluejeans endpoints are very restrictive and they don't even enabled CORS access for localhost. As a workaround, disable web security on the browser.

```bash
open -n -a /Applications/Google\ Chrome\ Canary.app/Contents/MacOS/Google\ Chrome\ Canary --args --disable-web-security --user-data-dir="/tmp/chrome-test"
```
