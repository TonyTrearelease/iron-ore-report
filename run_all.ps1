# ============================================================
# 一键运行：read_exchange -> import_cost_calculator -> generate_interactive -> GitHub
# ============================================================

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  第一步：运行 read_exchange.py （从Excel读取数据）" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

python -u read_exchange.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "read_exchange.py 执行失败，终止运行" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  第二步：运行 import_cost_calculator.py （计算进口成本与利润）" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

python -u import_cost_calculator.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "import_cost_calculator.py 执行失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  第三步：运行 generate_interactive.py （生成交互式计算器）" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

python -u generate_interactive.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "generate_interactive.py 执行失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  全部完成！" -ForegroundColor Green
Write-Host "  输出文件：" -ForegroundColor Green
Write-Host "    1. 进口成本估算结果_完整版.csv" -ForegroundColor Green
Write-Host "    2. 进口成本利润_{时间节点}.csv" -ForegroundColor Green
Write-Host "    3. 进口成本汇总_按品种.csv" -ForegroundColor Green
Write-Host "    4. 进口利润汇总_按品种.csv" -ForegroundColor Green
Write-Host "    5. 进口成本利润可视化报表.html" -ForegroundColor Green
Write-Host "    6. 进口成本交互计算器.html （双击打开，可调参）" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

# 第四步：推送至GitHub
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  第四步：推送至 GitHub Pages" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$gitPaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "${env:ProgramFiles(x86)}\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
)
$gitExe = $null
foreach ($p in $gitPaths) {
    if (Test-Path $p) { $gitExe = $p; break }
}

if (-not $gitExe) {
    Write-Host "  WARNING 未找到 Git，跳过推送步骤。" -ForegroundColor Yellow
    Write-Host "  请手动运行: git push origin main" -ForegroundColor Yellow
} else {
    $status = & $gitExe status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "  WARNING 没有文件变更，跳过推送。" -ForegroundColor Yellow
    } else {
        & $gitExe add -A
        & $gitExe commit -m "chore: 更新数据 ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
        Write-Host "  -> 正在推送到 GitHub ..." -ForegroundColor Yellow
        $pushResult = & $gitExe push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK 推送成功！" -ForegroundColor Green
            Write-Host "  -> 1-2分钟后访问：" -ForegroundColor Green
            Write-Host "    https://tonytrearelease.github.io/iron-ore-report/进口成本利润可视化报表.html" -ForegroundColor Green
            Write-Host "    https://tonytrearelease.github.io/iron-ore-report/进口成本交互计算器.html" -ForegroundColor Green
        } else {
            Write-Host "  WARNING 推送失败，详情：" -ForegroundColor Yellow
            $pushResult | Write-Host
            Write-Host "  请手动运行: git push origin main" -ForegroundColor Yellow
        }
    }
}
