param([string]$Docx, [string]$Pdf)
# Export docx to PDF with local Word (ASCII-only file; pass ASCII paths).
$full = (Resolve-Path $Docx).Path
$pdfFull = [System.IO.Path]::GetFullPath($Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Open($full, $false, $true)
    $doc.ExportAsFixedFormat($pdfFull, 17)
    "pdf=" + $pdfFull
    $doc.Close($false)
} finally {
    $w.Quit()
}
