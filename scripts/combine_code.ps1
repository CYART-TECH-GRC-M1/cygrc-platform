# CyGRC Platform - PowerShell Codebase Combiner
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$OutputFile = Join-Path $RootDir "combined_codebase.txt"

Write-Host "Scanning project files in: $RootDir" -ForegroundColor Cyan

$ExcludeDirs = @(
    "node_modules",
    ".next",
    ".git",
    ".github",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".turbo",
    ".kilo",
    "dist",
    "build",
    "coverage",
    ".idea",
    ".vscode",
    "frontend"
)

$ExcludeExts = @(
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp", ".tiff",
    ".mp4", ".mp3", ".wav", ".mov", ".avi",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".exe", ".dll", ".bin", ".zip", ".tar", ".gz", ".7z",
    ".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".pyd"
)

$ExcludeFiles = @(
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "cygrc.db",
    "combined_codebase.txt",
    "combined_code.txt",
    "all_code.txt",
    "combine_code.bat",
    "export_codebase.bat"
)

# Collect files efficiently
$AllFiles = [System.Collections.Generic.List[PSObject]]::new()

function Scan-Dir ($dir) {
    $items = Get-ChildItem -LiteralPath $dir -Force
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            if (-not ($ExcludeDirs -contains $item.Name) -and -not ($item.Name.StartsWith("."))) {
                Scan-Dir $item.FullName
            }
        } else {
            $ext = $item.Extension.ToLower()
            if ($ExcludeExts -contains $ext -or $ExcludeFiles -contains $item.Name -or $item.Name.EndsWith(".log")) {
                continue
            }
            $rel = $item.FullName.Substring($RootDir.Length + 1).Replace("\", "/")
            $AllFiles.Add([PSCustomObject]@{
                RelPath = $rel
                FullPath = $item.FullName
            })
        }
    }
}

Scan-Dir $RootDir

$SortedFiles = $AllFiles | Sort-Object RelPath
Write-Host "Found $($SortedFiles.Count) source code files." -ForegroundColor Green

# Prepare buffer
$sb = [System.Text.StringBuilder]::new()
$totalLines = 0
$fileData = [System.Collections.Generic.List[PSObject]]::new()

foreach ($f in $SortedFiles) {
    try {
        $content = [System.IO.File]::ReadAllText($f.FullPath, [System.Text.Encoding]::UTF8)
        $lines = ($content -split "\r?\n").Length
        $totalLines += $lines
        $fileData.Add([PSCustomObject]@{
            RelPath = $f.RelPath
            Content = $content
            Lines = $lines
        })
    } catch {
        Write-Warning "Skipping $($f.RelPath): $_"
    }
}

$rule = "=" * 80
$dash = "-" * 80
$now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$totalLinesFormatted = $totalLines.ToString("N0")

[void]$sb.AppendLine($rule)
[void]$sb.AppendLine("CYGRC PLATFORM - COMBINED CODEBASE EXPORT")
[void]$sb.AppendLine("Generated: $now")
[void]$sb.AppendLine("Total Files: $($fileData.Count)")
[void]$sb.AppendLine("Total Lines of Code: $totalLinesFormatted")
[void]$sb.AppendLine($rule)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("TABLE OF CONTENTS")
[void]$sb.AppendLine($dash)

$idx = 1
foreach ($f in $fileData) {
    $entry = "{0,3}. [{1}] ({2} lines)" -f $idx, $f.RelPath, $f.Lines
    [void]$sb.AppendLine($entry)
    $idx++
}

[void]$sb.AppendLine($dash)
[void]$sb.AppendLine("")

$idx = 1
foreach ($f in $fileData) {
    [void]$sb.AppendLine($rule)
    [void]$sb.AppendLine("[$idx/$($fileData.Count)] FILE: $($f.RelPath)")
    [void]$sb.AppendLine("LINES: $($f.Lines)")
    [void]$sb.AppendLine($rule)
    [void]$sb.AppendLine($f.Content)
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("")
    $idx++
}

[System.IO.File]::WriteAllText($OutputFile, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "Done! Saved to: $OutputFile ($totalLinesFormatted lines)" -ForegroundColor Green
