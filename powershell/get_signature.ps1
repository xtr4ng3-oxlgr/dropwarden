param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

# xtr4ng3: signature inspection only.
$result = @{
    ok = $true
    is_signed = $false
    status = $null
    signer = $null
    issuer = $null
    error = $null
}

try {
    $sig = Get-AuthenticodeSignature -LiteralPath $Path
    $result.status = [string]$sig.Status
    if ($sig.SignerCertificate) {
        $result.is_signed = $true
        $result.signer = $sig.SignerCertificate.Subject
        $result.issuer = $sig.SignerCertificate.Issuer
    }
} catch {
    $result.ok = $false
    $result.error = $_.Exception.Message
}

$result | ConvertTo-Json -Compress
