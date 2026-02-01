import os
import re
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path('.')
LOCALE_DIR = BASE_DIR / 'locale'
LANGUAGES = ['en', 'pt_BR']

def extract_strings():
    """Extract strings marked for translation in .py and .html files."""
    strings = set()
    
    # Regex for python: _("string") or _('string')
    # Also handles verbose_name=_("string")
    py_pattern = re.compile(r'_\(["\'](.*?)["\']\)')
    
    # Regex for templates: {% trans "string" %} or {% trans 'string' %}
    # handling blocktrans is harder, doing simple extraction for now
    tpl_pattern = re.compile(r'{%\s*trans\s+["\'](.*?)["\']\s*%}')
    
    # Blocktrans extraction (basic)
    # blocktrans_pattern = re.compile(r'{%\s*blocktrans.*?%}(.*?){%\s*endblocktrans\s*%}', re.DOTALL) 
    # Not implementing blocktrans complex extraction for this snippet, relying on simple keys.

    for root, _, files in os.walk(BASE_DIR):
        if 'venv' in root or '.git' in root:
            continue
            
        for file in files:
            path = Path(root) / file
            content = ""
            try:
                content = path.read_text(encoding='utf-8')
            except Exception:
                continue

            if file.endswith('.py'):
                matches = py_pattern.findall(content)
                strings.update(matches)
            elif file.endswith('.html'):
                matches = tpl_pattern.findall(content)
                strings.update(matches)
                
    return sorted(list(strings))

def create_po_file(language, strings):
    """Create a .po file for the given language."""
    lc_messages = LOCALE_DIR / language / 'LC_MESSAGES'
    lc_messages.mkdir(parents=True, exist_ok=True)
    
    po_file = lc_messages / 'django.po'
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M%z')
    
    content = f"""msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {now}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: {language}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""
    
    for s in strings:
        # Escape quotes
        safe_s = s.replace('"', '\\"')
        content += f'msgid "{safe_s}"\n'
        content += f'msgstr ""\n\n'
        
    po_file.write_text(content, encoding='utf-8')
    print(f"Created {po_file}")

if __name__ == "__main__":
    found_strings = extract_strings()
    print(f"Found {len(found_strings)} unique strings.")
    
    for lang in LANGUAGES:
        create_po_file(lang, found_strings)
