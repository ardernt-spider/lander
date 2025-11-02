$exe = 'C:\Users\artem\dev\lander\dist\LunarLander.exe'
$icon = [System.Drawing.Icon]::ExtractAssociatedIcon($exe)
if ($icon -eq $null) { Write-Error "No icon extracted"; exit 1 }
$bmp = $icon.ToBitmap()
$path = 'C:\Users\artem\dev\lander\icon_preview.png'
$bmp.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "Saved $path"