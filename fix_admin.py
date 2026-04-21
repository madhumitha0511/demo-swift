import os, glob, re

# 1. Read index.html for header, footer, and styles
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

header_match = re.search(r'(<header.*?>.*?</header>)', index_content, flags=re.DOTALL)
footer_match = re.search(r'(<footer.*?>.*?</footer>)', index_content, flags=re.DOTALL)
style_match = re.search(r'(<style>.*?</style>)', index_content, flags=re.DOTALL)

if not (header_match and footer_match and style_match):
    print("Could not find header/footer/style in index.html")
    exit(1)

header_block = header_match.group(1)
footer_block = footer_match.group(1)
style_block = style_match.group(1)

# 2. Update admin.html
with open('admin.html', 'r', encoding='utf-8') as f:
    admin_content = f.read()

# Replace header
admin_content = re.sub(r'<header.*?>.*?</header>', header_block, admin_content, flags=re.DOTALL)

# Replace footer
admin_content = re.sub(r'<footer.*?>.*?</footer>', footer_block, admin_content, flags=re.DOTALL)

# Inject styles if not present
if '<style>' not in admin_content:
    admin_content = admin_content.replace('</head>', '\n' + style_block + '\n</head>')

# Update Admin button to match theme
admin_content = admin_content.replace('class="vd rj ek rc rg gh lk ml il _l gi hi"', 'class="sv-submit-btn" style="width: 100%; justify-content: center; margin-top: 10px;"')

# Ensure logo changes in case the regex missed it (though header/footer replacement covers it, let's just make sure)
admin_content = admin_content.replace('images/logo-light.svg', 'images/logo-light.jpeg')
admin_content = admin_content.replace('images/logo-dark.svg', 'images/logo-dark.jpeg')

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_content)
print("Updated admin.html layout, header, footer, styles, and logo.")

# 3. Update the injected scripts in all HTML files
new_script = '''
    <script>
      document.addEventListener('DOMContentLoaded', () => {
        const editables = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, a');
        const pagePath = window.location.pathname.split('/').pop() || 'index.html';
        
        // Assign stable IDs
        editables.forEach((el, i) => {
          if (!el.hasAttribute('data-edit-id')) {
            el.setAttribute('data-edit-id', 'sv-edit-' + i);
          }
        });

        // Load saved content globally
        const savedContent = JSON.parse(localStorage.getItem('sv_content_' + pagePath)) || {};
        Object.keys(savedContent).forEach(id => {
          const el = document.querySelector(`[data-edit-id="${id}"]`);
          if (el) {
            el.innerHTML = savedContent[id];
          }
        });

        // Admin Edit Mode
        if (localStorage.getItem('isAdmin') === 'true') {
          editables.forEach(el => {
            el.setAttribute('contenteditable', 'true');
            el.style.outline = '1px dashed #4A6CF7';
            el.style.padding = '2px';
            
            if (el.tagName === 'A') {
              el.addEventListener('click', e => e.preventDefault());
            }
          });

          const btn = document.createElement('button');
          btn.innerText = 'Save Content';
          btn.style.position = 'fixed';
          btn.style.bottom = '20px';
          btn.style.left = '20px';
          btn.style.zIndex = '999999';
          btn.style.padding = '10px 20px';
          btn.style.background = '#4A6CF7';
          btn.style.color = 'white';
          btn.style.border = 'none';
          btn.style.borderRadius = '24px';
          btn.style.cursor = 'pointer';
          btn.style.fontWeight = '700';
          btn.style.boxShadow = '0 4px 15px rgba(74, 108, 247, 0.4)';
          btn.onclick = () => {
            const toSave = {};
            editables.forEach((el, i) => {
              toSave['sv-edit-' + i] = el.innerHTML;
            });
            localStorage.setItem('sv_content_' + pagePath, JSON.stringify(toSave));
            btn.innerText = 'Saved!';
            setTimeout(() => btn.innerText = 'Save Content', 2000);
          };
          document.body.appendChild(btn);

          const logoutBtn = document.createElement('button');
          logoutBtn.innerText = 'Logout Admin';
          logoutBtn.style.position = 'fixed';
          logoutBtn.style.bottom = '20px';
          logoutBtn.style.left = '160px';
          logoutBtn.style.zIndex = '999999';
          logoutBtn.style.padding = '10px 20px';
          logoutBtn.style.background = '#ef4444';
          logoutBtn.style.color = 'white';
          logoutBtn.style.border = 'none';
          logoutBtn.style.borderRadius = '24px';
          logoutBtn.style.cursor = 'pointer';
          logoutBtn.style.fontWeight = '700';
          logoutBtn.style.boxShadow = '0 4px 15px rgba(239, 68, 68, 0.4)';
          logoutBtn.onclick = () => {
            localStorage.removeItem('isAdmin');
            location.reload();
          };
          document.body.appendChild(logoutBtn);
        }
      });
    </script>
'''

old_script_pattern = re.compile(r'<script>\s*if \(localStorage\.getItem\(\'isAdmin\'\).*?}\n.*?});\n\s*}\n\s*</script>', re.DOTALL)
fallback_pattern = re.compile(r'<script>\s*if \(localStorage\.getItem\(\'isAdmin\'\) === \'true\'\).*?</script>', re.DOTALL)
new_script_pattern = re.compile(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\'\, \(\) => {\s*const editables = document\.querySelectorAll.*?</script>', re.DOTALL)

for file in glob.glob('*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean old scripts
    content = old_script_pattern.sub('', content)
    content = fallback_pattern.sub('', content)
    content = new_script_pattern.sub('', content)

    # Append new script
    content = content.replace('</body>', new_script + '\n</body>')
    content = content.replace('\n\n</body>', '\n</body>')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated scripts in {file}")

