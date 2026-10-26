"""OpenAI-compatible chat endpoint, usable with a locally configured 9Router."""

import json
import os
import base64
import random
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen


STYLE_RANDOM = random.SystemRandom()
OPENING_ANGLES = (
    "Bắt đầu bằng điều mới hoặc khác thường có căn cứ trong nguồn.",
    "Bắt đầu bằng một câu hỏi cụ thể mà thông tin trong nguồn có thể trả lời.",
    "Bắt đầu bằng lợi ích thực tế cho người đọc nếu nguồn nêu rõ lợi ích đó.",
    "Bắt đầu bằng tình huống quen thuộc với người làm công nghệ nếu dữ kiện cho phép.",
)


def request_chat(model: str, messages: list[dict], max_tokens: int, temperature: float = 0.2) -> str:
    base_url = os.environ.get("REUP_LLM_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
    if not model:
        raise ValueError("Chưa cấu hình model LLM")
    payload = json.dumps({
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
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


def chat(system: str, user: str, max_tokens: int = 600, temperature: float = 0.2) -> str:
    model = os.environ.get("REUP_LLM_MODEL", "").strip()
    return request_chat(model, [{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens, temperature)


def write_draft(title: str, summary: str, source_url: str) -> str:
    system = (
        "Viết một bài Facebook tiếng Việt ngắn, cuốn hút và dễ đọc cho cộng đồng IT. Mở đầu bằng một chi tiết cụ thể đáng chú ý; "
        "tránh câu mở đầu chung chung, giật gân hoặc khẳng định quá mức. Chia thành đoạn ngắn, nêu điều mới, vì sao đáng quan tâm "
        "và người đọc có thể tìm hiểu hoặc làm gì nếu nguồn đủ căn cứ. Có thể dùng chút hài hước tự nhiên và kết bằng câu hỏi gợi thảo luận cụ thể. "
        "Tự chọn cách dùng emoji nếu chúng giúp bài viết sinh động hoặc làm rõ ý; chọn biểu tượng hợp ngữ cảnh, "
        "thay đổi số lượng và vị trí theo nội dung từng bài. Không áp công thức một emoji cho mỗi dòng, "
        "không dùng emoji chỉ để trang trí và không thêm vào dòng hashtag hoặc nguồn. "
        "Thêm một dòng 2–5 hashtag ngắn, không dấu và liên quan trực tiếp đến chủ đề trước dòng nguồn. "
        "Chỉ dùng dữ kiện trong tiêu đề và tóm tắt đã cho; không bịa số liệu, trích dẫn, trải nghiệm cá nhân, "
        "lợi ích như tiết kiệm thời gian hoặc nội dung chưa đọc. Nếu giá trị thực tế chưa được nguồn xác nhận, nêu như một khả năng để người đọc tự khám phá. "
        "Không sao chép câu chữ của nguồn hoặc bài mẫu. Kết thúc bằng liên kết nguồn gốc. Chỉ trả nội dung bài đăng."
    )
    angle = STYLE_RANDOM.choice(OPENING_ANGLES)
    user = f"Tiêu đề: {title}\nTóm tắt: {summary}\nNguồn: {source_url}\nGợi ý cách mở bài (chỉ dùng nếu dữ kiện hỗ trợ): {angle}"
    draft = chat(system, user, 500, temperature=0.65)
    source_line = f"Nguồn: {source_url}"
    draft = draft.replace(source_line, "").strip()
    hashtags = re.findall(r"(?<!\w)#[A-Za-z][A-Za-z0-9_]*", draft)
    if len(hashtags) < 2:
        fallback = ("#CongNghe", "#TinMoi")
        missing = [tag for tag in fallback if tag not in hashtags][:2 - len(hashtags)]
        draft = f"{draft.rstrip()}\n\n{' '.join(missing)}"
    return f"{draft.rstrip()}\n\n{source_line}"


def generate_image(title: str, summary: str) -> bytes:
    """Generate a grounded cover through the local 9Router image endpoint."""
    model = os.environ.get("REUP_LLM_IMAGE_MODEL", "").strip()
    if not model:
        raise ValueError("Chưa cấu hình REUP_LLM_IMAGE_MODEL cho model tạo ảnh trong 9Router")
    base_url = os.environ.get("REUP_LLM_BASE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Tạo ảnh chỉ được gửi tới 9Router trên máy cục bộ")
    brief_system = (
        "Từ đúng tiêu đề và tóm tắt được cung cấp, lập dàn ý ảnh tin công nghệ. "
        "Chỉ trả JSON với headline (tên tổ chức/sản phẩm, tối đa 45 ký tự), subtitle (tin chính, tối đa 65 ký tự) "
        "và steps (1–3 ý ngắn, mỗi ý tối đa 30 ký tự) nếu nguồn thực sự mô tả các bước hoặc tác động. "
        "Không bịa người, logo, con số, sự kiện, kết quả đã hoàn thành hay chi tiết ngoài nguồn."
    )
    raw_brief = chat(brief_system, f"Tiêu đề: {title[:300]}\nTóm tắt: {summary[:1200]}", 220, temperature=0.2)
    match = re.search(r"\{.*\}", raw_brief, flags=re.DOTALL)
    if not match:
        raise ValueError("9Router không trả dàn ý ảnh hợp lệ")
    brief = json.loads(match.group())
    headline, subtitle, steps = brief.get("headline"), brief.get("subtitle"), brief.get("steps")
    if (not isinstance(headline, str) or not headline.strip() or len(headline) > 45
            or not isinstance(subtitle, str) or not subtitle.strip() or len(subtitle) > 65
            or not isinstance(steps, list) or len(steps) > 3
            or any(not isinstance(step, str) or not step.strip() or len(step) > 30 for step in steps)):
        raise ValueError("Dàn ý ảnh từ 9Router không hợp lệ")
    visual = (f"Show one row of {len(steps)} connected panels with these exact short labels: {'; '.join(steps)}. "
              if steps else "Show one clear visual of the named subject without implying a completed process. ")
    prompt = (
        "Horizontal 16:9 premium editorial news infographic, readable on a phone. "
        f"One very large exact headline: {headline.strip()}. "
        f"One smaller exact subtitle: {subtitle.strip()}. "
        f"{visual}"
        "Use only the provided headline, subtitle and short panel labels as text; no badges, footers or hashtags. "
        "No humans, uniforms, offices, laboratories, fabricated software screens or official logos. "
        "No invented results, numbers, quotes, events or locations. Do not imply a proposed partnership already "
        "completed its research. Spell all visible text exactly. "
        f"Source title: {title[:300]}\nSource summary: {summary[:1200]}"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "n": 1, "size": "1792x1024",
                          "response_format": "b64_json"}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("REUP_LLM_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = Request(f"{base_url}/images/generations", data=payload, headers=headers, method="POST")
    with urlopen(request, timeout=180) as response:
        encoded = response.read(16_000_001)
    if len(encoded) > 16_000_000:
        raise ValueError("Phản hồi ảnh từ 9Router quá lớn")
    item = json.loads(encoded)["data"][0]
    if item.get("b64_json"):
        image = base64.b64decode(item["b64_json"], validate=True)
    elif item.get("url"):
        from . import media
        image, _ = media.fetch_public_bytes(item["url"], media.MAX_IMAGE_BYTES)
    else:
        raise ValueError("9Router không trả dữ liệu ảnh")
    if not image or len(image) > 8_000_000:
        raise ValueError("Ảnh do 9Router trả về không hợp lệ")
    return image


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
        "quấy rối, lừa đảo, thông tin riêng tư và hình ảnh phản cảm. Ảnh phải thể hiện trực tiếp chủ đề, sản phẩm hoặc "
        "quy trình được nói tới trong bài; từ chối ảnh trang trí chung chung, logo đơn lẻ hoặc thẻ chỉ có tiêu đề. "
        "Nếu không xem được ảnh hoặc không chắc ảnh liên quan, trả allowed=false. "
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
