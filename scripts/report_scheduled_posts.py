import os
import sys
import json
import argparse
import datetime
import urllib.request
import urllib.error
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_ROOT)

def load_env():
    """Load configuration from .env and .env.deploy"""
    config = {}
    for env_file in ['.env', '.env.deploy']:
        env_path = os.path.join(PROJECT_ROOT, env_file)
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k and k not in config:
                            config[k] = v
    return config

def get_scheduled_posts(config):
    """Fetch scheduled ('future') posts from remote WordPress via SSH/PHP"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        config['SSH_HOST'],
        int(config.get('SSH_PORT', 2222)),
        config['SSH_USER'],
        config['SSH_PASS'],
        timeout=20,
        look_for_keys=False,
        allow_agent=False
    )

    php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
global $wpdb;
$future_posts = $wpdb->get_results("SELECT ID, post_title, post_date FROM {$wpdb->posts} WHERE post_type='post' AND post_status='future' ORDER BY post_date ASC");
$posts_data = array();
foreach ($future_posts as $p) {
    $posts_data[] = array(
        'id' => $p->ID,
        'title' => $p->post_title,
        'date' => $p->post_date
    );
}
echo json_encode(array('count' => count($posts_data), 'posts' => $posts_data), JSON_UNESCAPED_UNICODE);
"""

    temp_php = f"/tmp/check_sched_{int(datetime.datetime.now().timestamp())}.php"
    sftp = ssh.open_sftp()
    with sftp.file(temp_php, 'w') as f:
        f.write(php_code)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {temp_php} && rm {temp_php}")
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    ssh.close()

    if err:
        print(f"[Remote PHP Error] {err}", file=sys.stderr)

    try:
        # Find JSON in out
        json_start = out.find('{')
        if json_start != -1:
            return json.loads(out[json_start:])
    except Exception as e:
        print(f"[JSON Parse Error] {e}\nRaw output: {out}", file=sys.stderr)

    return {'count': 0, 'posts': []}

def format_slack_message(data, threshold=10, force_mention=False):
    """Format message for Slack notification"""
    count = data.get('count', 0)
    posts = data.get('posts', [])
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    is_low = count <= threshold or force_mention

    if is_low:
        title = "🚨 *【リマインド】投稿予約数が少なくなっています*"
        mention = "<@Hirofumi Kuruma> @Hirofumi Kuruma"
        status_line = f"{mention} 現在の投稿予約数は *{count} 件*（基準: {threshold} 件以下）です。\n至急、新しい投稿記事の作成・予約スケジュール設定をお願いいたします！"
    else:
        title = "📅 *本日の投稿予約状況レポート*"
        status_line = f"現在の投稿予約数は *{count} 件* です（十分なストックがあります: 基準10件超）。"

    # List of upcoming posts
    post_lines = []
    for idx, p in enumerate(posts[:15], 1):
        dt = p.get('date', '')[:16]
        p_title = p.get('title', '無題')
        post_lines.append(f"{idx}. `[{dt}]` {p_title}")

    if len(posts) > 15:
        post_lines.append(f"…他 {len(posts) - 15} 件")

    posts_block_text = "\n".join(post_lines) if post_lines else "現在、予約投稿はありません。"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📚 oscss-wp-nihongo 投稿予約状況",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{title}\n{status_line}\n\n*確認日時:* {now_str}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📋 予約済み記事一覧 ({count}件):*\n{posts_block_text}"
            }
        }
    ]

    fallback_text = f"【投稿予約数レポート】現在の予約数: {count}件"
    if is_low:
        fallback_text += " @Hirofumi Kuruma 投稿作成をお願いします！"

    return {
        "text": fallback_text,
        "blocks": blocks,
        "link_names": 1
    }

def send_slack(payload, config):
    """Send message to Slack via Webhook or Bot Token"""
    webhook_url = config.get('SLACK_WEBHOOK_URL') or os.environ.get('SLACK_WEBHOOK_URL', '')
    bot_token = config.get('SLACK_BOT_TOKEN') or os.environ.get('SLACK_BOT_TOKEN', '')
    channel_id = config.get('SLACK_CHANNEL_ID') or os.environ.get('SLACK_CHANNEL_ID', 'C0BJZ4S8PJM')

    data = json.dumps(payload).encode('utf-8')

    # Try Webhook first
    if webhook_url:
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"[Slack Success] Sent via Webhook (HTTP {resp.status})")
                return True
        except Exception as e:
            print(f"[Slack Webhook Error] {e}", file=sys.stderr)

    # Fallback to Bot API
    if bot_token:
        bot_payload = dict(payload)
        bot_payload['channel'] = channel_id
        req = urllib.request.Request(
            'https://slack.com/api/chat.postMessage',
            data=json.dumps(bot_payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': f"Bearer {bot_token}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get('ok'):
                    print(f"[Slack Success] Sent via Bot Token to {channel_id}")
                    return True
                else:
                    print(f"[Slack Bot Error] {res.get('error')}", file=sys.stderr)
        except Exception as e:
            print(f"[Slack Bot Exception] {e}", file=sys.stderr)

    return False

def main():
    parser = argparse.ArgumentParser(description="Check WordPress scheduled posts and report to Slack.")
    parser.add_argument("--dry-run", action="store_true", help="Print report to console without sending to Slack.")
    parser.add_argument("--threshold", type=int, default=10, help="Alert threshold count (default: 10).")
    parser.add_argument("--force-mention", action="store_true", help="Force mention alert even if above threshold.")
    args = parser.parse_args()

    config = load_env()
    print("[1/3] Fetching scheduled posts from production WordPress...")
    data = get_scheduled_posts(config)
    count = data.get('count', 0)
    print(f"[2/3] Retrieved {count} scheduled posts.")

    payload = format_slack_message(data, threshold=args.threshold, force_mention=args.force_mention)

    if args.dry_run:
        print("[Dry-run] Slack Payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("[3/3] Sending report to Slack...")
    success = send_slack(payload, config)
    if success:
        print("Done! Report delivered to Slack.")
    else:
        print("Failed to deliver Slack report.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
