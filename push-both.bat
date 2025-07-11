@echo off
echo 🟢 正在将代码推送到 GitHub...
git push origin main

echo 🟢 正在将代码推送到 GitLab...
git push gitlab main

echo ✅ 推送完成！
pause
