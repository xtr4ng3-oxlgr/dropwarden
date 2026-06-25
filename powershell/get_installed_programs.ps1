# xtr4ng3: inventory only.
$paths = @(
 "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
 "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$programs = @()
foreach ($p in $paths) {
    try {
        Get-ItemProperty $p -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.DisplayName) {
                $programs += @{
                    name = $_.DisplayName
                    version = $_.DisplayVersion
                    publisher = $_.Publisher
                    install_date = $_.InstallDate
                    location = $_.InstallLocation
                }
            }
        }
    } catch {}
}

@{ ok = $true; programs = $programs } | ConvertTo-Json -Depth 4 -Compress
