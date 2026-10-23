"""OpenAI-compatible chat endpoint, usable with a locally configured 9Router."""

import json
import os
from urllib.request import Request, urlopen


def chat(system: str, user: str, max_tokens: int = 600) -> str:
    base_url = os.environ.get("REUP_LLM_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
    model = os.environ.get("REUP_LLM_MODEL", "").strip()
    if not model:
        raise ValueError("Chưa cấu hình REUP_LLM_MODEL")
    payload = json.dumps({
        "model": model,
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("REUP_LLM_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = Request(f"{base_url}/chat/completions", data=payload, headers=headers, method="POST")
    with urlopen(request, timeout=60) as response:
        result = json.load(response)
    content = result["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM không trả nội dung hợp lệ")
    return content.strip()


def write_draft(title: str, summary: str, source_url: str) -> str:
    system = (
        "Viết một bài Facebook ngắn bằng tiếng Việt về tin công nghệ. Giọng thân mật với cộng đồng IT: mở đầu báo hiệu tin đáng chú ý, "
        "chia thành các đoạn ngắn, có thể dùng chút hài hước, sau đó nêu chi tiết kỹ thuật đã biết và điều người đọc nên làm nếu có căn cứ. "
        "Có thể kết bằng câu hỏi gợi thảo luận. Dùng tối đa hai emoji khi thật hợp. "
        "Chỉ dùng dữ kiện trong tiêu đề và tóm tắt đã cho; không bịa số liệu, trích dẫn, trải nghiệm cá nhân hoặc nội dung chưa đọc. "
        "Không sao chép câu chữ của nguồn hoặc bài mẫu. Kết thúc bằng liên kết nguồn gốc. Chỉ trả nội dung bài đăng."
    )
    user = f"Tiêu đề: {title}\nTóm tắt: {summary}\nNguồn: {source_url}"
    draft = chat(system, user, 500)
    if source_url not in draft:
        draft = f"{draft}\n\nNguồn: {source_url}"
    return draft


def check_content(body: str) -> tuple[bool, str]:
    system = (
        "Bạn kiểm duyệt bài đăng trước khi đăng lên mạng xã hội. Đánh giá nguy cơ vi phạm tiêu chuẩn cộng đồng của Meta "
        "và LinkedIn: kích động/bạo lực, thù ghét, quấy rối, tình dục, bóc lột trẻ em, lừa đảo, thông tin sai lệch, "
        "spam và tiết lộ dữ liệu riêng tư. Nếu không chắc, trả allowed=false. Chỉ trả JSON đúng dạng "
        '{"allowed": true hoặc false, "reason": "lý do ngắn"}. Không thêm markdown.'
    )
    raw = chat(system, body, 160)
    verdict = json.loads(raw)
    if not isinstance(verdict, dict) or type(verdict.get("allowed")) is not bool:
        raise ValueError("Kết quả kiểm duyệt không hợp lệ")
    reason = str(verdict.get("reason", "")).strip()[:300]
    return verdict["allowed"], reason
