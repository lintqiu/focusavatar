#!/usr/bin/env python3
"""
数字人生成工具
- 使用前请前往指定网址获取 accessKeyId 和 accessKeySecret（见下方引导）
- 支持两种操作：提交任务（MP3/MP4/文字） / 查询任务结果（orderNo）

关于 OpenClaw 执行超时：
- 提交任务生成视频需要后端处理时间，较长，请在运行时告诉助手：
  "运行这个脚本，需要等待 5-10 分钟，请设置超时 600 秒"
- 助手会根据你说的时间设置执行超时，不会提前中断
"""
import requests
import time
import sys
import json
import os

# 获取密钥的引导地址（注册 → 购买 → 创建密钥，获取 accessKeyId 与 accessKeySecret）
CREDENTIALS_GET_URL = "https://yunji.focus-jd.cn"
API_ENDPOINT = os.environ.get("FOCUSAVATAR_API", "https://yunji.focus-jd.cn")

def prompt(message):
    print(f"\n{message}", end='')
    sys.stdout.flush()
    return input().strip()

def print_credentials_guide():
    """安装/启动时提示用户获取 accessKeyId 与 accessKeySecret（引入流程）"""
    print("\n" + "=" * 50)
    print("  📌 使用前请先获取 accessKeyId 和 accessKeySecret（引入流程）")
    print(f"  🔗 {CREDENTIALS_GET_URL}")
    print()
    print("  1️⃣  请先前往上述地址 注册 账号")
    print("  2️⃣  然后完成 购买/支付")
    print("  3️⃣  在控制台 创建密钥，复制 accessKeyId 和 accessKeySecret")
    print()
    print("  获取后请在下方输入，或设置环境变量免输入：")
    print("     FOCUSAVATAR_ACCESS_KEY_ID / FOCUSAVATAR_ACCESS_KEY_SECRET")
    print("=" * 50 + "\n")

def get_credentials():
    """从环境变量或交互获取 accessKeyId 和 accessKeySecret，返回 (access_key_id, access_key_secret)"""
    access_key_id = os.environ.get("FOCUSAVATAR_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("FOCUSAVATAR_ACCESS_KEY_SECRET", "").strip()
    if access_key_id and access_key_secret:
        return access_key_id, access_key_secret
    if not access_key_id:
        access_key_id = prompt("请输入 accessKeyId（可设置环境变量 FOCUSAVATAR_ACCESS_KEY_ID）: ").strip()
    if not access_key_secret:
        access_key_secret = prompt("请输入 accessKeySecret（可设置环境变量 FOCUSAVATAR_ACCESS_KEY_SECRET）: ").strip()
    return access_key_id, access_key_secret

def make_auth_headers(access_key_id: str, access_key_secret: str):
    """根据 accessKeyId 和 accessKeySecret 生成请求头"""
    headers = {"Content-Type": "application/json"}
    if access_key_id:
        headers["X-Access-Key-Id"] = access_key_id
    if access_key_secret:
        headers["X-Access-Key-Secret"] = access_key_secret
    return headers

def run_submit_flow(access_key_id: str, access_key_secret: str):
    """提交任务流程：输入 MP3/MP4/文字 → 确认 → 提交 → 轮询结果"""
    while True:
        mp3 = ""
        while not mp3:
            mp3 = prompt("1️⃣  请输入 MP3 路径/URL: ")
            if not mp3:
                print("❌ 不能为空，请重新输入")

        mp4 = ""
        while not mp4:
            mp4 = prompt("2️⃣  请输入 MP4 路径/URL: ")
            if not mp4:
                print("❌ 不能为空，请重新输入")

        text = ""
        while not text:
            text = prompt("3️⃣  请输入需要合成的文字内容: ")
            if not text:
                print("❌ 不能为空，请重新输入")

        print("\n📋 请确认信息：")
        print(f"  MP3: {mp3}")
        print(f"  MP4: {mp4}")
        print(f"  文字: {text}")
        print()

        confirm = ""
        while confirm not in ["1", "2"]:
            confirm = prompt("请选择：[1] 提交  [2] 重新输入\n选择: ")
            if confirm not in ["1", "2"]:
                print("❌ 请输入 1 或 2")

        if confirm == "2":
            print("\n🔄 重新开始...")
            continue

        print("\n🚀 正在提交...")
        headers = make_auth_headers(access_key_id, access_key_secret)
        try:
            payload = {"mp3": mp3, "mp4": mp4, "text": text}
            resp = requests.post(
                API_ENDPOINT.rstrip("/") + "/skill/api/submit",
                json=payload,
                headers=headers,
                timeout=999999,
            )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            err_msg = str(e)
            resp = getattr(e, "response", None)
            if resp is not None:
                code_error = resp.headers.get("codeError") or resp.headers.get("codeerror")
                try:
                    body = resp.json()
                    if isinstance(body, dict) and body.get("data") is not None:
                        err_msg = str(body["data"])
                    elif isinstance(body, dict):
                        err_msg = body.get("message") or body.get("msg") or body.get("error") or err_msg
                except Exception:
                    try:
                        err_msg = (resp.text or err_msg).strip() or err_msg
                    except Exception:
                        pass
                if code_error is not None:
                    err_msg = f"{err_msg} [codeError: {code_error}]" if err_msg else f"codeError: {code_error}"
            print(f"\n❌ 提交失败: {err_msg}")
            return

        if "videoUrl" in result:
            print("\n✅ 生成完成!")
            print(f"\n📺 视频链接: {result['videoUrl']}")
            print("\n💡 查询任务结果接口: POST " + API_ENDPOINT.rstrip("/") + "/skill/api/api/result ，需提供 orderNo。")
            return

        print("\n⚙️  生成中...")
        progress = 0
        while progress < 99:
            progress += 1
            print(f"\r正在生成... {int(progress)}%", end='')
            sys.stdout.flush()
            time.sleep(2)

        print(f"\r正在生成... 99% (等待后端处理)", end='')
        sys.stdout.flush()

        if "orderNo" in result:
            task_id = result["orderNo"]
            status_url = API_ENDPOINT.rstrip("/") + "/skill/api/api/result"
            print(f'\n🚀 查询任务结果...orderNo: {task_id}')
            while True:
                try:
                    r = requests.post(
                        status_url,
                        json={"orderNo": task_id},
                        headers=headers,
                        timeout=999999,
                    )
                    raw = r.json()
                    data = json.loads(raw) if isinstance(raw, str) else raw

                    progress_val = data.get("progress")
                    if progress_val is not None and progress_val != "":
                        try:
                            p = min(int(progress_val), 99)
                            print(f"\r正在生成... {p}% (等待后端处理)", end='')
                            sys.stdout.flush()
                        except (TypeError, ValueError):
                            pass

                    if data.get("status") == "done" and "videoUrl" in data:
                        print("\n✅ 生成完成!")
                        print(f"\n📺 视频链接: {data['videoUrl']}")
                        # print("\n💡 之后可通过「查询任务结果」用 orderNo 查询: " + status_url)
                        return
                    elif data.get("status") == "error":
                        print(f"\n❌ 生成失败: {data.get('message', '未知错误')}")
                        return
                    else:
                        time.sleep(11)
                except Exception:
                    time.sleep(4)
        else:
            print(f"\n📄 后端返回: {result}")
            return

def run_query_flow(access_key_id: str, access_key_secret: str):
    """查询任务结果流程：输入 orderNo → 调用 /skill/api/api/result"""
    try:
        from result import query_result
    except ImportError:
        # 若单独运行或路径不同，使用内联实现
        def query_result(order_no: str, key_id: str, key_secret: str):
            url = API_ENDPOINT.rstrip("/") + "/skill/api/api/result"
            h = make_auth_headers(key_id, key_secret)
            r = requests.post(url, json={"orderNo": order_no}, headers=h, timeout=30)
            r.raise_for_status()
            raw = r.json()
            return json.loads(raw) if isinstance(raw, str) else raw

    order_no = prompt("请输入任务单号 (orderNo): ").strip()
    if not order_no:
        print("❌ 任务单号不能为空")
        return
    try:
        data = query_result(order_no, access_key_id, access_key_secret)
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return

    status = data.get("status", "")
    if status == "done" and data.get("videoUrl"):
        print("✅ 任务已完成")
        print(f"📺 视频链接: {data['videoUrl']}")
    elif status == "error":
        print(f"❌ 任务失败: {data.get('message', '未知错误')}")
    else:
        progress = data.get("progress", "")
        print(f"⏳ 状态: {status}, 进度: {progress}")
        print("📄 完整返回:", json.dumps(data, ensure_ascii=False, indent=2))

def main():
    print_credentials_guide()
    access_key_id, access_key_secret = get_credentials()

    print("\n" + "=" * 50)
    print("       数字人生成工具")
    print("=" * 50)

    choice = ""
    while choice not in ["1", "2"]:
        choice = prompt("请选择：[1] 提交任务（生成视频）  [2] 查询任务结果（需 orderNo）\n选择: ")
        if choice not in ["1", "2"]:
            print("❌ 请输入 1 或 2")

    if choice == "1":
        run_submit_flow(access_key_id, access_key_secret)
    else:
        run_query_flow(access_key_id, access_key_secret)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
