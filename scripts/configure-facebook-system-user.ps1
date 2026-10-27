param([switch]$Check)

$ErrorActionPreference = 'Stop'
$pageId = [Environment]::GetEnvironmentVariable('REUP_FACEBOOK_PAGE_ID', 'User')
if (-not $pageId) { $pageId = (Read-Host 'Facebook Page ID').Trim() }
$version = [Environment]::GetEnvironmentVariable('REUP_META_GRAPH_VERSION', 'User')
if (-not $version) { $version = (Read-Host 'Graph API version (dạng vN.N)').Trim() }
if ($pageId -notmatch '^\d+$' -or $version -notmatch '^v\d+\.\d+$') {
    throw 'Page ID hoặc phiên bản Graph API không hợp lệ.'
}

if ($Check) {
    if ([Environment]::GetEnvironmentVariable('REUP_FACEBOOK_AUTH_MODE', 'User') -ne 'system_user') {
        throw 'Máy này chưa chọn chế độ System User.'
    }
    $systemToken = [Environment]::GetEnvironmentVariable('REUP_FACEBOOK_SYSTEM_USER_TOKEN', 'User')
} else {
    $secureToken = Read-Host 'System User access token (đầu vào được ẩn)' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try { $systemToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
}
if ([string]::IsNullOrWhiteSpace($systemToken)) { throw 'Chưa có System User token.' }

$cursor = ''
$selectedPage = $null
for ($index = 0; $index -lt 10; $index++) {
    $uri = "https://graph.facebook.com/$version/me/accounts?fields=id,name,access_token,tasks&limit=100"
    if ($cursor) { $uri += '&after=' + [uri]::EscapeDataString($cursor) }
    try {
        $response = Invoke-RestMethod -Method Get -Uri $uri -Headers @{ Authorization = "Bearer $systemToken" } -TimeoutSec 20
    } catch {
        throw 'Meta từ chối System User token hoặc không liệt kê Page. Kiểm tra App, quyền và Page đã gán trong Business Settings.'
    }
    foreach ($page in @($response.data)) {
        if ([string]$page.id -eq $pageId) { $selectedPage = $page; break }
    }
    if ($selectedPage) { break }
    $nextCursor = [string]$response.paging.cursors.after
    if (-not $nextCursor -or $nextCursor -eq $cursor) { break }
    $cursor = $nextCursor
}
if (-not $selectedPage -or [string]::IsNullOrWhiteSpace([string]$selectedPage.access_token)) {
    throw 'System User chưa có Page token cho Page ID đã chọn. Gán Page và quyền tạo nội dung cho System User rồi thử lại.'
}

$pageToken = [string]$selectedPage.access_token
$uri = "https://graph.facebook.com/$version/${pageId}?fields=id,name"
try {
    $verifiedPage = Invoke-RestMethod -Method Get -Uri $uri -Headers @{ Authorization = "Bearer $pageToken" } -TimeoutSec 20
} catch {
    throw 'Page token lấy từ System User không đọc được Page đã chọn; chưa lưu cấu hình.'
}
if ([string]$verifiedPage.id -ne $pageId -or [string]::IsNullOrWhiteSpace([string]$verifiedPage.name)) {
    throw 'Meta không xác nhận đúng Page ID và tên; chưa lưu cấu hình.'
}

Write-Output "Đã xác minh Page: $($verifiedPage.name) (ID $pageId)."
if (-not $Check) {
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_ID', $pageId, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_NAME', [string]$verifiedPage.name, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_NAME_ID', $pageId, 'User')
    [Environment]::SetEnvironmentVariable('REUP_META_GRAPH_VERSION', $version, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_SYSTEM_USER_TOKEN', $systemToken, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_AUTH_MODE', 'system_user', 'User')
    Write-Output 'Đã chọn System User cho ứng dụng. Page token cũ được giữ lại nhưng không còn được dùng.'
}
Write-Output 'Đây là phép kiểm tra đọc Page; quyền đăng cần thử bằng một bài có kiểm soát.'
