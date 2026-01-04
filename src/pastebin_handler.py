import subprocess

def upload(api_key, code):
    try:
        cmd = [
            "curl", "-s", "-X", "POST",
            "-d", f"api_dev_key={api_key}",
            "-d", "api_option=paste",
            "--data-urlencode", f"api_paste_code={code}",
            "https://pastebin.com/api/api_post.php"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        if "https://pastebin.com" in res.stdout:
            return True, res.stdout
        return False, res.stdout
    except Exception as e:
        return False, str(e)