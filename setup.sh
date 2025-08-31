#!/bin/bash

# setup.sh - Configuration script for Streamlit deployment
# This file is used when deploying to platforms like Heroku

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
\n\
[theme]\n\
primaryColor = '#FF6B6B'\n\
backgroundColor = '#FFFFFF'\n\
secondaryBackgroundColor = '#F0F2F6'\n\
textColor = '#262730'\n\
font = 'sans serif'\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
\n\
[runner]\n\
magicEnabled = true\n\
installTracer = false\n\
fixMatplotlib = true\n\
" > ~/.streamlit/config.toml