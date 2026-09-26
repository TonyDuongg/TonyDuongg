#!/usr/bin/env python3
"""
Generate a beautiful, dark-slate themed Top Languages SVG card
using the GitHub GraphQL API with private repository support (when token is provided)
or fallback to public REST API.
"""

import os
import sys
import json
import urllib.request
import urllib.error

TOKEN = (
    os.environ.get("METRICS_TOKEN")
    or os.environ.get("GH_TOKEN")
    or os.environ.get("PAT")
    or os.environ.get("TOKEN")
    or os.environ.get("GITHUB_TOKEN")
)

GRAPHQL_URL = "https://api.github.com/graphql"
GRAPHQL_QUERY = """
query($after: String) {
  viewer {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        isPrivate
        languages(first: 25, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
"""

# Default colors for popular languages
DEFAULT_COLORS = {
    "Go": "#00ADD8",
    "Python": "#3572A5",
    "TypeScript": "#3178C6",
    "JavaScript": "#F7DF1E",
    "C#": "#178600",
    "Java": "#B07219",
    "C++": "#F34B7D",
    "C": "#555555",
    "Rust": "#DEA584",
    "HTML": "#E34C26",
    "CSS": "#563D7C",
    "Shell": "#89E051",
    "Dockerfile": "#384D54",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
}

def fetch_languages_graphql(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "TonyDuongg-Profile-Langs-Generator",
    }
    
    languages_data = {}
    has_next_page = True
    after_cursor = None
    
    while has_next_page:
        payload = {
            "query": GRAPHQL_QUERY,
            "variables": {"after": after_cursor}
        }
        
        req = urllib.request.Request(
            GRAPHQL_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
            return None
            
        data = result.get("data", {}).get("viewer", {}).get("repositories", {})
        nodes = data.get("nodes", [])
        page_info = data.get("pageInfo", {})
        
        for repo in nodes:
            repo_langs = repo.get("languages", {}).get("edges", [])
            for edge in repo_langs:
                lang_size = edge.get("size", 0)
                lang_node = edge.get("node", {})
                name = lang_node.get("name")
                color = lang_node.get("color") or DEFAULT_COLORS.get(name, "#58a6ff")
                
                if name:
                    if name not in languages_data:
                        languages_data[name] = {"size": 0, "color": color}
                    languages_data[name]["size"] += lang_size
                    
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")
        
    return languages_data

def fetch_languages_public(username="TonyDuongg"):
    print("Falling back to public REST API...")
    headers = {"User-Agent": "TonyDuongg-Profile-Langs-Generator"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
        
    req = urllib.request.Request(f"https://api.github.com/users/{username}/repos", headers=headers)
    languages_data = {}
    
    try:
        with urllib.request.urlopen(req) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
            for repo in repos:
                lang_url = repo.get("languages_url")
                if lang_url:
                    l_req = urllib.request.Request(lang_url, headers=headers)
                    with urllib.request.urlopen(l_req) as l_resp:
                        langs = json.loads(l_resp.read().decode("utf-8"))
                        for l_name, l_size in langs.items():
                            if l_name not in languages_data:
                                languages_data[l_name] = {"size": 0, "color": DEFAULT_COLORS.get(l_name, "#58a6ff")}
                            languages_data[l_name]["size"] += l_size
    except Exception as e:
        print(f"Error fetching public repos: {e}", file=sys.stderr)
        
    return languages_data

def generate_svg(languages_data, output_path="dist/top-langs.svg"):
    # Sort languages by size descending
    sorted_langs = sorted(languages_data.items(), key=lambda x: x[1]["size"], reverse=True)
    
    # Filter to top 8 languages
    top_langs = sorted_langs[:8]
    total_size = sum(lang[1]["size"] for lang in top_langs)
    
    if total_size == 0:
        # Default placeholder if no languages
        top_langs = [("Go", {"size": 40, "color": "#00ADD8"}), ("Python", {"size": 30, "color": "#3572A5"}), ("TypeScript", {"size": 20, "color": "#3178C6"}), ("JavaScript", {"size": 10, "color": "#F7DF1E"})]
        total_size = 100

    card_width = 380
    items_count = len(top_langs)
    rows_count = (items_count + 1) // 2
    card_height = 85 + rows_count * 28 + 15
    bar_total_width = 330
    
    items = []
    accumulated_width = 0
    
    for name, info in top_langs:
        pct = (info["size"] / total_size) * 100
        part_width = round((info["size"] / total_size) * bar_total_width, 1)
        items.append({
            "name": name,
            "color": info["color"],
            "pct": pct,
            "width": part_width,
            "x": accumulated_width
        })
        accumulated_width += part_width

    bar_rects = []
    for item in items:
        if item["width"] > 0:
            bar_rects.append(
                f'<rect x="{item["x"]}" y="0" width="{item["width"]}" height="8" fill="{item["color"]}" />'
            )
            
    list_items = []
    col_width = 165
    for i, item in enumerate(items):
        col = i % 2
        row = i // 2
        x = 25 + col * col_width
        y = 95 + row * 28
        
        pct_str = f"{item['pct']:.1f}%"
        display_name = item['name']
        if len(display_name) > 13:
            display_name = display_name[:12] + "…"
            
        list_items.append(f'''
    <g transform="translate({x}, {y})">
      <circle cx="6" cy="6" r="5" fill="{item['color']}" />
      <text x="18" y="10" class="lang-label">{display_name}</text>
      <text x="{col_width - 15}" y="10" text-anchor="end" class="lang-pct">{pct_str}</text>
    </g>''')

    svg_content = f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Most Used Languages">
  <style>
    .card-title {{
      font: 600 18px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      fill: #58a6ff;
    }}
    .lang-label {{
      font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      fill: #c9d1d9;
    }}
    .lang-pct {{
      font: 400 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      fill: #8b949e;
    }}
    .card-bg {{
      fill: #0d1117;
      stroke: #30363d;
      stroke-width: 1;
      rx: 8;
    }}
  </style>

  <rect class="card-bg" width="{card_width - 2}" height="{card_height - 2}" x="1" y="1" />

  <!-- Title -->
  <text x="25" y="38" class="card-title">Most Used Languages</text>

  <!-- Progress Bar -->
  <g transform="translate(25, 55)">
    <mask id="bar-mask">
      <rect x="0" y="0" width="{bar_total_width}" height="8" rx="4" fill="white" />
    </mask>
    <g mask="url(#bar-mask)">
      {''.join(bar_rects)}
    </g>
  </g>

  <!-- Languages List (2 Columns) -->
  <g>
    {''.join(list_items)}
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    data = None
    if TOKEN:
        try:
            print("Attempting GraphQL with provided token...")
            data = fetch_languages_graphql(TOKEN)
        except Exception as e:
            print(f"GraphQL failed: {e}, falling back to REST...", file=sys.stderr)
            
    if not data:
        data = fetch_languages_public("TonyDuongg")
        
    print(f"Found {len(data)} distinct languages.")
    for lang, info in sorted(data.items(), key=lambda x: x[1]['size'], reverse=True)[:10]:
        print(f" - {lang}: {info['size']} bytes")
    generate_svg(data)
