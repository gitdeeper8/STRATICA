#!/usr/bin/env python3

"""STRATICA Upload v1.0.0 - بدون توكن (سيتم إدخاله يدوياً)"""

import requests
import hashlib
import os
import glob
import getpass

print("="*60)
print("🪨 STRATICA v1.0.0 Upload - PyPI")
print("="*60)

# طلب التوكن من المستخدم يدوياً (آمن)
TOKEN = getpass.getpass("🔑 أدخل PyPI token: ")

# التحقق من وجود README.md
if not os.path.exists('README.md'):
    print("❌ README.md غير موجود!")
    exit(1)

# قراءة README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
print(f"📄 README.md: {len(readme)} حرف")

# البحث عن ملفات التوزيع
wheel_files = glob.glob("dist/*.whl")
tar_files = glob.glob("dist/*.tar.gz")

if not wheel_files and not tar_files:
    print("\n📦 لا توجد ملفات توزيع. جاري بناء الحزمة...")
    os.system("python -m build")
    
    wheel_files = glob.glob("dist/*.whl")
    tar_files = glob.glob("dist/*.tar.gz")

if not wheel_files and not tar_files:
    print("\n❌ فشل بناء الحزمة.")
    exit(1)

print(f"\n📦 الملفات:")
for f in wheel_files + tar_files:
    print(f"   • {os.path.basename(f)}")

for filepath in wheel_files + tar_files:
    filename = os.path.basename(filepath)
    print(f"\n📤 رفع: {filename}")

    # تحديد نوع الملف
    if filename.endswith('.tar.gz'):
        filetype = 'sdist'
        pyversion = 'source'
    else:
        filetype = 'bdist_wheel'
        pyversion = 'py3'

    # حساب الهاشات
    with open(filepath, 'rb') as f:
        content = f.read()
    md5_hash = hashlib.md5(content).hexdigest()
    sha256_hash = hashlib.sha256(content).hexdigest()

    # بيانات الرفع
    data = {
        ':action': 'file_upload',
        'metadata_version': '2.1',
        'name': 'stratica',
        'version': '1.0.0',
        'filetype': filetype,
        'pyversion': pyversion,
        'md5_digest': md5_hash,
        'sha256_digest': sha256_hash,
        'description': readme,
        'description_content_type': 'text/markdown',
        'author': 'Samir Baladi',
        'author_email': 'gitdeeper@gmail.com',
        'license': 'MIT',
        'summary': 'STRATICA: Stratigraphic Pattern Recognition & Paleoclimatic Temporal Reconstruction',
        'home_page': 'https://stratica.netlify.app',
        'project_urls': 'Documentation,https://stratica.readthedocs.io;Source,https://github.com/gitdeeper8/STRATICA;DOI,https://doi.org/10.5281/zenodo.18851076',
        'requires_python': '>=3.8',
        'keywords': 'stratigraphy, paleoclimatology, physics-informed neural networks, milankovitch cycles, deep-time, tci, sedimentary basins, isotope analysis, cyclostratigraphy'
    }

    # رفع الملف
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://upload.pypi.org/legacy/',
            files={'content': (filename, f, 'application/octet-stream')},
            data=data,
            auth=('__token__', TOKEN),
            timeout=60,
            headers={'User-Agent': 'STRATICA-Uploader/1.0'}
        )

    print(f"   الحالة: {response.status_code}")

    if response.status_code == 200:
        print("   ✅✅✅ تم الرفع بنجاح!")
    else:
        print(f"   ❌ خطأ: {response.text[:200]}")

print("\n" + "="*60)
print("🔗 https://pypi.org/project/stratica/")
print("="*60)
