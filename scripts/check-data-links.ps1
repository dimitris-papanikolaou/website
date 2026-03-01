# Check external data links used by the website. Reports broken (non-2xx or timeout).
$urls = @(
    @{ name = "Missing Novelty - Data (.dta)"; url = "https://www.dropbox.com/scl/fi/nebzxddi77hdda2shnm6z/drug_icd9_noveltyscores_KLP21.dta?rlkey=za4qdza0mv2s9ucd5f3gpnb1l&raw=1" },
    @{ name = "Missing Novelty - Readme (PDF)"; url = "https://www.dropbox.com/scl/fi/my5vuyywi4jwaizt9bj9s/Data_Overview_KLP_novelty.pdf?rlkey=w2t890ejljtvf9ihthks0y71m&raw=1" },
    @{ name = "Pairwise Citation Data (publications.yml)"; url = "https://www.dropbox.com/scl/fi/1m96czhofv825jc4mnqgs/full_citations_combined_v2019-0305.zip?rlkey=bu0h7ro56je2y0vsfytq9dnbf&raw=1" },
    @{ name = "Pairwise Citation Data (data.qmd)"; url = "https://www.dropbox.com/s/1lh1fxkgrwlvn6b/full_citations_combined_v2019-0305.zip?raw=1" },
    @{ name = "Left Behind - ReplicationCodeExport.zip"; url = "https://www.dropbox.com/s/05onvj5fa9av814/ReplicationCodeExport.zip?raw=1" },
    @{ name = "Organization Capital - Replication zip"; url = "https://www.dropbox.com/s/ffqfdt8vf9uwsk5/org%20cap%20replication%20and%20data%20update.zip?raw=1" },
    @{ name = "JPEFiles.zip (Investment Shocks)"; url = "https://www.dropbox.com/scl/fi/u50pe7fead167etrrp1d2/JPEFiles.zip?rlkey=tpiis6xj6x9bscvurvuffuptg&raw=1" },
    @{ name = "OpenICPSR 119043"; url = "https://www.openicpsr.org/openicpsr/project/119043/version/V1/view" },
    @{ name = "Intangible Value - GitHub"; url = "https://github.com/papadimi/edwardtkim/intangiblevalue" },
    @{ name = "The Covid Factor"; url = "https://www.thecovidfactor.org/" },
    @{ name = "KPSS Extended Data (GitHub)"; url = "https://github.com/KPSS2017/Technological-Innovation-Resource-Allocation-and-Growth-Extended-Data" },
    @{ name = "Intangible Value data (data.qmd GitHub)"; url = "https://github.com/edwardtkim/intangiblevalue" }
)

$broken = @()
foreach ($u in $urls) {
    try {
        $r = Invoke-WebRequest -Uri $u.url -Method Head -MaximumRedirection 5 -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -lt 200 -or $r.StatusCode -ge 300) {
            $broken += [pscustomobject]@{ Name = $u.name; Url = $u.url; Status = $r.StatusCode }
        }
    } catch {
        $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "Error" }
        $broken += [pscustomobject]@{ Name = $u.name; Url = $u.url; Status = $status; Message = $_.Exception.Message }
    }
}

if ($broken.Count -eq 0) {
    Write-Host "All data links returned 2xx." -ForegroundColor Green
} else {
    Write-Host "Broken or failed links:" -ForegroundColor Red
    $broken | Format-Table -AutoSize
}
