# سازنده خودکار APK اپلیکیشن Parvaz

این مخزن یک پروژه سازنده است. با هر Push روی شاخه `main`، GitHub Actions آخرین سورس رسمی v2rayNG را از شاخه `master` دریافت می‌کند، تغییرات Parvaz را اعمال می‌کند، نسخه Release را با کلید شما امضا می‌کند و فایل‌های APK را در **Actions Artifacts** و **Releases** قرار می‌دهد.

## امکانات اعمال‌شده

- نام برنامه: `Parvaz`
- شناسه برنامه: `com.parvaz.vpn`
- تم تیره پیش‌فرض و پالت نارنجی، بنفش و صورتی
- آیکون اختصاصی بال پرنده و خطوط سرعت
- افزودن دو اشتراک پیش‌فرض با مسیرهای فعلی مخزن‌های منبع
- به‌روزرسانی اشتراک‌ها و اجرای Real Delay هنگام ورود برنامه
- انتخاب خودکار کم‌تأخیرترین کانفیگ موفق
- هنگام لمس Connect، انتظار برای پایان تست، انتخاب بهترین سرور و سپس اتصال
- ساخت و امضای APK با GitHub Actions

> هشدار امنیتی: سرورهای رایگان عمومی قابل اعتماد تضمین‌شده نیستند. برای اطلاعات حساس از اشتراک خصوصی و اپراتور معتبر استفاده کنید.

## ۱) آپلود در GitHub

1. در GitHub یک Repository خالی بسازید؛ برای مثال `Parvaz`.
2. تمام محتویات این پوشه را در ریشه Repository آپلود کنید؛ پوشه مخفی `.github` نیز باید آپلود شود.
3. شاخه اصلی Repository را `main` قرار دهید.

## ۲) ساخت keystore

روی کامپیوتری که Java JDK نصب است اجرا کنید:

```bash
keytool -genkeypair -v \
  -keystore parvaz.keystore \
  -alias parvaz \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

فایل `parvaz.keystore` را داخل Repository آپلود نکنید.

## ۳) تبدیل keystore به Base64

Linux:

```bash
base64 -w 0 parvaz.keystore > parvaz-base64.txt
```

macOS:

```bash
base64 parvaz.keystore | tr -d '\n' > parvaz-base64.txt
```

Windows PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("parvaz.keystore")) | Set-Content -NoNewline parvaz-base64.txt
```

## ۴) افزودن GitHub Secrets

در Repository بروید به:

`Settings → Secrets and variables → Actions → New repository secret`

چهار Secret زیر را بسازید:

| Secret | مقدار |
|---|---|
| `SIGNING_KEY` | تمام متن فایل `parvaz-base64.txt` |
| `KEY_ALIAS` | معمولاً `parvaz` |
| `KEY_STORE_PASSWORD` | رمز keystore |
| `KEY_PASSWORD` | رمز alias/key |

## ۵) اجرای ساخت APK

یکی از این دو روش را انجام دهید:

- یک فایل را Commit/Push کنید تا Workflow خودکار اجرا شود.
- از تب `Actions`، Workflow با نام **Build Parvaz APK** را باز کنید و `Run workflow` را بزنید.

پس از سبزشدن Build:

- پایین صفحه همان اجرای Actions، فایل Artifact با نام `Parvaz-APK-...` را دانلود کنید.
- یا از بخش `Releases`، آخرین نسخه با نام `Parvaz build ...` را باز کنید و APK مناسب دستگاه را بگیرید. معمولاً برای بیشتر گوشی‌های جدید، نسخه `arm64-v8a` مناسب است؛ نسخه `universal` حجم بیشتری دارد اما عمومی‌تر است.

## نکات مهم

- Keystore و رمزهایش را برای همیشه نگه دارید. نسخه‌های بعدی فقط با همان کلید روی نسخه قبلی نصب/به‌روزرسانی می‌شوند.
- اگر Workflow به دلیل تغییرات آینده سورس v2rayNG در مرحله `Apply Parvaz branding and features` متوقف شود، یعنی ساختار سورس بالادستی عوض شده و اسکریپت عمداً از تولید APK ناقص جلوگیری کرده است.
- خروجی بر پایه کد GPL-3.0 پروژه v2rayNG است؛ هنگام توزیع عمومی، الزامات مجوز و ارائه سورس تغییرات را رعایت کنید.
