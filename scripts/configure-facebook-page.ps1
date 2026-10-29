param(
    [switch]$Check,
    [switch]$FromUserToken
)

$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'load-env.ps1') -RepoRoot (Split-Path -Parent $PSScriptRoot)
if ($Check -and $FromUserToken) {
    throw 'Chọn -Check hoặc -FromUserToken, không dùng cả hai cùng lúc.'
}

if ($Check) {
    if ($env:REUP_FACEBOOK_AUTH_MODE -eq 'system_user') {
        throw 'Máy đang dùng System User. Chạy configure-facebook-system-user.ps1 -Check.'
    }
    $pageId = $env:REUP_FACEBOOK_PAGE_ID
    $version = $env:REUP_META_GRAPH_VERSION
    $token = $env:REUP_FACEBOOK_PAGE_TOKEN
    if (-not $pageId -or -not $version -or -not $token) {
        throw 'Chưa có đủ Page ID, Page token và phiên bản Graph API trong .env hoặc biến môi trường User.'
    }
} elseif ($FromUserToken) {
    $pageId = [Environment]::GetEnvironmentVariable('REUP_FACEBOOK_PAGE_ID', 'User')
    if (-not $pageId) {
        $pageId = (Read-Host 'Facebook Page ID').Trim()
    }
    $version = [Environment]::GetEnvironmentVariable('REUP_META_GRAPH_VERSION', 'User')
    if (-not $version) {
        $version = (Read-Host 'Graph API version (dạng vN.N)').Trim()
    }
    if ($pageId -notmatch '^\d+$' -or $version -notmatch '^v\d+\.\d+$') {
        throw 'Page ID hoặc phiên bản Graph API chưa hợp lệ.'
    }
    $secureUserToken = Read-Host 'User access token từ Graph API Explorer (đầu vào được ẩn)' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureUserToken)
    try {
        $userToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
    if ([string]::IsNullOrWhiteSpace($userToken)) {
        throw 'User access token trống.'
    }
    $uri = "https://graph.facebook.com/$version/${pageId}?fields=id,name,access_token"
    try {
        $pageFromUser = Invoke-RestMethod -Method Get -Uri $uri -Headers @{Authorization = "Bearer $userToken"} -TimeoutSec 20
    } catch {
        throw 'Meta chưa trả Page token. Kiểm tra User token, quyền pages_show_list/pages_manage_posts và quyền quản lý Page trong Graph API Explorer.'
    } finally {
        $userToken = $null
    }
    if ([string]$pageFromUser.id -ne $pageId -or [string]::IsNullOrWhiteSpace([string]$pageFromUser.access_token)) {
        throw 'Meta không trả Page token cho đúng Page ID; chưa lưu cấu hình.'
    }
    $token = [string]$pageFromUser.access_token
} else {
    $pageId = (Read-Host 'Facebook Page ID').Trim()
    $version = (Read-Host 'Graph API version (dạng vN.N)').Trim()
    $secureToken = Read-Host 'Page access token (đầu vào được ẩn)' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

if ($pageId -notmatch '^\d+$' -or $version -notmatch '^v\d+\.\d+$' -or [string]::IsNullOrWhiteSpace($token)) {
    throw 'Page ID, phiên bản Graph API hoặc token chưa hợp lệ.'
}

$uri = "https://graph.facebook.com/$version/${pageId}?fields=id,name"
try {
    $page = Invoke-RestMethod -Method Get -Uri $uri -Headers @{Authorization = "Bearer $token"} -TimeoutSec 20
} catch {
    throw 'Không đọc được Page bằng token này. Kiểm tra Page ID, quyền, phiên bản API và hạn token trong Meta App.'
}
if ([string]$page.id -ne $pageId) {
    throw 'Token không trả đúng Page ID đã nhập; chưa lưu cấu hình.'
}

Write-Output "Đã xác minh quyền đọc Page: $($page.name) (ID $pageId)."
if (-not $Check) {
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_ID', $pageId, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_NAME', [string]$page.name, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_NAME_ID', $pageId, 'User')
    [Environment]::SetEnvironmentVariable('REUP_META_GRAPH_VERSION', $version, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_TOKEN', $token, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_AUTH_MODE', 'page_token', 'User')
    Write-Output 'Đã lưu cấu hình trong biến môi trường User của Windows. Khởi động lại dashboard sau khi xem các bài đang chờ.'
}
Write-Output 'Kiểm tra đọc Page không xác nhận quyền đăng; hãy thử một bài có kiểm soát trước khi để lịch tự chạy.'
