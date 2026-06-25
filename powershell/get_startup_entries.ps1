# xtr4ng3: startup inventory only.
$items = @()

$regPaths = @(
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
 "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
 "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
)

foreach ($rp in $regPaths) {
    try {
        $props = Get-ItemProperty -Path $rp -ErrorAction SilentlyContinue
        if ($props) {
            $props.PSObject.Properties | Where-Object { $_.Name -notmatch "^PS" } | ForEach-Object {
                $items += @{
                    source = $rp
                    name = $_.Name
                    command = [string]$_.Value
                }
            }
        }
    } catch {}
}

try {
    $startupFolders = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    foreach ($sf in $startupFolders) {
        if (Test-Path $sf) {
            Get-ChildItem $sf -ErrorAction SilentlyContinue | ForEach-Object {
                $items += @{
                    source = $sf
                    name = $_.Name
                    command = $_.FullName
                }
            }
        }
    }
} catch {}

@{ ok = $true; startup = $items } | ConvertTo-Json -Depth 4 -Compress
