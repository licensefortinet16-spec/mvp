#!/bin/bash
git config user.email "bot@example.com"
git config user.name "AI Assistant"
git commit -m "feat: initial commit for MVP WhatsApp Business API"
git branch -M main
git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/licensefortinet16-spec/mvp.git
git push -u origin main
