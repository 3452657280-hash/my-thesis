param([string]$Docx, [string]$OutDir = "")
# Open docx in local Word: update all fields (TOC, page numbers) and save;
# optionally export every page as page*.emf for preview (convert with emf2png.py).
# Keep this file ASCII-only: Windows PowerShell 5 reads BOM-less UTF-8 as ANSI.
# Pass an ASCII path (build_thesis.py also saves _build/_thesis.docx).
$full = (Resolve-Path $Docx).Path
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Open($full)
    $doc.ActiveWindow.View.Type = 3
    foreach ($t in $doc.TablesOfContents) { $t.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($t in $doc.TablesOfContents) { $t.Update() }
    "pages=" + $doc.ComputeStatistics(2)
    $doc.Save()
    if ($OutDir) {
        New-Item -ItemType Directory -Force $OutDir | Out-Null
        Get-ChildItem $OutDir -Include "page*.png", "page*.emf" -Recurse | Remove-Item
        $outFull = (Resolve-Path $OutDir).Path
        $pane = $doc.ActiveWindow.ActivePane
        for ($i = 1; $i -le $pane.Pages.Count; $i++) {
            [byte[]]$bits = $pane.Pages.Item($i).EnhMetaFileBits
            [System.IO.File]::WriteAllBytes((Join-Path $outFull ("page{0:D2}.emf" -f $i)), $bits)
        }
        "rendered=" + $pane.Pages.Count
    }
    $doc.Saved = $true  # page export marks the doc dirty; without this Close() can pop a save dialog
    $doc.Close(0)
} finally {
    $w.Quit()
}
