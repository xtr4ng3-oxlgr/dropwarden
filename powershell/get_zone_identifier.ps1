param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

# xtr4ng3: read metadata only, do not modify the file.
$result = @{
    ok = $true
    zone_id = $null
    host_url = $null
    referrer_url = $null
    error = $null
}

try {
    $ads = Get-Content -LiteralPath "$Path`:Zone.Identifier" -ErrorAction Stop
    foreach ($line in $ads) {
        if ($line -match "^ZoneId=(.*)$") { $result.zone_id = $Matches[1] }
        if ($line -match "^HostUrl=(.*)$") { $result.host_url = $Matches[1] }
        if ($line -match "^ReferrerUrl=(.*)$") { $result.referrer_url = $Matches[1] }
    }
} catch {
    $result.ok = $false
    $result.error = $_.Exception.Message
}

$result | ConvertTo-Json -Compress
