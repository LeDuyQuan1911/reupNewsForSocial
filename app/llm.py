"""OpenAI-compatible chat endpoint, usable with a locally configured 9Router."""

import json
import os
import base64
from urllib.request import Request, urlopen


def request_chat(model: str, messages: list[dict], max_tokens: int) -> str:
    base_url = os.environ.get("REUP_LLM_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
    if not model:
        raise ValueError("Chưa cấu hình model LLM")
    payload = json.dumps({
        "model": model,
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "messages": messages,
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


def chat(system: str, user: str, max_tokens: int = 600) -> str:
    model = os.environ.get("REUP_LLM_MODEL", "").strip()
    return request_chat(model, [{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens)


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
    return parse_verdict(raw)


def parse_verdict(raw: str) -> tuple[bool, str]:
    verdict = json.loads(raw)
    if not isinstance(verdict, dict) or type(verdict.get("allowed")) is not bool:
        raise ValueError("Kết quả kiểm duyệt không hợp lệ")
    reason = str(verdict.get("reason", "")).strip()[:300]
    return verdict["allowed"], reason


def check_post(body: str, image_bytes: bytes) -> tuple[bool, str]:
    model = os.environ.get("REUP_LLM_VISION_MODEL", "").strip() or os.environ.get("REUP_LLM_MODEL", "").strip()
    if not model:
        raise ValueError("Chưa cấu hình REUP_LLM_VISION_MODEL hoặc REUP_LLM_MODEL")
    image = base64.b64encode(image_bytes).decode("ascii")
    system = (
        "Kiểm duyệt cả văn bản và ảnh cho bài Facebook/LinkedIn. Chặn nội dung bạo lực, thù ghét, tình dục, bóc lột trẻ em, "
        "quấy rối, lừa đảo, thông tin riêng tư và hình ảnh phản cảm. Nếu không xem được ảnh hoặc không chắc, trả allowed=false. "
        'Chỉ trả JSON dạng {"allowed": true hoặc false, "reason": "lý do ngắn"}.'
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": [
            {"type": "text", "text": body},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": "low"}},
        ]},
    ]
    return parse_verdict(request_chat(model, messages, 180))
