# GitHub 推送脚本
param(
    [string]$Message = "Update: 项目更新",
    [string]$NewRepo = ""
)

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "GitHub Push Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 检查是否有新的仓库地址
if ($NewRepo -ne "") {
    Write-Host "切换到新仓库: $NewRepo" -ForegroundColor Yellow
    git remote remove origin
    git remote add origin $NewRepo
    Write-Host "远程仓库已更新" -ForegroundColor Green
    Write-Host ""
}

# 显示当前状态
Write-Host "当前 Git 状态:" -ForegroundColor Yellow
git status --short
Write-Host ""

# 添加所有更改
Write-Host "添加所有更改..." -ForegroundColor Yellow
git add .

# 显示将要提交的文件
Write-Host ""
Write-Host "将要提交的文件:" -ForegroundColor Yellow
git status --short
Write-Host ""

# 提交更改
Write-Host "提交更改..." -ForegroundColor Yellow
git commit -m $Message

# 推送到 GitHub
Write-Host ""
Write-Host "推送到 GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "推送完成!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
