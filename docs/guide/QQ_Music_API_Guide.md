# QQ 音乐 API 直连指南

## 业务流程

搜索歌曲 → 获取专辑 ID → 拼接专辑封面 URL → 下载图片

## 1. 搜索接口

**URL**: `https://u.y.qq.com/cgi-bin/musicu.fcg`

**方法**: GET（也支持 POST）

**请求头**:
```
Referer: https://y.qq.com/
```

**GET 请求参数**（`data` 字段传入 JSON）:
```
?data={"music.search.SearchCgiService":{"module":"music.search.SearchCgiService","method":"DoSearchForQQMusicDesktop","param":{"search_type":0,"query":"关键词","page_num":1,"num_per_page":10}}}
```

**POST 请求**（Content-Type: application/json，body 同上 JSON）

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `search_type` | number | 0=歌曲 |
| `query` | string | 搜索关键词 |
| `page_num` | number | 页码，从 1 开始 |
| `num_per_page` | number | 每页数量 |

### 响应关键字段

```json
{
  "music.search.SearchCgiService": {
    "code": 0,
    "data": {
      "body": {
        "song": {
          "totalnum": 10,
          "list": [
            {
              "name": "歌曲名",
              "mid": "歌曲mid",
              "id": 123456,
              "singer": [
                {
                  "name": "歌手名",
                  "mid": "歌手mid",
                  "id": 12345
                }
              ],
              "album": {
                "name": "专辑名",
                "id": 75610845,
                "mid": "003qFAzA1ZRtWt"
              }
            }
          ]
        }
      }
    }
  }
}
```

### 从搜索结果中提取专辑 ID

每首歌的 `album` 对象包含两个字段：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `album.id` | number | 专辑数字 ID | `75610845` |
| `album.mid` | string | 专辑字符串 ID（**用于拼接封面 URL**） | `003qFAzA1ZRtWt` |

> **重要**：获取封面图片使用的是 `album.mid`（字符串），不是 `album.id`（数字）。

### curl 示例

```bash
# GET
curl -s "https://u.y.qq.com/cgi-bin/musicu.fcg?data=%7B%22music.search.SearchCgiService%22%3A%7B%22module%22%3A%22music.search.SearchCgiService%22%2C%22method%22%3A%22DoSearchForQQMusicDesktop%22%2C%22param%22%3A%7B%22search_type%22%3A0%2C%22query%22%3A%22cyberlume%20Timeless%20Covers%22%2C%22page_num%22%3A1%2C%22num_per_page%22%3A10%7D%7D%7D" \
  -H "Referer: https://y.qq.com/"

# POST
curl -s "https://u.y.qq.com/cgi-bin/musicu.fcg" \
  -X POST \
  -H "Referer: https://y.qq.com/" \
  -H "Content-Type: application/json" \
  -d '{"music.search.SearchCgiService":{"module":"music.search.SearchCgiService","method":"DoSearchForQQMusicDesktop","param":{"search_type":0,"query":"cyberlume Timeless Covers","page_num":1,"num_per_page":10}}}'
```

---

## 2. 获取专辑封面图片 URL

无需额外请求，直接用搜索结果中的 `album.mid` 拼接：

**URL 模板**:
```
https://y.gtimg.cn/music/photo_new/T002R{size}M000{album_mid}.jpg?max_age={maxAge}
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `size` | 图片尺寸 | `300x300`、`500x500`、`800x800` |
| `album_mid` | 专辑 mid | `003qFAzA1ZRtWt` |
| `maxAge` | 缓存时间（秒） | `2592000`（30天） |

### 示例

专辑 mid 为 `003qFAzA1ZRtWt`，500x500 尺寸：
```
https://y.gtimg.cn/music/photo_new/T002R500x500M000003qFAzA1ZRtWt.jpg?max_age=2592000
```

---

## 3. 下载图片

```bash
curl -s -o album_cover.jpg "https://y.gtimg.cn/music/photo_new/T002R500x500M000003qFAzA1ZRtWt.jpg?max_age=2592000" \
  -H "Referer: https://y.qq.com/"
```

建议请求时带上 `Referer: https://y.qq.com/` 头。

---

## 完整流程示例

```python
import json, urllib.parse, urllib.request

def search(query, page=1, limit=10):
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    data = json.dumps({
        "music.search.SearchCgiService": {
            "module": "music.search.SearchCgiService",
            "method": "DoSearchForQQMusicDesktop",
            "param": {
                "search_type": 0,
                "query": query,
                "page_num": page,
                "num_per_page": limit
            }
        }
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Referer": "https://y.qq.com/",
        "Content-Type": "application/json"
    })
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp["music.search.SearchCgiService"]["data"]["body"]["song"]["list"]

def download_cover(album_mid, filename, size="500x500"):
    cover_url = f"https://y.gtimg.cn/music/photo_new/T002R{size}M000{album_mid}.jpg?max_age=2592000"
    req = urllib.request.Request(cover_url, headers={"Referer": "https://y.qq.com/"})
    with open(filename, "wb") as f:
        f.write(urllib.request.urlopen(req).read())

# 使用
songs = search("cyberlume Timeless Covers")
for s in songs[:3]:
    album_mid = s["album"]["mid"]
    album_name = s["album"]["name"]
    print(f'{s["name"]} / {s["singer"][0]["name"]} / 专辑: {album_name} / mid: {album_mid}')

# 下载封面
download_cover("003qFAzA1ZRtWt", "Timeless_Covers.jpg")
```

---

## 注意事项

- 搜索接口不需要登录 cookie 即可使用
- 封面图片 URL 是 CDN 直链，带 `Referer` 头即可访问
- `data` 参数中的 JSON 如果用 GET 传递，需要 URL 编码
- QQ 音乐可能随时调整接口，如有变动需重新抓包分析
