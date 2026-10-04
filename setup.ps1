# Bootstrap-only exception: lifecycle operations remain in stdlib Python.
$ErrorActionPreference = 'Stop'
$BootstrapArguments = @($args)
$GenieDataRoot = if ($env:GENIE_BOOTSTRAP_HOME) { $env:GENIE_BOOTSTRAP_HOME } else { Join-Path $env:USERPROFILE '.genie' }
for ($index = 0; $index -lt $BootstrapArguments.Count - 1; $index++) {
    if ($BootstrapArguments[$index] -eq '--home') { $GenieDataRoot = $BootstrapArguments[$index + 1] }
}
foreach ($candidate in @('python', 'python3')) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) {
        & $command.Source -c 'import sys; raise SystemExit(sys.version_info < (3,11))' 2>$null
        if ($LASTEXITCODE -eq 0) {
            & $command.Source (Join-Path $PSScriptRoot 'bootstrap.py') @BootstrapArguments
            exit $LASTEXITCODE
        }
    }
}
if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') {
    throw 'Managed runtime currently supports native Windows x64. No WSL/remote fallback is used.'
}
$registry = Get-Content (Join-Path $PSScriptRoot 'bootstrap-registry.json') -Raw | ConvertFrom-Json
$runtime = $registry.platforms.'windows-x64'.python
$runtimeRoot = Join-Path $GenieDataRoot ('bootstrap\runtime\' + $runtime.version)
$python = Join-Path $runtimeRoot $runtime.executable
if (-not ((Test-Path $python) -and (Test-Path (Join-Path $runtimeRoot '.verified')))) {
    $temporary = Join-Path $GenieDataRoot ('bootstrap\runtime\.stage-' + [guid]::NewGuid().ToString('N'))
    New-Item $temporary -ItemType Directory -Force | Out-Null
    try {
        $archive = Join-Path $temporary 'runtime.tar.gz'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest $runtime.url -OutFile $archive -UseBasicParsing
        $actual = (Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $runtime.sha256) { throw 'Managed Python checksum mismatch; nothing activated.' }
        $stage = Join-Path $temporary 'stage'
        New-Item $stage -ItemType Directory | Out-Null
        & tar.exe -xzf $archive -C $stage
        if ($LASTEXITCODE -ne 0) { throw 'Native tar extraction failed.' }
        & (Join-Path $stage $runtime.executable) -c 'import sys; raise SystemExit(sys.version_info < (3,11))'
        if ($LASTEXITCODE -ne 0) { throw 'Managed Python failed its compatibility probe.' }
        Set-Content (Join-Path $stage '.verified') $runtime.sha256
        if (Test-Path $runtimeRoot) { throw 'Existing managed runtime is incomplete; preserve it and repair before retry.' }
        Move-Item $stage $runtimeRoot
    } finally {
        Remove-Item $temporary -Recurse -Force -ErrorAction SilentlyContinue
    }
}
& $python (Join-Path $PSScriptRoot 'bootstrap.py') @BootstrapArguments
exit $LASTEXITCODE
