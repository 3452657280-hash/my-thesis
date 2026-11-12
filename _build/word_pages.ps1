param([string]$Docx, [string]$OutDir, [string]$Pdf = "")
# 用本机 Word 打开 docx：可选导出 PDF；把每页的增强图元写成 page*.emf（再由 Python/Pillow 转 PNG）。
$full = (Resolve-Path $Docx).Path
New-Item -ItemType Directory -Force $OutDir | Out-Null
Get-ChildItem $OutDir -Include "page*.png", "page*.emf" -Recurse | Remove-Item
$outFull = (Resolve-Path $OutDir).Path
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $doc = $w.Documents.Open($full)
    $doc.ActiveWindow.View.Type = 3   # wdPrintView
    "pages=" + $doc.ComputeStatistics(2)
    if ($Pdf) { $doc.ExportAsFixedFormat([IO.Path]::GetFullPath($Pdf), 17) }
    $pane = $doc.ActiveWindow.ActivePane
    for ($i = 1; $i -le $pane.Pages.Count; $i++) {
        [byte[]]$bits = $pane.Pages.Item($i).EnhMetaFileBits
        [System.IO.File]::WriteAllBytes((Join-Path $outFull ("page{0:D2}.emf" -f $i)), $bits)
    }
    "rendered=" + $pane.Pages.Count
    $doc.Close($false)
} finally {
    $w.Quit()
}
