param(
    [switch]$Check
)

$ErrorActionPreference = 'Stop'

if ($Check) {
    $pageId = [Environment]::GetEnvironmentVariable('REUP_FACEBOOK_PAGE_ID', 'User')
    $version = [Environment]::GetEnvironmentVariable('REUP_META_GRAPH_VERSION', 'User')
    $token = [Environment]::GetEnvironmentVariable('REUP_FACEBOOK_PAGE_TOKEN', 'User')
    if (-not $pageId -or -not $version -or -not $token) {
        throw 'Chưa có đủ Page ID, Page token và phiên bản Graph API trong biến môi trường User.'
    }
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
    [Environment]::SetEnvironmentVariable('REUP_META_GRAPH_VERSION', $version, 'User')
    [Environment]::SetEnvironmentVariable('REUP_FACEBOOK_PAGE_TOKEN', $token, 'User')
    Write-Output 'Đã lưu cấu hình trong biến môi trường User của Windows. Khởi động lại dashboard sau khi xem các bài đang chờ.'
}
Write-Output 'Kiểm tra đọc Page không xác nhận quyền đăng; hãy thử một bài có kiểm soát trước khi để lịch tự chạy.'
